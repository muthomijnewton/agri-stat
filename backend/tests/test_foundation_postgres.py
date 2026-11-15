"""Real extension integration, opt-in locally and enabled in CI."""
import os
from uuid import uuid4
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from app.db.migrate import ROOT


@pytest.mark.skipif(not os.getenv("PHASE1_POSTGRES_TEST_URL"), reason="PostgreSQL with TimescaleDB/PostGIS is not available")
def test_postgres_spatial_columns_and_weather_hypertable():
    engine = create_engine(os.environ["PHASE1_POSTGRES_TEST_URL"])
    schema = "phase1_test_" + uuid4().hex
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            connection.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
            config = Config(str(ROOT / "alembic.ini"))
            config.attributes["connection"] = connection
            config.attributes["version_table_schema"] = schema
            command.upgrade(config, "head")
            assert connection.execute(text("SELECT count(*) FROM timescaledb_information.hypertables WHERE hypertable_schema=:schema AND hypertable_name='weather_observations'"), {"schema": schema}).scalar() == 1
            connection.execute(text("INSERT INTO locations (id,name,location_type,latitude,longitude,weather_grid_key,organization_id,updated_at) VALUES ('a','Farm','FARM',0,37,'grid','00000000-0000-0000-0000-000000000001',CURRENT_TIMESTAMP), ('b','Market','MARKET',NULL,NULL,NULL,'00000000-0000-0000-0000-000000000001',CURRENT_TIMESTAMP)"))
            assert connection.execute(text("SELECT ST_AsText(geom::geometry) FROM locations WHERE id='a'")).scalar() == "POINT(37 0)"
            assert connection.execute(text("SELECT geom FROM locations WHERE id='b'")).scalar() is None
            connection.execute(text("INSERT INTO supply_routes (id,name,origin_location_id,dest_location_id,base_lead_time_days,current_risk_level,route_geometry,organization_id,updated_at) VALUES ('r','Route','a','b',1,'UNKNOWN','null','00000000-0000-0000-0000-000000000001',CURRENT_TIMESTAMP)"))
            assert connection.execute(text("SELECT route_geom FROM supply_routes WHERE id='r'")).scalar() is None
            connection.execute(text("UPDATE supply_routes SET route_geometry = :geometry WHERE id='r'"), {"geometry": '{"type":"LineString","coordinates":[[37,0],[38,1]]}'})
            assert connection.execute(text("SELECT ST_AsText(route_geom::geometry) FROM supply_routes WHERE id='r'")).scalar() == "LINESTRING(37 0,38 1)"
        finally:
            transaction.rollback()
    engine.dispose()
