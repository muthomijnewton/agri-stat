"""Phase 2 model training and transparent planning API."""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.security import get_current_admin, get_current_user
from app.db.database import get_db
from app.models.foundation import Location, SupplyRoute
from app.models.models import Product
from app.models.operations import SalesOrder, SalesOrderItem
from app.models.planning import DemandDay, ForecastRun
from app.api.endpoints.foundation import owned, queue
from app.services.planning_service import local_today, demand_history
from app.services.weather_service import TIMEZONE

router=APIRouter(prefix='/api/v1/planning',tags=['Phase 2 forecasts and planning'])


class ConfirmDay(BaseModel):
    location_id: UUID
    product_id: int = Field(gt=0)
    date: date
    quantity: Decimal | None = Field(default=None,ge=0,max_digits=16,decimal_places=4,allow_inf_nan=False)
    stockout: bool
    source: str = Field(min_length=3,max_length=200)
    use_sales_ledger: bool = True


class TrainRequest(BaseModel):
    location_id: UUID
    product_id: int = Field(gt=0)
    route_id: UUID


@router.post('/demand-days',status_code=201)
def confirm_day(data:ConfirmDay,db:Session=Depends(get_db),user=Depends(get_current_admin)):
    owned(db,Location,data.location_id,user);owned(db,Product,data.product_id,user)
    if data.date>=local_today(): raise HTTPException(422,'Only completed days can be confirmed')
    quantity=data.quantity
    if data.use_sales_ledger:
        start=datetime.combine(data.date,time.min,tzinfo=ZoneInfo(TIMEZONE)).astimezone(timezone.utc)
        quantity=db.query(func.coalesce(func.sum(SalesOrderItem.quantity),0)).join(SalesOrder,SalesOrder.id==SalesOrderItem.order_id).filter(
            SalesOrder.organization_id==user.organization_id,SalesOrder.location_id==str(data.location_id),
            SalesOrderItem.product_id==data.product_id,SalesOrder.sold_at>=start,SalesOrder.sold_at<start+timedelta(days=1)).scalar()
    elif quantity is None:
        raise HTTPException(422,'Historical records require an explicit daily quantity in the product base unit')
    row=DemandDay(organization_id=user.organization_id,location_id=str(data.location_id),product_id=data.product_id,
        date=data.date,quantity=quantity,stockout=data.stockout,source=('ledger: ' if data.use_sales_ledger else 'historical: ')+data.source[:188])
    db.add(row)
    try: db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'This day is already confirmed; historical records cannot silently overwrite it') from None
    return {'id':row.id,'date':row.date,'quantity':str(row.quantity),'stockout':row.stockout,'source':row.source}


@router.get('/demand-days')
def demand_days(location_id:UUID,product_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    owned(db,Location,location_id,user);owned(db,Product,product_id,user)
    rows=db.query(DemandDay).filter_by(organization_id=user.organization_id,location_id=str(location_id),product_id=product_id).order_by(DemandDay.date.desc()).limit(365).all()
    return [{'date':r.date,'quantity':str(r.quantity),'stockout':r.stockout,'source':r.source} for r in rows]


@router.post('/train',status_code=202)
def train(data:TrainRequest,db:Session=Depends(get_db),user=Depends(get_current_admin)):
    owned(db,Location,data.location_id,user);owned(db,Product,data.product_id,user)
    route=owned(db,SupplyRoute,data.route_id,user)
    if str(data.location_id) not in (route.origin_location_id,route.dest_location_id):
        raise HTTPException(422,'Select a route connected to this location')
    try: demand_history(db,user.organization_id,str(data.location_id),data.product_id)
    except ValueError as exc: raise HTTPException(422,str(exc)) from None
    row=ForecastRun(organization_id=user.organization_id,location_id=str(data.location_id),product_id=data.product_id,route_id=str(data.route_id),status='queued')
    db.add(row);db.commit()
    try: task=queue('planning.train',user,row.id)
    except HTTPException:
        row.status='queue_failed';row.result={'message':'Worker queue unavailable; submit a new training request'};db.commit();raise
    return {'run_id':row.id,**task}


def public_run(row):
    # Model artifacts and input snapshots stay in the database, not every browser response.
    return {'id':row.id,'location_id':row.location_id,'product_id':row.product_id,'route_id':row.route_id,
        'status':row.status,'updated_at':row.updated_at,
        'result':{k:v for k,v in row.result.items() if k not in ('artifact','input_snapshot')}}


@router.get('/runs')
def runs(location_id:UUID,db:Session=Depends(get_db),user=Depends(get_current_user)):
    owned(db,Location,location_id,user)
    return [public_run(r) for r in db.query(ForecastRun).filter_by(organization_id=user.organization_id,location_id=str(location_id)).order_by(ForecastRun.updated_at.desc()).limit(20)]


@router.get('/runs/{run_id}')
def get_run(run_id:UUID,db:Session=Depends(get_db),user=Depends(get_current_user)):
    return public_run(owned(db,ForecastRun,run_id,user))


@router.post('/runs/{run_id}/plan',status_code=202)
def plan(run_id:UUID,db:Session=Depends(get_db),user=Depends(get_current_admin)):
    row=owned(db,ForecastRun,run_id,user)
    if row.status!='validated': raise HTTPException(422,'A validated demand model is required')
    task=queue('planning.plan',user,row.id)
    return task
