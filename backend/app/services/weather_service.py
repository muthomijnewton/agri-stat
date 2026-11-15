"""Open-Meteo forecast and delayed historical reanalysis ingestion."""
import math
import os
from datetime import date, datetime, timedelta
from statistics import mean
from zoneinfo import ZoneInfo

from app.models.foundation import Location, WeatherObservation, utcnow
from app.services.external_data import fetch_json

TIMEZONE = os.getenv("APP_TIMEZONE", "Africa/Nairobi")
LAT_STEP = 5000 / 111195.0
DAILY = "rain_sum,temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration"


def weather_grid(latitude, longitude):
    """Approximately 5 km cells, latitude-corrected east/west width.

    Cache grouping only: this does not improve the source model's resolution.
    The center is deterministic so every location sharing a key gets identical data.
    """
    lat, lon = float(latitude), float(longitude)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid coordinates")
    band = min(int((lat + 90) / LAT_STEP), math.ceil(180 / LAT_STEP) - 1)
    center_lat = min(89.999999, -90 + (band + 0.5) * LAT_STEP)
    columns = max(1, round(360 * 111195 * math.cos(math.radians(center_lat)) / 5000))
    column = min(int((lon + 180) / 360 * columns), columns - 1)
    center_lon = -180 + (column + 0.5) * 360 / columns
    return f"5km-v1:{band}:{column}", center_lat, center_lon


def daily_rows(payload, *, forecast):
    daily = payload.get("daily", {})
    hourly = payload.get("hourly", {})
    moisture = {}
    times = hourly.get("time", [])
    soil = hourly.get("soil_moisture_0_to_7cm", [])
    if forecast:
        # Forecast layers differ from ERA5-Land: estimate 0–7 cm by depth weighting.
        # Assumes uniform moisture within the provider's 3–9 cm layer.
        soil = []
        for i in range(len(times)):
            layers = [hourly.get(key, []) for key in ("soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm")]
            values = [layer[i] if i < len(layer) else None for layer in layers]
            soil.append((values[0] + 2 * values[1] + 4 * values[2]) / 7 if all(v is not None for v in values) else None)
    for timestamp, value in zip(times, soil):
        if value is not None and math.isfinite(value):
            moisture.setdefault(timestamp[:10], []).append(value)
    for i, day in enumerate(daily.get("time", [])):
        values = {}
        for column, source in (("rainfall_mm", "rain_sum"), ("temp_max_c", "temperature_2m_max"),
                               ("temp_min_c", "temperature_2m_min"),
                               ("evapotranspiration_mm", "et0_fao_evapotranspiration")):
            series = daily.get(source, [])
            value = series[i] if i < len(series) else None
            values[column] = value if value is not None and math.isfinite(value) else None
        # Never promote a forecast into an actual when archive data is missing.
        if not forecast and any(values[k] is None for k in ("rainfall_mm", "temp_max_c", "temp_min_c")):
            continue
        yield dict(date=date.fromisoformat(day), is_forecast=forecast, **values,
                   soil_moisture_0_to_7cm=mean(moisture[day]) if moisture.get(day) else None,
                   source="open-meteo-forecast-soil-depth-estimate" if forecast else "open-meteo-era5-seamless-reanalysis")


def sync_location_weather(db, location, *, fetch=fetch_json, today=None):
    if location.latitude is None or location.longitude is None:
        raise ValueError("This market has no verified coordinates; weather sync is unavailable")
    today = today or datetime.now(ZoneInfo(TIMEZONE)).date()
    key, lat, lon = weather_grid(location.latitude, location.longitude)
    location.weather_grid_key = key
    common = dict(latitude=lat, longitude=lon, timezone=TIMEZONE, daily=DAILY)
    forecast = fetch(os.getenv("WEATHER_FORECAST_URL", "https://api.open-meteo.com/v1/forecast"),
                     params={**common, "forecast_days": 14,
                             "hourly": "soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm"})
    # ERA5-Land is delayed. Refresh overlapping days to pick up revisions.
    archive = fetch(os.getenv("WEATHER_ARCHIVE_URL", "https://archive-api.open-meteo.com/v1/archive"),
                    params={**common, "models": "era5_seamless", "hourly": "soil_moisture_0_to_7cm", "start_date": str(today - timedelta(days=21)),
                            "end_date": str(today - timedelta(days=5))})
    count = 0
    for payload, is_forecast in ((forecast, True), (archive, False)):
        for values in daily_rows(payload, forecast=is_forecast):
            if db.bind.dialect.name == "postgresql":
                from sqlalchemy.dialects.postgresql import insert
            else:
                from sqlalchemy.dialects.sqlite import insert
            fields = dict(organization_id=location.organization_id, weather_grid_key=key,
                          **values, fetched_at=utcnow(), updated_at=utcnow())
            primary = ["organization_id", "weather_grid_key", "date", "is_forecast"]
            statement = insert(WeatherObservation).values(**fields)
            db.execute(statement.on_conflict_do_update(index_elements=primary,
                set_={field: value for field, value in fields.items() if field not in primary}))
            count += 1
    db.flush()
    return {"grid": key, "rows": count}


def distinct_grid_locations(db):
    seen = set()
    for location in db.query(Location).filter(Location.weather_grid_key.isnot(None)).order_by(Location.id):
        key = (location.organization_id, location.weather_grid_key)
        if key not in seen:
            seen.add(key)
            yield location
