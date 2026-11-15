"""Append-only farm sales and the physical batches consumed by each sale."""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from app.db.database import Base
from app.models.foundation import TenantRecord, new_id, utcnow


class SalesOrder(TenantRecord, Base):
    __tablename__ = 'sales_orders'
    id = Column(String(36), primary_key=True, default=new_id)
    client_event_id = Column(String(36), nullable=False)
    request_hash = Column(String(64), nullable=False)
    location_id = Column(String(36), ForeignKey('locations.id'), nullable=False)
    recorded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    sold_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    currency = Column(String(3), nullable=False, default='KES')
    total_amount = Column(Numeric(18, 2), nullable=False)
    __table_args__ = (UniqueConstraint('organization_id', 'client_event_id', name='uq_sales_org_event'),
                     CheckConstraint('total_amount >= 0', name='ck_sales_total'))


class SalesOrderItem(Base):
    __tablename__ = 'sales_order_items'
    id = Column(String(36), primary_key=True, default=new_id)
    order_id = Column(String(36), ForeignKey('sales_orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Numeric(16, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    __table_args__ = (UniqueConstraint('order_id', 'product_id', name='uq_sales_item_product'),
                     CheckConstraint('quantity > 0 AND unit_price >= 0 AND total_amount >= 0', name='ck_sales_item_values'))


class SaleAllocation(Base):
    __tablename__ = 'sale_allocations'
    id = Column(String(36), primary_key=True, default=new_id)
    order_item_id = Column(String(36), ForeignKey('sales_order_items.id'), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey('inventory_batches.id'), nullable=False)
    quantity = Column(Numeric(16, 4), nullable=False)
    __table_args__ = (UniqueConstraint('order_item_id', 'batch_id', name='uq_sale_item_batch'),
                     CheckConstraint('quantity > 0', name='ck_sale_allocation_quantity'))
