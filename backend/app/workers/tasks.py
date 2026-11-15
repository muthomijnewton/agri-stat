import httpx
from app.db.database import SessionLocal
from app.models.foundation import InventoryBatch, Location, SupplyRoute
from app.services.inventory_service import batch_status
from app.services.routing_service import inspect_route
from app.services.weather_service import distinct_grid_locations, sync_location_weather
from app.workers.celery_app import celery_app

RETRY = dict(autoretry_for=(httpx.HTTPError,), retry_backoff=True, retry_jitter=True,
             retry_kwargs={"max_retries": 3})


@celery_app.task(name="foundation.sync_weather", **RETRY)
def sync_weather(organization_id, location_id):
    with SessionLocal.begin() as db:
        location = db.get(Location, location_id)
        if location is None or location.organization_id != organization_id:
            raise ValueError("Location not found in organization")
        return sync_location_weather(db, location)


@celery_app.task(name="foundation.refresh_weather")
def refresh_weather():
    with SessionLocal() as db:
        locations = [(row.organization_id, row.id) for row in distinct_grid_locations(db)]
    for organization_id, location_id in locations:
        sync_weather.delay(organization_id, location_id)
    return {"grids_queued": len(locations)}


@celery_app.task(name="foundation.inspect_route", **RETRY)
def profile_route(organization_id, route_id):
    with SessionLocal.begin() as db:
        route = db.get(SupplyRoute, route_id)
        if route is None or route.organization_id != organization_id:
            raise ValueError("Route not found in organization")
        return inspect_route(db, route)


@celery_app.task(name="foundation.refresh_batches")
def refresh_batches():
    with SessionLocal.begin() as db:
        rows = db.query(InventoryBatch).all()
        for batch in rows:
            batch.status = batch_status(batch)
        return {"batches": len(rows)}


@celery_app.task(name="foundation.refresh_markets", **RETRY)
def refresh_markets(organization_id=None):
    from app.models.foundation import DEFAULT_ORGANIZATION_ID
    from app.services.live_market_service import load_live_sources, prepare_live_sources
    sources = prepare_live_sources()
    with SessionLocal.begin() as db:
        return load_live_sources(db, sources, organization_id=organization_id or DEFAULT_ORGANIZATION_ID)


@celery_app.task(name='planning.train')
def train_demand(organization_id,run_id):
    from app.models.planning import ForecastRun
    from app.services.planning_service import train_run
    with SessionLocal() as db:
        run=db.get(ForecastRun,run_id)
        if not run or run.organization_id!=organization_id: raise ValueError('Run not found')
        if run.status!='queued': return {'run_id':run.id,'status':run.status}
        changed=db.query(ForecastRun).filter_by(id=run_id,organization_id=organization_id,status='queued').update({'status':'running'})
        db.commit()
        if changed!=1: return {'run_id':run_id,'status':'already_claimed'}
        try:
            train_run(db,run);db.commit()
        except Exception as exc:
            db.rollback();run=db.get(ForecastRun,run_id)
            run.status='blocked' if isinstance(exc,ValueError) else 'failed'
            run.result={'message':str(exc)[:400] if isinstance(exc,ValueError) else 'Training failed; inspect worker logs and submit a new run'}
            db.commit()
            import logging
            logging.getLogger(__name__).exception('Demand training failed for run %s',run_id)
        return {'run_id':run.id,'status':run.status,'message':run.result.get('message')}


@celery_app.task(name='planning.plan')
def plan_replenishment(organization_id,run_id):
    from app.models.planning import ForecastRun
    from app.services.planning_service import current_plan
    with SessionLocal.begin() as db:
        run=db.get(ForecastRun,run_id)
        if not run or run.organization_id!=organization_id: raise ValueError('Run not found')
        try: result=current_plan(db,run)
        except (ValueError,httpx.HTTPError) as exc:
            message=str(exc) if isinstance(exc,ValueError) else 'Live weather request failed; retry later'
            run.result={**run.result,'planning_status':'blocked','planning_message':message}
            return {'status':'blocked','message':message}
        run.result={**run.result,'latest_plan':result,'planning_status':'complete','planning_message':'Saved estimate; recalculate after stock changes'}
        return {'status':'complete','plan':result}
