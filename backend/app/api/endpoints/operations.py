"""Phase 2 farm operations: real stock, atomic FEFO sales, and data readiness."""
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, case, and_, or_
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.foundation import InventoryBatch, Location, utcnow
from app.models.models import Product
from app.models.operations import SalesOrder
from app.schemas.operations import SaleCreate
from app.services.farm_sales import record_sale, replay, sale_result, SaleError

router = APIRouter(prefix='/api/v1', tags=['Phase 2 farm operations'])


def location_owned(db, user, location_id):
    row = db.query(Location).filter_by(id=str(location_id), organization_id=user.organization_id).first()
    if not row:
        raise HTTPException(404, 'Location not found')
    return row


@router.post('/sales', status_code=201)
def create_sale(data: SaleCreate, response: Response, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        order, replayed = record_sale(db, user, data)
        db.commit()
    except SaleError as exc:
        db.rollback()
        raise HTTPException(exc.status, str(exc)) from None
    except IntegrityError:
        db.rollback()
        try:
            order = replay(db, user.organization_id, data)
        except SaleError as exc:
            raise HTTPException(exc.status, str(exc)) from None
        if not order:
            raise HTTPException(409, 'Sale could not be saved; check its product and location') from None
        replayed = True
    except OperationalError:
        db.rollback()
        raise HTTPException(503, 'Database is busy or unavailable. Retry with the same event ID') from None
    response.status_code = 200 if replayed else 201
    return sale_result(db, order, replayed=replayed)


@router.get('/sales')
def sales(location_id: UUID | None = None, limit: int = Query(20, ge=1, le=100),
          db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(SalesOrder).filter_by(organization_id=user.organization_id)
    if location_id:
        location_owned(db, user, location_id)
        query = query.filter_by(location_id=str(location_id))
    return [sale_result(db, row) for row in query.order_by(SalesOrder.sold_at.desc(), SalesOrder.id).limit(limit)]


@router.get('/stock')
def stock(location_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    location_owned(db, user, location_id)
    now = utcnow()
    usable = and_(InventoryBatch.received_at <= now,
        or_(InventoryBatch.expires_at.is_(None), InventoryBatch.expires_at > now), Product.is_active.is_(True))
    expired = and_(InventoryBatch.expires_at.is_not(None), InventoryBatch.expires_at <= now)
    rows = db.query(Product.id, Product.name, Product.unit,
        func.sum(case((usable, InventoryBatch.quantity_on_hand), else_=0)),
        func.sum(case((expired, InventoryBatch.quantity_on_hand), else_=0)),
        func.sum(case((and_(usable, InventoryBatch.expires_at.is_(None)), InventoryBatch.quantity_on_hand), else_=0)),
    ).join(InventoryBatch, InventoryBatch.product_id == Product.id).filter(
        InventoryBatch.organization_id == user.organization_id, Product.organization_id == user.organization_id,
        InventoryBatch.location_id == str(location_id), InventoryBatch.is_synthetic.is_(False),
    ).group_by(Product.id, Product.name, Product.unit).order_by(Product.name, Product.id).all()
    return {'location_id': str(location_id), 'as_of': now, 'items': [
        {'product_id': pid, 'name': name, 'unit': unit, 'available': str(available or Decimal(0)),
         'expired': str(expired_qty or Decimal(0)), 'unknown_expiry': str(unknown or Decimal(0))}
        for pid, name, unit, available, expired_qty, unknown in rows]}


@router.get('/forecast-readiness')
def readiness(location_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    location_owned(db, user, location_id)
    count, earliest, latest = db.query(func.count(SalesOrder.id), func.min(SalesOrder.sold_at), func.max(SalesOrder.sold_at)).filter(
        SalesOrder.organization_id == user.organization_id, SalesOrder.location_id == str(location_id)).one()
    from app.models.planning import ForecastRun
    from app.services.planning_service import local_today
    runs = db.query(ForecastRun).filter_by(organization_id=user.organization_id, location_id=str(location_id), status='validated').all()
    ready = any(r.result.get('forecasts') and r.result['forecasts'][0]['date'] == str(local_today()) for r in runs)
    return {'sales_recorded': count, 'first_sale_at': earliest, 'last_sale_at': latest,
        'status': 'no_sales_history' if not count else 'collecting_sales_history',
        'demand_model_ready': ready,
        'explanation': 'Public market quotes are not farm sales. Confirm complete daily totals on Demand planning, then train and validate a model. Market prices never substitute for your own sales history.'}
