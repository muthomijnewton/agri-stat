from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location_type: Literal["FARM", "DEPOT", "SHOP", "MARKET"]
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, max_digits=10, decimal_places=7)

    @model_validator(mode="after")
    def coordinates_required_except_markets(self):
        if self.latitude is None or self.longitude is None:
            if self.location_type != "MARKET" or self.latitude is not None or self.longitude is not None:
                raise ValueError("Coordinates are required together; only markets may omit both")
        return self


class LocationRead(LocationCreate, Record):
    id: UUID
    organization_id: UUID
    weather_grid_key: str | None
    updated_at: datetime


class RouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    origin_location_id: UUID
    dest_location_id: UUID
    base_lead_time_days: Decimal = Field(gt=0, le=365, max_digits=10, decimal_places=4)

    @model_validator(mode="after")
    def different_endpoints(self):
        if self.origin_location_id == self.dest_location_id:
            raise ValueError("Route endpoints must differ")
        return self


class RouteRead(RouteCreate, Record):
    id: UUID
    organization_id: UUID
    total_distance_km: Decimal | None
    unpaved_ratio: Decimal | None
    unknown_surface_ratio: Decimal | None
    current_risk_level: str
    adjusted_lead_time_days: Decimal | None
    route_geometry: dict | None
    inspected_at: datetime | None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    category: Literal["PRODUCE_PERISHABLE", "PRODUCE_STAPLE", "FERTILIZER", "SEED", "CROP_PROTECTION"]
    unit: Literal["kg", "litres", "units"] = "kg"
    unit_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    shelf_life_days: int | None = Field(default=None, gt=0)
    optimal_temp_min_c: Decimal | None = Field(default=None, ge=-100, le=100)
    optimal_temp_max_c: Decimal | None = Field(default=None, ge=-100, le=100)

    @model_validator(mode="after")
    def valid_temperature_range(self):
        if self.optimal_temp_min_c is not None and self.optimal_temp_max_c is not None:
            if self.optimal_temp_min_c > self.optimal_temp_max_c:
                raise ValueError("Minimum temperature must not exceed maximum temperature")
        if self.category == "PRODUCE_PERISHABLE" and self.shelf_life_days is None:
            raise ValueError("Perishable products require shelf_life_days")
        return self


class ProductRead(Record):
    id: int
    name: str
    sku: str | None
    category: str | None
    unit: str | None
    unit_price: Decimal | None
    shelf_life_days: int | None
    optimal_temp_min_c: Decimal | None
    optimal_temp_max_c: Decimal | None


class BatchCreate(BaseModel):
    location_id: UUID
    product_id: int = Field(gt=0)
    batch_code: str = Field(min_length=1, max_length=100)
    quantity_on_hand: Decimal = Field(ge=0, max_digits=16, decimal_places=4)
    unit_cost: Decimal = Field(ge=0, max_digits=16, decimal_places=4)
    received_at: AwareDatetime
    expires_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        self.received_at = self.received_at.astimezone(timezone.utc)
        if self.expires_at is not None:
            self.expires_at = self.expires_at.astimezone(timezone.utc)
        if self.expires_at and self.expires_at <= self.received_at:
            raise ValueError("Expiry must follow receipt")
        return self


class BatchRead(Record):
    id: UUID
    location_id: UUID
    product_id: int
    batch_code: str
    quantity_on_hand: Decimal
    unit_cost: Decimal
    received_at: datetime
    expires_at: datetime | None
    status: str
    is_synthetic: bool


class WeatherRead(Record):
    weather_grid_key: str
    date: date
    is_forecast: bool
    rainfall_mm: Decimal | None
    temp_max_c: Decimal | None
    temp_min_c: Decimal | None
    soil_moisture_0_to_7cm: Decimal | None
    evapotranspiration_mm: Decimal | None
    source: str
    fetched_at: datetime
