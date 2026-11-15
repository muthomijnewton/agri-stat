"""Phase 1 contracts: migration preservation, isolation, provenance, provider gaps."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.db.migrate import ROOT, migrate_database
from app.models.foundation import (DEFAULT_ORGANIZATION_ID, InventoryBatch, Location,
    MarketObservation, Organization, WeatherObservation)
from app.models.models import Product, Transaction
from app.services.inventory_service import batch_status
from app.services.real_data import daily_price_series, import_market_rows, parse_rows, unit_factor
from app.services.routing_service import surface_profile
from app.services.weather_service import daily_rows, sync_location_weather, weather_grid


@pytest.fixture
def organization(db):
    row = Organization(id=DEFAULT_ORGANIZATION_ID, name="Test organization")
    db.add(row)
    db.commit()
    return row


def test_migration_fresh_and_repeat(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    migrate_database(engine)
    migrate_database(engine)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0005_planning"
        assert connection.execute(text("SELECT count(*) FROM organizations")).scalar() == 1
    assert {"inventory_batches", "locations", "weather_observations"} <= set(inspect(engine).get_table_names())
    engine.dispose()


def test_migration_adopts_legacy_without_losing_data(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    config = Config(str(ROOT / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "0001_initial")
        connection.execute(text("INSERT INTO products (id, name) VALUES (47, 'Existing maize')"))
        connection.execute(text("DROP TABLE alembic_version"))
    migrate_database(engine)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT name FROM products WHERE id=47")).scalar() == "Existing maize"
        assert connection.execute(text("SELECT organization_id FROM products WHERE id=47")).scalar() == DEFAULT_ORGANIZATION_ID
    assert "transaction_type" in {column["name"] for column in inspect(engine).get_columns("transactions")}
    engine.dispose()


def test_partial_legacy_database_is_not_stamped(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'partial.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE products (id INTEGER)"))
    with pytest.raises(RuntimeError, match="Partial legacy"):
        migrate_database(engine)
    assert "alembic_version" not in inspect(engine).get_table_names()
    engine.dispose()


def test_locations_are_scoped_and_validate_coordinates(admin_client, db, organization):
    other = Organization(id=str(uuid4()), name="Other")
    db.add(other)
    db.flush()
    db.add(Location(organization_id=other.id, name="Hidden", location_type="FARM", latitude=0,
                    longitude=37, weather_grid_key=weather_grid(0, 37)[0]))
    db.commit()
    payload = {"name": "Farm", "location_type": "FARM", "latitude": -0.1, "longitude": 37}
    created = admin_client.post("/api/v1/locations", json=payload)
    assert created.status_code == 201, created.text
    assert len(admin_client.get("/api/v1/locations").json()) == 1
    assert admin_client.post("/api/v1/locations", json={**payload, "latitude": 91}).status_code == 422


def test_nonadmin_cannot_create_location(client, organization):
    # Existing conftest overrides get_current_admin; remove that override for this check.
    from app.main import app
    from app.core.security import get_current_admin
    app.dependency_overrides.pop(get_current_admin)
    assert client.post("/api/v1/locations", json={"name": "Farm", "location_type": "FARM", "latitude": 0, "longitude": 37}).status_code == 403


def test_batch_validation_and_conflict(admin_client, db, organization):
    location = admin_client.post("/api/v1/locations", json={"name": "Depot", "location_type": "DEPOT", "latitude": 0, "longitude": 37}).json()
    product = admin_client.post("/api/v1/products", json={"name": "Tomato", "sku": "TOM", "category": "PRODUCE_PERISHABLE", "shelf_life_days": 7}).json()
    now = datetime.now(timezone.utc)
    payload = dict(location_id=location["id"], product_id=product["id"], batch_code="LOT1", quantity_on_hand=Decimal("4.25").__str__(),
                   unit_cost="20.5", received_at=now.isoformat())
    assert admin_client.post("/api/v1/inventory-batches", json=payload).status_code == 422
    payload["expires_at"] = (now + timedelta(days=2)).isoformat()
    response = admin_client.post("/api/v1/inventory-batches", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "EXPIRING_SOON"
    assert admin_client.post("/api/v1/inventory-batches", json=payload).status_code == 409
    assert admin_client.post("/api/v1/inventory-batches", json={**payload, "quantity_on_hand": -1}).status_code == 422


def test_cross_organization_reference_rejected(admin_client, db, organization):
    other = Organization(id=str(uuid4()), name="Other")
    db.add(other)
    db.flush()
    foreign = Location(organization_id=other.id, name="Foreign", location_type="DEPOT", latitude=0,
                       longitude=37, weather_grid_key=weather_grid(0, 37)[0])
    db.add(foreign)
    db.commit()
    assert admin_client.get(f"/api/v1/locations/{foreign.id}").status_code == 404
    assert admin_client.post(f"/api/v1/locations/{foreign.id}/sync-weather").status_code == 404


def test_disabled_queue_is_reported(admin_client, organization, monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    location = admin_client.post("/api/v1/locations", json={"name": "Farm", "location_type": "FARM", "latitude": 0, "longitude": 37}).json()
    assert admin_client.post(f'/api/v1/locations/{location["id"]}/sync-weather').status_code == 503


def test_grid_center_is_stable_and_not_decimal_rounding():
    key, lat, lon = weather_grid(-0.1, 37)
    assert weather_grid(lat, lon)[0] == key
    assert weather_grid(lat + 0.01, lon)[0] == key
    assert weather_grid(lat + 0.05, lon)[0] != key
    assert weather_grid(90, 180)[0] == weather_grid(*weather_grid(90, 180)[1:])[0]


def weather_payload(day, rain=12):
    return {"daily": {"time": [str(day)], "rain_sum": [rain], "temperature_2m_max": [29],
            "temperature_2m_min": [18], "et0_fao_evapotranspiration": [3]}}


def test_weather_null_archive_never_becomes_actual():
    assert list(daily_rows(weather_payload(date(2026, 1, 1), rain=None), forecast=False)) == []


def test_weather_sync_preserves_forecast_and_archive_idempotently(db, organization):
    loc = Location(organization_id=organization.id, name="Farm", location_type="FARM", latitude=0,
                   longitude=37, weather_grid_key=weather_grid(0, 37)[0])
    db.add(loc)
    db.flush()
    today = date(2026, 1, 20)
    calls = []
    def fetch(url, params):
        calls.append(params)
        # ERA5-Land alone has no rain in the provider contract.
        rain = None if params.get("models") == "era5_land" else 12
        return weather_payload(today if "forecast" in url else today - timedelta(days=5), rain=rain)
    sync_location_weather(db, loc, fetch=fetch, today=today)
    sync_location_weather(db, loc, fetch=fetch, today=today)
    assert db.query(WeatherObservation).count() == 2
    assert {row.is_forecast for row in db.query(WeatherObservation)} == {True, False}
    assert calls[1]["end_date"] == "2026-01-15"


def test_forecast_soil_depth_estimate():
    payload = weather_payload(date(2026, 1, 1))
    payload["hourly"] = {"time": ["2026-01-01T00:00"], "soil_moisture_0_to_1cm": [0.1],
                         "soil_moisture_1_to_3cm": [0.2], "soil_moisture_3_to_9cm": [0.3]}
    row = next(daily_rows(payload, forecast=True))
    assert row["soil_moisture_0_to_7cm"] == pytest.approx(1.7 / 7)
    assert "estimate" in row["source"]


def test_route_uses_edge_lengths_and_keeps_unknown_surface():
    legs = [{"annotation": {"nodes": [1, 2, 3, 4], "distance": [100, 300, 600]}}]
    ways = [{"nodes": [1, 2], "tags": {"surface": "asphalt"}}, {"nodes": [2, 3], "tags": {"surface": "murram"}},
            {"nodes": [50, 51], "tags": {"surface": "dirt"}}]
    assert surface_profile(legs, ways) == {"unpaved_ratio": 0.3, "unknown_surface_ratio": 0.6}
    with pytest.raises(ValueError, match="incomplete"):
        surface_profile([{"annotation": {"nodes": [1, 2], "distance": []}}], ways)


@pytest.mark.parametrize("unit,expected", [("90 KG", ("kg", Decimal(90))), ("400 G", ("kg", Decimal('.4'))),
                                          ("500 ML", ("litres", Decimal('.5')))])
def test_package_units(unit, expected):
    assert unit_factor(unit) == expected


def test_unknown_crate_weight_is_not_invented():
    with pytest.raises(ValueError, match="Unknown package"):
        unit_factor("crate")
    assert unit_factor("crate", {"crate": 20}) == ("kg", Decimal(20))


HDX = b'date,market,commodity,latitude,longitude,unit,price,pricetype,currency\n2026-01-15,Meru,Maize,0.05,37.65,90 KG,4500,Wholesale,KES\n'


def test_real_price_import_is_repeatable_and_does_not_create_sales(db, organization):
    rows = parse_rows(HDX, "hdx")
    assert rows[0]["price"] == 50
    for _ in range(2):
        import_market_rows(db, rows, source="hdx", source_url="https://data.humdata.org/dataset/example",
                          content_sha256="a" * 64, organization_id=organization.id)
    assert db.query(MarketObservation).count() == 1
    assert db.query(Transaction).count() == 0
    assert db.query(InventoryBatch).count() == 0


def test_kamis_quoted_units_and_sidecar_coordinates():
    raw = b'Commodity,Market,Wholesale,Retail,Supply Volume,Date\nDry Maize,Taveta Retail Market,35.00/Kg,50.00/Kg,8000,2026-11-11\n'
    rows = parse_rows(raw, "kamis", coordinates={"Taveta Retail Market": (-3.4, 37.68)})
    assert len(rows) == 2
    assert rows[0]["price"] == 35 and rows[0]["volume"] == 8000


def test_missing_coordinates_rejected_not_guessed():
    raw = HDX.replace(b'0.05,37.65', b',')
    with pytest.raises(ValueError, match="latitude"):
        parse_rows(raw, "hdx")


def test_price_resampling_marks_imputation_and_does_not_fill_demand():
    common = dict(location_id="1", product_id=1, price_type="retail", currency="KES", base_unit="kg", source="hdx")
    observations = [SimpleNamespace(**common, date=date(2026, 1, day), price=Decimal(price), volume=None)
                    for day, price in [(1, 50), (3, 55)]]
    rows = daily_price_series(observations)
    assert rows[1]["is_imputed"] and rows[1]["price"] == 50 and rows[1]["volume"] is None


def test_expired_and_depleted_batch_status():
    now = datetime.now(timezone.utc)
    row = SimpleNamespace(quantity_on_hand=3, expires_at=now - timedelta(days=1))
    assert batch_status(row, now) == "EXPIRED"
    row.quantity_on_hand = 0
    assert batch_status(row, now) == "DEPLETED"


def test_live_kamis_html_and_missing_quote():
    from app.services.live_market_service import kamis_csv
    html = '<table><tr><th>Commodity</th><th>Market</th><th>Date</th><th>Wholesale</th><th>Retail</th></tr><tr><td>Maize</td><td>Test market</td><td>2026-11-11</td><td>-</td><td>50/Kg</td></tr></table>'
    rows = parse_rows(kamis_csv(html), "kamis", allow_unlocated=True)
    assert len(rows) == 1 and rows[0]["price"] == 50
    assert rows[0]["latitude"] is None


def test_live_unlocated_market_is_retained_without_weather(admin_client, db, organization):
    response = admin_client.post("/api/v1/locations", json={"name": "Published market", "location_type": "MARKET"})
    assert response.status_code == 201, response.text
    identifier = response.json()["id"]
    assert response.json()["latitude"] is None
    assert admin_client.post(f"/api/v1/locations/{identifier}/sync-weather").status_code == 422


def test_live_market_api_shows_provenance(admin_client, db, organization):
    rows = parse_rows(HDX, "hdx")
    import_market_rows(db, rows, source="hdx", source_url="https://data.humdata.org/dataset/example",
                      content_sha256="a" * 64, organization_id=organization.id)
    import_market_rows(db, rows, source="kamis", source_url="https://kamis.kilimo.go.ke/site/market",
                      content_sha256="b" * 64, organization_id=organization.id)
    db.commit()
    result = admin_client.get("/api/v1/market-prices?q=maize&source=kamis").json()
    assert result["total"] == 1
    assert result["items"][0]["market"] == "Meru"
    assert result["items"][0]["source"] == "kamis"
    assert result["items"][0]["source_url"].startswith("https://kamis.kilimo.go.ke/")
    assert admin_client.get("/api/v1/market-prices?source=hdx").json()["total"] == 1
    assert {r["source"] for r in admin_client.get("/api/v1/market-observations").json()} == {"hdx", "kamis"}
    summary = admin_client.get("/api/v1/market-summary").json()
    assert {r["source"] for r in summary["sources"]} == {"hdx", "kamis"}
    assert summary["sources"][0]["observations"] == 1 and summary["markets"] == 1
    for params, expected in [({"location":"mer", "product":"MAIZE"},2),
                             ({"location":"Nairobi", "product":"maize"},0),
                             ({"location":"Meru", "product":"tomato"},0),
                             ({"location":"%"},0), ({"product":"_"},0)]:
        assert admin_client.get("/api/v1/market-prices",params=params).json()["total"] == expected


def test_live_refresh_downloads_both_sources():
    from app.services.live_market_service import prepare_live_sources, KAMIS_URLS, HDX_URL
    calls=[]
    def fetch(url):
        calls.append(url)
        if url == HDX_URL: return HDX
        return b'<table><tr><th>Commodity</th><th>Market</th><th>Date</th><th>Wholesale</th><th>Retail</th></tr><tr><td>Maize</td><td>Meru</td><td>2026-11-11</td><td>-</td><td>50/Kg</td></tr></table>'
    sources=prepare_live_sources(fetch=fetch)
    assert calls == [HDX_URL] + KAMIS_URLS
    assert {s["source"] for s in sources} == {"hdx", "kamis"}


def test_hdx_source_can_be_loaded(db, organization):
    from app.services.live_market_service import load_live_sources
    result=load_live_sources(db,[{"source":"hdx", "source_url":"https://data.humdata.org/dataset/example",
        "content_sha256":"c"*64,"rows":parse_rows(HDX,"hdx"),"rejects":[]}],organization_id=organization.id)
    assert result[0]["source"] == "hdx"


def test_explicit_demo_reset_retains_accounts(db, organization, auth_user, sample_product):
    from app.services.live_market_service import clear_demo_business_data
    from app.models.models import User
    clear_demo_business_data(db, organization.id)
    assert db.query(User).filter_by(id=auth_user.id).count() == 1
    assert db.query(Product).count() == 0


def test_refresh_job_status_hides_other_organization(monkeypatch):
    from fastapi import HTTPException
    from app.api.endpoints.foundation import job_status
    from redis import Redis
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379/7')
    monkeypatch.setattr(Redis, 'from_url', lambda *args, **kwargs: SimpleNamespace(get=lambda key: b'another-organization'))
    with pytest.raises(HTTPException) as error:
        job_status(uuid4(), SimpleNamespace(organization_id=DEFAULT_ORGANIZATION_ID))
    assert error.value.status_code == 404


def test_refresh_job_failure_does_not_expose_provider_errors(monkeypatch):
    from app.api.endpoints.foundation import job_status
    from app.workers.celery_app import celery_app
    from redis import Redis
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379/7')
    monkeypatch.setattr(Redis, 'from_url', lambda *args, **kwargs: SimpleNamespace(get=lambda key: DEFAULT_ORGANIZATION_ID.encode()))
    monkeypatch.setattr(celery_app, 'AsyncResult', lambda task: SimpleNamespace(state='FAILURE', result=RuntimeError('private diagnostic')))
    result = job_status(uuid4(), SimpleNamespace(organization_id=DEFAULT_ORGANIZATION_ID))
    assert result['status'] == 'FAILURE'
    assert result['result'] is None
    assert 'private diagnostic' not in str(result)


def test_live_verification_bypasses_response_cache(monkeypatch):
    import httpx
    from redis import Redis
    from app.services import external_data
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379/7')
    def forbidden_cache(*args, **kwargs):
        pytest.fail('Live verification must not consult Redis')
    monkeypatch.setattr(Redis, 'from_url', forbidden_cache)
    requests = []
    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={'elements': []})
    client_class = httpx.Client
    monkeypatch.setattr(external_data.httpx, 'Client', lambda **kwargs: client_class(
        transport=httpx.MockTransport(respond), **kwargs))
    assert external_data.fetch_json('https://example.test/api/interpreter',
        data={'data': '[out:json];out;'}, cache_seconds=0) == {'elements': []}
    assert len(requests) == 1
    assert requests[0].method == 'POST'
    assert 'agri-stat' in requests[0].headers['User-Agent']
