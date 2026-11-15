"""Versioned Phase 1 API. Organization identity always comes from authentication."""
import os
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_admin, get_current_user
from app.db.database import get_db
from app.models.models import Product
from app.models.foundation import ImportRun, InventoryBatch, Location, MarketObservation, SupplyRoute, WeatherObservation
from app.schemas.foundation import (BatchCreate, BatchRead, LocationCreate, LocationRead,
    ProductCreate, ProductRead, RouteCreate, RouteRead, WeatherRead)
from app.services.inventory_service import batch_status
from app.services.weather_service import weather_grid

router = APIRouter(prefix="/api/v1", tags=["Phase 1 foundation"])


def scoped(db, model, user):
    return db.query(model).filter(model.organization_id == user.organization_id)


def owned(db, model, record_id, user):
    row = scoped(db, model, user).filter(model.id == str(record_id) if isinstance(record_id, UUID) else model.id == record_id).first()
    if row is None:
        raise HTTPException(404, "Record not found")
    return row


def save(db, row):
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Conflicting SKU, batch code, or invalid related record") from None
    db.refresh(row)
    return row


def queue(task_name, user, record_id=None):
    if not os.getenv("REDIS_URL"):
        raise HTTPException(503, "Background workers are not configured. Set REDIS_URL and start a Celery worker.")
    from app.workers.celery_app import celery_app
    from redis import Redis
    try:
        identifier = str(uuid4())
        cache = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=2, socket_connect_timeout=2)
        cache.setex(f"agristat:phase1:job-owner:{identifier}", 86400, user.organization_id)
        args = [user.organization_id] + ([str(record_id)] if record_id is not None else [])
        task = celery_app.send_task(task_name, args=args, task_id=identifier, retry=False)
    except Exception:
        raise HTTPException(503, "Background queue is unavailable") from None
    return {"task_id": task.id, "status": "queued"}


@router.get("/jobs/{task_id}")
def job_status(task_id: UUID, user=Depends(get_current_user)):
    if not os.getenv("REDIS_URL"):
        raise HTTPException(503, "Background workers are not configured")
    from redis import Redis
    from app.workers.celery_app import celery_app
    try:
        cache = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=2, socket_connect_timeout=2)
        owner = cache.get(f"agristat:phase1:job-owner:{task_id}")
        if owner is None or owner.decode() != user.organization_id:
            raise HTTPException(404, "Job not found")
        result = celery_app.AsyncResult(str(task_id))
        state = result.state
        return {"status": state, "result": result.result if state == "SUCCESS" else None,
                "message": "Source refresh failed; existing records were kept. Check worker logs." if state == "FAILURE" else None}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Background queue is unavailable") from None


@router.post("/market-prices/refresh", status_code=202)
def refresh_market_prices(user=Depends(get_current_admin)):
    return queue("foundation.refresh_markets", user)


@router.get("/locations", response_model=list[LocationRead])
def locations(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return scoped(db, Location, user).order_by(Location.name, Location.id).offset(skip).limit(limit).all()


@router.post("/locations", response_model=LocationRead, status_code=201)
def create_location(data: LocationCreate, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    return save(db, Location(**data.model_dump(), organization_id=user.organization_id,
                             weather_grid_key=weather_grid(data.latitude, data.longitude)[0] if data.latitude is not None else None))


@router.get("/locations/{location_id}", response_model=LocationRead)
def location(location_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return owned(db, Location, location_id, user)


@router.get("/products", response_model=list[ProductRead])
def products(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return scoped(db, Product, user).filter(Product.is_active.is_(True)).order_by(Product.id).offset(skip).limit(limit).all()


@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    return save(db, Product(**data.model_dump(), organization_id=user.organization_id))


@router.get("/supply-routes", response_model=list[RouteRead])
def routes(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return scoped(db, SupplyRoute, user).order_by(SupplyRoute.id).offset(skip).limit(limit).all()


@router.post("/supply-routes", response_model=RouteRead, status_code=201)
def create_route(data: RouteCreate, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    for identifier in (data.origin_location_id, data.dest_location_id):
        if owned(db, Location, identifier, user).latitude is None:
            raise HTTPException(422, "Route endpoints need verified coordinates")
    return save(db, SupplyRoute(**data.model_dump(mode="json"), organization_id=user.organization_id))


@router.post("/supply-routes/{route_id}/inspect", status_code=202)
def inspect(route_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    owned(db, SupplyRoute, route_id, user)
    return queue("foundation.inspect_route", user, route_id)


@router.get("/inventory-batches", response_model=list[BatchRead])
def batches(location_id: UUID | None = None, include_synthetic: bool = False,
            skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
            db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = scoped(db, InventoryBatch, user)
    if location_id:
        owned(db, Location, location_id, user)
        query = query.filter(InventoryBatch.location_id == str(location_id))
    if not include_synthetic:
        query = query.filter(InventoryBatch.is_synthetic.is_(False))
    result = []
    for batch in query.order_by(InventoryBatch.received_at, InventoryBatch.id).offset(skip).limit(limit):
        response = BatchRead.model_validate(batch)
        response.status = batch_status(batch)
        result.append(response)
    return result


@router.post("/inventory-batches", response_model=BatchRead, status_code=201)
def create_batch(data: BatchCreate, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    owned(db, Location, data.location_id, user)
    product = owned(db, Product, data.product_id, user)
    if not product.is_active:
        raise HTTPException(422, "Product is inactive")
    if product.shelf_life_days and data.expires_at is None:
        raise HTTPException(422, "Perishable batches require an expiry timestamp")
    values = data.model_dump()
    values["location_id"] = str(data.location_id)
    batch = InventoryBatch(**values, organization_id=user.organization_id)
    batch.status = batch_status(batch)
    return save(db, batch)


@router.post("/locations/{location_id}/sync-weather", status_code=202)
def sync_weather(location_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_admin)):
    if owned(db, Location, location_id, user).latitude is None:
        raise HTTPException(422, "This market has no verified coordinates")
    return queue("foundation.sync_weather", user, location_id)


@router.get("/locations/{location_id}/weather", response_model=list[WeatherRead])
def weather(location_id: UUID, limit: int = Query(60, ge=1, le=365), db: Session = Depends(get_db), user=Depends(get_current_user)):
    location = owned(db, Location, location_id, user)
    return scoped(db, WeatherObservation, user).filter_by(weather_grid_key=location.weather_grid_key).order_by(
        WeatherObservation.date.desc(), WeatherObservation.is_forecast).limit(limit).all()


@router.get("/market-observations")
def markets(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return scoped(db, MarketObservation, user).filter_by(source="kamis").order_by(MarketObservation.date.desc(), MarketObservation.id).offset(skip).limit(limit).all()


@router.get("/market-summary")
def market_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    summaries = db.query(MarketObservation.source, func.count(MarketObservation.id),
                         func.max(MarketObservation.date)).filter_by(organization_id=user.organization_id, source="kamis").group_by(MarketObservation.source).all()
    result = []
    for source, count, latest in summaries:
        run = scoped(db, ImportRun, user).filter_by(source=source).order_by(ImportRun.imported_at.desc()).first()
        result.append({"source": source, "observations": count, "latest_date": latest,
                       "last_refreshed": run.imported_at if run else None, "source_url": run.source_url if run else None})
    return {"sources": result, "markets": scoped(db, MarketObservation, user).filter_by(source="kamis").with_entities(MarketObservation.location_id).distinct().count()}


@router.get("/market-prices")
def market_prices(q: str = Query("", max_length=100), source: str | None = None,
                  location: str = Query("", max_length=100), product: str = Query("", max_length=100),
                  skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=500),
                  db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(MarketObservation, Location.name, Product.name, ImportRun.source_url, ImportRun.imported_at).join(
        Location, Location.id == MarketObservation.location_id).join(
        Product, Product.id == MarketObservation.product_id).join(
        ImportRun, ImportRun.id == MarketObservation.import_run_id).filter(MarketObservation.organization_id == user.organization_id, MarketObservation.source == "kamis")
    def literal(value):
        return value.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    for column, value in ((Location.name, location), (Product.name, product)):
        if value.strip():
            query = query.filter(column.ilike(f"%{literal(value)}%", escape="\\"))
    if q.strip():
        term = literal(q)
        query = query.filter(Product.name.ilike(f"%{term}%", escape="\\") | Location.name.ilike(f"%{term}%", escape="\\"))
    if source:
        query = query.filter(MarketObservation.source == source)
    total = query.count()
    items = []
    for row, market, product, url, refreshed in query.order_by(MarketObservation.date.desc(), Product.name, Location.name, MarketObservation.id).offset(skip).limit(limit):
        items.append({"id": row.id, "product": product, "market": market, "date": row.date,
                      "price": row.price, "price_type": row.price_type, "currency": row.currency,
                      "unit": row.base_unit, "volume": row.volume, "frequency": row.frequency,
                      "source": row.source, "source_url": url, "last_refreshed": refreshed})
    return {"total": total, "items": items}
