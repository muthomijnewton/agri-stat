"""Load confirmed farm records and live weather without manufacturing demand."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import pandas as pd
from sqlalchemy import and_, or_
from app.models.foundation import InventoryBatch, Location, SupplyRoute, utcnow
from app.models.models import Product
from app.models.planning import DemandDay, ForecastRun
from app.services.demand_model import train_validate, MIN_DAYS
from app.services.external_data import fetch_json
from app.services.weather_service import daily_rows, weather_grid, DAILY, TIMEZONE
from app.services.reorder_engine import calculate_plan


def local_today():
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def route_points(db, route):
    origin = db.get(Location, route.origin_location_id)
    geometry = route.route_geometry or {}
    coordinates = geometry.get('coordinates', [])
    if not coordinates or origin.latitude is None or origin.longitude is None:
        raise ValueError('Inspect this route first to obtain its road geometry')
    # Midpoint by cumulative geometric distance, not by vertex count.
    import math
    lengths = [math.hypot((b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2)), b[1]-a[1]) for a,b in zip(coordinates,coordinates[1:])]
    halfway = sum(lengths)/2; traveled = 0
    midpoint = coordinates[0]
    for a,b,length in zip(coordinates,coordinates[1:],lengths):
        if traveled+length >= halfway:
            fraction=(halfway-traveled)/length if length else 0
            midpoint=[a[0]+fraction*(b[0]-a[0]),a[1]+fraction*(b[1]-a[1])]; break
        traveled += length
    return [(float(origin.latitude),float(origin.longitude)),(midpoint[1],midpoint[0])]


def archive_weather(db, location, route, start, end, fetch=fetch_json):
    cache = {}
    def series(lat,lon):
        key,lat,lon = weather_grid(lat,lon)
        if key not in cache:
            payload=fetch('https://archive-api.open-meteo.com/v1/archive',params={
                'latitude':lat,'longitude':lon,'timezone':TIMEZONE,'models':'era5_seamless','daily':DAILY,
                'hourly':'soil_moisture_0_to_7cm','start_date':str(start),'end_date':str(end)})
            rows=list(daily_rows(payload,forecast=False))
            if not rows: raise ValueError('Weather archive returned no usable records')
            cache[key]=pd.DataFrame(rows).set_index('date')
            cache[key].index=pd.to_datetime(cache[key].index)
        return cache[key]
    farm=series(location.latitude,location.longitude)
    points=route_points(db,route)
    road=[series(*point).rainfall_mm for point in points]
    # Use wetter of origin and midpoint; both are required (skipna=False).
    result=pd.DataFrame({'rainfall_mm':farm.rainfall_mm,'soil_moisture':farm.soil_moisture_0_to_7cm,
        'route_rainfall_mm':pd.concat(road,axis=1).max(axis=1,skipna=False)})
    return result.astype(float)


def demand_history(db, org, location_id, product_id):
    rows=db.query(DemandDay).filter_by(organization_id=org,location_id=location_id,product_id=product_id).order_by(DemandDay.date).all()
    if len(rows)<MIN_DAYS:
        raise ValueError('Need at least 120 consecutive confirmed daily totals, including explicit zero-sale days')
    if rows[-1].date != local_today()-timedelta(days=1):
        raise ValueError('Confirm daily totals through yesterday before training a current forecast')
    # Use a bounded recent history. A stockout is censored demand, not a trustworthy zero.
    rows=rows[-365:]
    if any(row.stockout for row in rows):
        raise ValueError('History contains stockouts. Sales on those days understate demand; resolve a suitable uncensored training period first')
    return pd.Series([float(row.quantity) for row in rows],index=pd.DatetimeIndex([row.date for row in rows]),name='quantity')


def train_run(db, run):
    location=db.get(Location,run.location_id);route=db.get(SupplyRoute,run.route_id)
    if location.organization_id != run.organization_id or route.organization_id != run.organization_id:
        raise ValueError('Run references records outside the organization')
    history=demand_history(db,run.organization_id,run.location_id,run.product_id)
    weather=archive_weather(db,location,route,history.index[0].date(),history.index[-1].date()-timedelta(days=7))
    result=train_validate(history,weather)
    result['weather_source']='Open-Meteo ERA5-Seamless reanalysis; soil moisture is modelled, not a farm sensor'
    run.result=result;run.status=result['status'];db.flush()
    return result


def current_plan(db,run,fetch=fetch_json):
    result=run.result
    today=local_today()
    forecasts=[row for row in result.get('forecasts',[]) if row['date'] >= str(today)]
    if run.status!='validated' or len(forecasts)<14 or forecasts[0]['date']!=str(today):
        raise ValueError('Train a validated forecast through yesterday before requesting today’s plan')
    route=db.get(SupplyRoute,run.route_id);product=db.get(Product,run.product_id)
    if route.dest_location_id != run.location_id:
        raise ValueError('Purchased-stock planning requires an incoming route with this farm as the destination. Use an outbound route forecast for sales and dispatch only')
    if not product.is_active:
        raise ValueError('This product is inactive')
    if route.unpaved_ratio is None or route.unknown_surface_ratio is None or not route.inspected_at:
        raise ValueError('Road surface inspection is required')
    inspected=route.inspected_at.replace(tzinfo=timezone.utc) if route.inspected_at.tzinfo is None else route.inspected_at
    if utcnow()-inspected>timedelta(days=30):
        raise ValueError('Road inspection is older than 30 days; refresh it before planning')
    rain=[];temperatures=[]
    for lat,lon in route_points(db,route):
        payload=fetch('https://api.open-meteo.com/v1/forecast',params={'latitude':lat,'longitude':lon,
            'timezone':TIMEZONE,'forecast_days':14,'daily':'rain_sum,temperature_2m_max'},cache_seconds=0)
        daily=payload.get('daily',{}); dates=daily.get('time',[])
        expected=[str(today+timedelta(days=i)) for i in range(14)]
        if dates!=expected: raise ValueError('Fresh 14-day route weather is unavailable')
        rainfall=daily.get('rain_sum',[]); heat=daily.get('temperature_2m_max',[])
        import math
        if len(rainfall)!=14 or len(heat)!=14 or any(v is None or not math.isfinite(v) for v in rainfall+heat):
            raise ValueError('Route weather is incomplete')
        rain.append(sum(rainfall[:3]));temperatures.append(heat)
    now=utcnow()
    batches=db.query(InventoryBatch).filter(InventoryBatch.organization_id==run.organization_id,
        InventoryBatch.location_id==run.location_id,InventoryBatch.product_id==run.product_id,
        InventoryBatch.is_synthetic.is_(False),InventoryBatch.received_at<=now,
        or_(InventoryBatch.expires_at.is_(None),InventoryBatch.expires_at>now)).all()
    net_stock=sum(float(b.quantity_on_hand) for b in batches)
    args=dict(base_lead_days=float(route.base_lead_time_days),unpaved_ratio=float(route.unpaved_ratio),
        unknown_ratio=float(route.unknown_surface_ratio),rain_3d_mm=max(rain),
        daily_demand=sum(row['p50'] for row in forecasts)/len(forecasts),demand_std=result['demand_std'],net_stock=net_stock,
        shelf_life_days=product.shelf_life_days,optimal_temp_max_c=float(product.optimal_temp_max_c) if product.optimal_temp_max_c is not None else None)
    preliminary=calculate_plan(**args)
    lead=preliminary['adjusted_lead_time_days']
    if lead+7>14: raise ValueError('Lead time plus the 7-day review period exceeds the available 14-day forecast; no recommendation issued')
    import math
    transit_days=max(1,math.ceil(lead))
    args['temp_max_c']=max(max(values[:transit_days]) for values in temperatures)
    plan=calculate_plan(**args)
    plan.update(run_id=run.id,as_of=now.isoformat(),unit=product.unit,available_stock=net_stock,
        forecast_source=result['selected_model'],route_weather_fetched_at=now.isoformat(),
        purpose='Purchased replenishment or aggregation only; this does not recommend planting or predict harvest yield')
    plan['reasons'].append('Stock is usable now; batch expiry before future demand and unrecorded incoming orders still require review')
    route.adjusted_lead_time_days=plan['adjusted_lead_time_days'];route.current_risk_level=plan['risk_level']
    return plan
