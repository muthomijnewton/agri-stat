"""Strict, repeatable public-market ETL with source provenance and no fake sales."""
import csv
import hashlib
import io
import json
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from app.models.models import Product
from app.models.foundation import ImportRun, InventoryBatch, Location, MarketObservation, Organization
from app.services.weather_service import weather_grid

MAX_BYTES = 20 * 1024 * 1024


def number(value, label, *, optional=False):
    if optional and (value is None or str(value).strip() == ""):
        return None
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except InvalidOperation:
        raise ValueError(f"Invalid {label}: {value!r}") from None
    if not result.is_finite():
        raise ValueError(f"Non-finite {label}")
    return result


def unit_factor(value, custom_kg=None):
    unit = re.sub(r"\s+", " ", value.strip().lower())
    if custom_kg and unit in custom_kg:
        factor = number(custom_kg[unit], "package weight")
        if factor <= 0:
            raise ValueError("Package weight must be positive")
        return "kg", factor
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)\s*)?(kg|kgs|kilogram|kilograms|g|gram|grams|l|litre|litres|liter|liters|ml)(?:\s+bag)?", unit)
    if match:
        size = Decimal(match[1] or "1")
        suffix = match[2]
        if suffix in {"g", "gram", "grams", "ml"}:
            size /= 1000
        if size <= 0:
            raise ValueError("Unit size must be positive")
        return ("litres" if suffix.startswith("l") or suffix == "ml" else "kg"), size
    if unit in {"unit", "units", "piece", "pieces", "head", "bunch"}:
        return unit if unit in {"head", "bunch"} else "units", Decimal(1)
    raise ValueError(f"Unknown package weight for {value!r}; supply an explicit --unit-kg mapping")


def parse_rows(content, source, *, coordinates=None, custom_kg=None, rejects=None, allow_unlocated=False):
    if source not in {"hdx", "kamis"}:
        raise ValueError("Supported Phase 1 sources: hdx, kamis")
    if len(content) > MAX_BYTES:
        raise ValueError("CSV exceeds 20 MB")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    rows = []
    for line, raw in enumerate(reader, start=2):
        row = {str(k).strip().lower().replace(" ", "_"): (v or "").strip() for k, v in raw.items() if k}
        # HDX's optional second header contains HXL tags, not observations.
        if row and all(not v or v.startswith("#") for v in row.values()):
            continue
        if not any(row.values()):
            continue
        try:
            market = row.get("market", "")
            commodity = row.get("commodity") or row.get("product", "")
            if not market or not commodity:
                raise ValueError("market and commodity are required")
            if source == "kamis":
                distinctions = [row[key] for key in ("classification", "grade", "sex") if row.get(key) not in (None, "", "-")]
                if distinctions:
                    commodity += " [" + "/".join(distinctions) + "]"
            raw_date = row.get("date", "")
            try:
                observed = date.fromisoformat(raw_date)
            except ValueError:
                observed = datetime.strptime(raw_date, "%d/%m/%Y").date()
            lat, lon = row.get("latitude"), row.get("longitude")
            if not lat or not lon:
                lat, lon = (coordinates or {}).get(market, (None, None))
            if allow_unlocated and not lat and not lon:
                lat, lon = None, None
            else:
                lat, lon = number(lat, "latitude"), number(lon, "longitude")
                weather_grid(lat, lon)  # Coordinate range validation.
            unit = row.get("unit", "")
            if source == "kamis" and not unit:
                units = {value.split("/", 1)[1].strip().lower() for key in ("wholesale", "retail", "wholesale_price", "retail_price")
                         if "/" in (value := row.get(key, ""))}
                if len(units) == 1:
                    unit = units.pop()
            base_unit, factor = unit_factor(unit, custom_kg)
            volume = number(row.get("volume") or row.get("supply_volume"), "volume", optional=True)
            if volume is not None and volume < 0:
                raise ValueError("volume must not be negative")
            frequency = row.get("frequency") or ("monthly" if source == "hdx" else "daily")
            if frequency not in {"daily", "monthly"}:
                raise ValueError("frequency must be daily or monthly")
            common = dict(date=observed, market=market, commodity=commodity, latitude=lat, longitude=lon,
                          base_unit=base_unit, volume=volume * factor if volume is not None else None,
                          currency=row.get("currency") or "KES", frequency=frequency)
            prices = [(row.get("pricetype", "retail").lower(), row.get("price"))] if source == "hdx" else [
                (kind, row.get(kind) or row.get(kind + "_price")) for kind in ("wholesale", "retail")]
            parsed_prices = []
            for kind, value in prices:
                if not value or value.strip().lower() in {"-", "n/a", "na"}:
                    continue
                if "/" in value:
                    value, quoted_unit = value.split("/", 1)
                    if unit_factor(quoted_unit, custom_kg) != (base_unit, factor):
                        raise ValueError("Inconsistent units within price row")
                price = number(value, "price") / factor
                if price < 0:
                    raise ValueError("price must not be negative")
                parsed_prices.append({**common, "price": price, "price_type": kind})
            if not parsed_prices:
                raise ValueError("No price columns found")
            rows.extend(parsed_prices)
        except (ValueError, TypeError) as error:
            if rejects is not None:
                rejects.append({"line": line, "market": row.get("market"), "reason": str(error)})
                continue
            raise ValueError(f"CSV line {line}: {error}") from error
        if len(rows) > 200000:
            raise ValueError("CSV exceeds 200,000 observations")
    if not rows:
        raise ValueError("CSV contains no observations")
    return rows


def import_market_rows(db, rows, *, source, source_url, content_sha256, organization_id, opening_days=0):
    if db.get(Organization, organization_id) is None:
        raise ValueError("Organization not found")
    if not source_url.startswith("https://"):
        raise ValueError("A public HTTPS source URL is required for provenance")
    if not 0 <= opening_days <= 30:
        raise ValueError("Opening inventory horizon must be 0–30 days")
    run = ImportRun(organization_id=organization_id, source=source, source_url=source_url,
                    content_sha256=content_sha256, row_count=len(rows))
    db.add(run)
    db.flush()
    inserted, updated = 0, 0
    locations, products, openings = {}, {}, {}
    observations = {row.source_key: row for row in db.query(MarketObservation).filter_by(
        organization_id=organization_id, source=source)}
    for values in rows:
        market = values["market"]
        location_key = (market, values["latitude"], values["longitude"])
        if location_key not in locations:
            location = db.query(Location).filter_by(organization_id=organization_id, name=market,
                location_type="MARKET", latitude=values["latitude"], longitude=values["longitude"]).first()
            if location is None:
                location = Location(organization_id=organization_id, name=market, location_type="MARKET",
                    latitude=values["latitude"], longitude=values["longitude"],
                    weather_grid_key=weather_grid(values["latitude"], values["longitude"])[0] if values["latitude"] is not None else None)
                db.add(location)
                db.flush()
            locations[location_key] = location
        location = locations[location_key]
        sku = "market:" + hashlib.sha256(f'{values["commodity"]}:{values["base_unit"]}'.encode()).hexdigest()[:24]
        if sku not in products:
            product = db.query(Product).filter_by(organization_id=organization_id, sku=sku).first()
            if product is None:
                product = Product(organization_id=organization_id, sku=sku, name=values["commodity"],
                                  unit=values["base_unit"], description=f"Public market catalog ({source})")
                db.add(product)
                db.flush()
            products[sku] = product
        product = products[sku]
        source_key = hashlib.sha256(json.dumps([source, market, str(values["latitude"]), str(values["longitude"]),
            sku, str(values["date"]), values["price_type"], values["currency"], values["frequency"]]).encode()).hexdigest()
        observation = observations.get(source_key)
        fields = {key: values[key] for key in ("date", "price", "price_type", "currency", "base_unit", "volume", "frequency")}
        if observation is None:
            observation = MarketObservation(organization_id=organization_id, location_id=location.id,
                product_id=product.id, source=source, source_key=source_key, import_run_id=run.id, **fields)
            db.add(observation)
            observations[source_key] = observation
            inserted += 1
        else:
            for key, value in fields.items():
                setattr(observation, key, value)
            observation.import_run_id = run.id
            updated += 1
        # The source-key map also deduplicates rows that have not been flushed yet.
        if opening_days and values["volume"] is not None and values["frequency"] == "daily":
            key = (location.id, product.id)
            if key not in openings or values["date"] > openings[key]["date"]:
                openings[key] = values
    for (location_id, product_id), values in openings.items():
        code = "SIMULATED-" + source + "-" + str(values["date"])
        existing = db.query(InventoryBatch).filter_by(organization_id=organization_id, location_id=location_id,
                                                     product_id=product_id, batch_code=code).first()
        if existing is None:
            db.add(InventoryBatch(organization_id=organization_id, location_id=location_id, product_id=product_id,
                batch_code=code, quantity_on_hand=values["volume"] * opening_days, unit_cost=values["price"],
                received_at=datetime.combine(values["date"], datetime.min.time(), timezone.utc), is_synthetic=True))
    db.flush()
    return {"run_id": run.id, "inserted": inserted, "updated": updated, "simulated_batches": len(openings)}


def daily_price_series(observations):
    """Resample one already-selected price series, explicitly labeling filled days.

    No volume filling: price-only records cannot establish daily demand.
    """
    if not observations:
        return []
    series_keys = {(row.location_id, row.product_id, row.price_type, row.currency, row.base_unit, row.source)
                   for row in observations}
    if len(series_keys) != 1:
        raise ValueError("Select one market/product/price-type/currency/unit/source series")
    by_day = {row.date: row for row in observations}
    current, end = min(by_day), max(by_day)
    price = None
    result = []
    while current <= end:
        observed = by_day.get(current)
        if observed:
            price = observed.price
        result.append({"date": current, "price": price, "is_imputed": observed is None,
                       "volume": observed.volume if observed else None})
        current += timedelta(days=1)
    return result
