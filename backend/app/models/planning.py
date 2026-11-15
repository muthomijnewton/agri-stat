"""Confirmed demand days and reproducible, tenant-scoped model runs."""
from sqlalchemy import Column, String, Integer, Date, Numeric, Boolean, JSON, ForeignKey, UniqueConstraint, CheckConstraint
from app.db.database import Base
from app.models.foundation import TenantRecord, new_id


class DemandDay(TenantRecord, Base):
    __tablename__ = 'demand_days'
    id = Column(String(36), primary_key=True, default=new_id)
    location_id = Column(String(36), ForeignKey('locations.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Numeric(16, 4), nullable=False)
    stockout = Column(Boolean, nullable=False)
    source = Column(String(200), nullable=False)
    __table_args__ = (UniqueConstraint('organization_id', 'location_id', 'product_id', 'date', name='uq_demand_day'),
                     CheckConstraint('quantity >= 0', name='ck_demand_quantity'))


class ForecastRun(TenantRecord, Base):
    __tablename__ = 'forecast_runs'
    id = Column(String(36), primary_key=True, default=new_id)
    location_id = Column(String(36), ForeignKey('locations.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    route_id = Column(String(36), ForeignKey('supply_routes.id'), nullable=False)
    status = Column(String(30), nullable=False, default='queued')
    result = Column(JSON, nullable=False, default=dict)
