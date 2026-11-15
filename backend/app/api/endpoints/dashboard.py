"""Tenant-scoped dashboard projections and checked historical-demand CSV import."""
import csv
import hashlib
import io
from datetime import date, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import get_current_admin, get_current_user
from app.db.database import get_db
from app.models.foundation import Location, InventoryBatch, SupplyRoute, WeatherObservation, utcnow
from app.models.models import Product
from app.models.operations import SalesOrder
from app.models.planning import DemandDay, ForecastRun
from app.api.endpoints.foundation import owned
from app.api.endpoints.planning import ConfirmDay, public_run
from app.services.inventory_service import batch_status
from app.services.planning_service import local_today

router = APIRouter(prefix='/api/v1', tags=['Phase 3 dashboard'])


@router.get('/dashboard')
def overview(location_id: UUID | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    org = user.organization_id
    now, today = utcnow(), local_today()
    locations = db.query(Location).filter_by(organization_id=org).order_by(Location.name).all()
    if location_id:
        owned(db, Location, location_id, user)
    batches = db.query(InventoryBatch, Product).join(Product, Product.id == InventoryBatch.product_id).filter(
        InventoryBatch.organization_id == org, Product.organization_id == org,
        InventoryBatch.is_synthetic.is_(False), InventoryBatch.quantity_on_hand > 0)
    sales = db.query(SalesOrder).filter_by(organization_id=org)
    runs = db.query(ForecastRun).filter_by(organization_id=org)
    if location_id:
        batches = batches.filter(InventoryBatch.location_id == str(location_id))
        sales = sales.filter(SalesOrder.location_id == str(location_id))
        runs = runs.filter(ForecastRun.location_id == str(location_id))
    location_names = {row.id: row.name for row in locations}
    totals, lots, counts = {}, [], {'expired': 0, 'expiring_soon': 0, 'unknown_expiry': 0}
    for batch, product in batches.all():
        received = batch.received_at.replace(tzinfo=timezone.utc) if batch.received_at.tzinfo is None else batch.received_at
        state = batch_status(batch, now)
        if received > now: state = 'NOT_RECEIVED'
        elif not product.is_active: state = 'INACTIVE_PRODUCT'
        if state == 'EXPIRED': counts['expired'] += 1
        elif state == 'EXPIRING_SOON': counts['expiring_soon'] += 1
        if state in ('ACTIVE', 'EXPIRING_SOON'):
            totals[product.unit] = totals.get(product.unit, Decimal(0)) + batch.quantity_on_hand
            if batch.expires_at is None: counts['unknown_expiry'] += 1
        lots.append({'id': batch.id, 'batch_code': batch.batch_code, 'product': product.name,
            'product_id': product.id, 'unit': product.unit, 'quantity': str(batch.quantity_on_hand),
            'location': location_names.get(batch.location_id), 'expires_at': batch.expires_at, 'status': state})
    lots.sort(key=lambda b: (b['expires_at'] is None, str(b['expires_at'] or ''), b['batch_code']))
    routes = db.query(SupplyRoute).filter_by(organization_id=org)
    if location_id:
        routes = routes.filter((SupplyRoute.origin_location_id == str(location_id)) | (SupplyRoute.dest_location_id == str(location_id)))
    recent_runs = runs.order_by(ForecastRun.updated_at.desc()).limit(50).all()
    products = {p.id: p for p in db.query(Product).filter_by(organization_id=org).all()}
    def run_view(run):
        value = public_run(run)
        product = products.get(run.product_id)
        value['product_name'] = product.name if product else 'Unknown product'
        value['unit'] = product.unit if product else None
        return value
    return {'as_of': now, 'location_id': str(location_id) if location_id else None,
        'farm_count': sum(l.location_type == 'FARM' for l in locations),
        'sales_count': sales.count(), 'sales_value_kes': str(sales.with_entities(func.coalesce(func.sum(SalesOrder.total_amount),0)).scalar()),
        'available_by_unit': {k: str(v) for k,v in totals.items()}, 'batch_counts': counts,
        'batches': lots[:100], 'batch_total': len(lots), 'route_count': routes.count(),
        'high_risk_routes': routes.filter(SupplyRoute.current_risk_level == 'HIGH').count(),
        'runs': [run_view(r) for r in recent_runs], 'today': today,
        'notes': 'Sales totals use the farm ledger only. Stock quantities are kept separate by unit. Saved road risk must be reviewed with its inspection and planning dates.'}


@router.get('/map-data')
def map_data(db: Session = Depends(get_db), user=Depends(get_current_user)):
    org, today = user.organization_id, local_today()
    locations = db.query(Location).filter_by(organization_id=org).order_by(Location.name).all()
    rows = db.query(WeatherObservation).filter(WeatherObservation.organization_id==org,
        WeatherObservation.is_forecast.is_(True), WeatherObservation.date>=today,
        WeatherObservation.date<today+timedelta(days=3)).all()
    grids = {}
    for row in rows: grids.setdefault(row.weather_grid_key, []).append(row)
    def weather(location):
        values=grids.get(location.weather_grid_key, [])
        # A missing day/reading is unknown, not zero rainfall.
        fresh=lambda v: utcnow()-(v.fetched_at.replace(tzinfo=timezone.utc) if v.fetched_at.tzinfo is None else v.fetched_at)<=timedelta(hours=36)
        complete=len(values)==3 and all(v.rainfall_mm is not None and fresh(v) for v in values)
        soil=[v for v in values if v.soil_moisture_0_to_7cm is not None and fresh(v)]
        return {'rain_3d_mm':sum(float(v.rainfall_mm) for v in values) if complete else None,
            'soil_moisture':float(sorted(soil,key=lambda v:v.date)[0].soil_moisture_0_to_7cm) if soil else None,
            'fetched_at':max((v.fetched_at for v in values),default=None), 'is_forecast':True}
    routes=db.query(SupplyRoute).filter_by(organization_id=org).all()
    return {'as_of':utcnow(),'locations':[{'id':l.id,'name':l.name,'type':l.location_type,
        'latitude':l.latitude,'longitude':l.longitude,'weather_grid_key':l.weather_grid_key,**weather(l)} for l in locations],
        'routes':[{'id':r.id,'name':r.name,'origin_location_id':r.origin_location_id,'dest_location_id':r.dest_location_id,
        'geometry':r.route_geometry,'risk':r.current_risk_level,'inspected_at':r.inspected_at,
        'distance_km':r.total_distance_km,'unpaved_ratio':r.unpaved_ratio,'unknown_surface_ratio':r.unknown_surface_ratio,
        'base_lead_time_days':r.base_lead_time_days,'adjusted_lead_time_days':r.adjusted_lead_time_days} for r in routes]}


@router.post('/admin/import-csv')
async def import_demand_csv(file: UploadFile = File(...), location_id: UUID = Form(...),
        product_id: int = Form(...), commit: bool = Form(False), preview_hash: str | None = Form(None),
        db: Session = Depends(get_db), user=Depends(get_current_admin)):
    owned(db,Location,location_id,user);product=owned(db,Product,product_id,user)
    data=await file.read(1024*1024+1)
    if len(data)>1024*1024: raise HTTPException(413,'CSV exceeds the 1 MB limit')
    digest=hashlib.sha256(str(location_id).encode()+b'\0'+str(product_id).encode()+b'\0'+data).hexdigest()
    if commit and digest!=preview_hash: raise HTTPException(409,'File or selection changed. Preview it again before importing')
    try:
        reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig')),strict=True)
        expected={'date','quantity','stockout','source'}
        if reader.fieldnames is None or set(reader.fieldnames)!=expected or len(reader.fieldnames)!=4:
            raise HTTPException(422,'CSV must have exactly these headers: date,quantity,stockout,source')
        existing={d for (d,) in db.query(DemandDay.date).filter_by(organization_id=user.organization_id,
            location_id=str(location_id),product_id=product_id).all()}
        errors, records, seen = [], [], set()
        for line,row in enumerate(reader,start=2):
            if line>5001: raise HTTPException(413,'CSV exceeds 5,000 rows')
            try:
                if None in row or any(v is None for v in row.values()): raise ValueError('Row must have exactly four columns')
                flag=row['stockout'].strip().lower()
                if flag not in ('true','false'): raise ValueError('stockout must be true or false')
                record=ConfirmDay(location_id=location_id,product_id=product_id,date=row['date'].strip(),
                    quantity=row['quantity'].strip(),stockout=flag=='true',source=row['source'].strip(),use_sales_ledger=False)
                if record.date>=local_today(): raise ValueError('Only completed days can be imported')
                if record.date in seen: raise ValueError('Duplicate date within this file')
                if record.date in existing: raise ValueError('Date already exists; existing records will not be overwritten')
                seen.add(record.date);records.append(record)
            except (ValueError,ValidationError) as exc:
                errors.append({'line':line,'message':str(exc)[:240]})
        if not records and not errors: raise HTTPException(422,'CSV contains no data rows')
    except (UnicodeDecodeError,csv.Error): raise HTTPException(422,'Use a valid UTF-8 CSV file') from None
    if errors:
        return {'status':'invalid','errors':errors[:100],'error_count':len(errors),'valid_rows':len(records),'imported_rows':0}
    result={'status':'preview','preview_hash':digest,'row_count':len(records),'unit':product.unit,
        'first_date':min(r.date for r in records),'last_date':max(r.date for r in records),
        'total_quantity':str(sum((r.quantity for r in records),Decimal(0))),
        'stockout_days':sum(r.stockout for r in records),'imported_rows':0,
        'sample':[{'date':r.date,'quantity':str(r.quantity),'stockout':r.stockout,'source':r.source} for r in records[:10]]}
    if commit:
        db.add_all([DemandDay(organization_id=user.organization_id,location_id=str(location_id),product_id=product_id,
            date=r.date,quantity=r.quantity,stockout=r.stockout,source='historical: '+r.source[:188]) for r in records])
        try: db.commit()
        except IntegrityError:
            db.rollback();raise HTTPException(409,'Records changed after preview; nothing was imported. Preview again') from None
        result.update(status='imported',imported_rows=len(records))
    return result
