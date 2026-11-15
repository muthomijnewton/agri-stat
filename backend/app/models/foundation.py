"""Phase 1 records. Existing integer product IDs remain API-compatible."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime,
                        ForeignKey, Integer, JSON, Numeric, String, Text,
                        UniqueConstraint)
from app.db.database import Base

DEFAULT_ORGANIZATION_ID = "00000000-0000-0000-0000-000000000001"


def new_id():
    return str(uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String(36), primary_key=True, default=new_id)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TenantRecord:
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Location(TenantRecord, Base):
    __tablename__ = "locations"
    id = Column(String(36), primary_key=True, default=new_id)
    name = Column(String(255), nullable=False)
    location_type = Column(String(16), nullable=False)
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    weather_grid_key = Column(String(64), index=True)
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_location_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_location_lon"),
        CheckConstraint("location_type IN ('FARM','DEPOT','SHOP','MARKET')", name="ck_location_type"),
        CheckConstraint("(latitude IS NOT NULL AND longitude IS NOT NULL AND weather_grid_key IS NOT NULL) OR (location_type = 'MARKET' AND latitude IS NULL AND longitude IS NULL AND weather_grid_key IS NULL)", name="ck_location_coordinates"),
    )


class SupplyRoute(TenantRecord, Base):
    __tablename__ = "supply_routes"
    id = Column(String(36), primary_key=True, default=new_id)
    name = Column(String(255), nullable=False)
    origin_location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    dest_location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    total_distance_km = Column(Numeric(12, 3))
    unpaved_ratio = Column(Numeric(7, 6))
    unknown_surface_ratio = Column(Numeric(7, 6))
    base_lead_time_days = Column(Numeric(10, 4), nullable=False)
    adjusted_lead_time_days = Column(Numeric(10, 4))
    current_risk_level = Column(String(16), nullable=False, default="UNKNOWN")
    route_geometry = Column(JSON)
    inspected_at = Column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("origin_location_id <> dest_location_id", name="ck_route_endpoints"),
        CheckConstraint("base_lead_time_days > 0", name="ck_route_lead_time"),
        CheckConstraint("unpaved_ratio BETWEEN 0 AND 1", name="ck_route_unpaved"),
        CheckConstraint("unknown_surface_ratio BETWEEN 0 AND 1", name="ck_route_unknown"),
    )


class InventoryBatch(TenantRecord, Base):
    __tablename__ = "inventory_batches"
    id = Column(String(36), primary_key=True, default=new_id)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_code = Column(String(100), nullable=False)
    quantity_on_hand = Column(Numeric(16, 4), nullable=False)
    unit_cost = Column(Numeric(16, 4), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    status = Column(String(24), nullable=False, default="ACTIVE")
    is_synthetic = Column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint("organization_id", "location_id", "product_id", "batch_code", name="uq_batch_code"),
        CheckConstraint("quantity_on_hand >= 0 AND unit_cost >= 0", name="ck_batch_nonnegative"),
        CheckConstraint("expires_at IS NULL OR expires_at > received_at", name="ck_batch_expiry"),
    )


class WeatherObservation(TenantRecord, Base):
    __tablename__ = "weather_observations"
    # Include the partition date in every unique key, as TimescaleDB requires.
    organization_id = Column(String(36), ForeignKey("organizations.id"), primary_key=True)
    weather_grid_key = Column(String(64), primary_key=True)
    date = Column(Date, primary_key=True)
    is_forecast = Column(Boolean, primary_key=True)
    rainfall_mm = Column(Numeric(12, 4))
    temp_max_c = Column(Numeric(8, 4))
    temp_min_c = Column(Numeric(8, 4))
    soil_moisture_0_to_7cm = Column(Numeric(10, 6))
    evapotranspiration_mm = Column(Numeric(12, 4))
    source = Column(String(64), nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class ImportRun(TenantRecord, Base):
    __tablename__ = "import_runs"
    id = Column(String(36), primary_key=True, default=new_id)
    source = Column(String(32), nullable=False)
    source_url = Column(Text, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    row_count = Column(Integer, nullable=False)
    imported_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class MarketObservation(TenantRecord, Base):
    """Public market prices/volumes are not a tenant's sales transactions."""
    __tablename__ = "market_observations"
    id = Column(String(36), primary_key=True, default=new_id)
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Numeric(16, 4), nullable=False)
    price_type = Column(String(32), nullable=False)
    currency = Column(String(8), nullable=False)
    base_unit = Column(String(16), nullable=False)
    volume = Column(Numeric(16, 4))
    frequency = Column(String(16), nullable=False)
    source = Column(String(32), nullable=False)
    source_key = Column(String(64), nullable=False)
    import_run_id = Column(String(36), ForeignKey("import_runs.id"), nullable=False)
    __table_args__ = (UniqueConstraint("organization_id", "source_key", name="uq_market_source_key"),)
