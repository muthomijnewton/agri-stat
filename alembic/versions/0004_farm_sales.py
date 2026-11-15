"""Farm sales ledger with auditable FEFO allocations."""
from alembic import op
import sqlalchemy as sa
revision = '0004_farm_sales'
down_revision = '0003_unlocated_markets'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('sales_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('client_event_id', sa.String(36), nullable=False),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('location_id', sa.String(36), sa.ForeignKey('locations.id'), nullable=False),
        sa.Column('recorded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('sold_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.UniqueConstraint('organization_id', 'client_event_id', name='uq_sales_org_event'),
        sa.CheckConstraint('total_amount >= 0', name='ck_sales_total'))
    op.create_index('ix_sales_orders_organization_id', 'sales_orders', ['organization_id'])
    op.create_index('ix_sales_orders_sold_at', 'sales_orders', ['sold_at'])
    op.create_table('sales_order_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_id', sa.String(36), sa.ForeignKey('sales_orders.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(16, 4), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(18, 2), nullable=False),
        sa.UniqueConstraint('order_id', 'product_id', name='uq_sales_item_product'),
        sa.CheckConstraint('quantity > 0 AND unit_price >= 0 AND total_amount >= 0', name='ck_sales_item_values'))
    op.create_index('ix_sales_order_items_order_id', 'sales_order_items', ['order_id'])
    op.create_table('sale_allocations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_item_id', sa.String(36), sa.ForeignKey('sales_order_items.id'), nullable=False),
        sa.Column('batch_id', sa.String(36), sa.ForeignKey('inventory_batches.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(16, 4), nullable=False),
        sa.UniqueConstraint('order_item_id', 'batch_id', name='uq_sale_item_batch'),
        sa.CheckConstraint('quantity > 0', name='ck_sale_allocation_quantity'))
    op.create_index('ix_sale_allocations_order_item_id', 'sale_allocations', ['order_item_id'])


def downgrade():
    for table in ('sale_allocations', 'sales_order_items', 'sales_orders'):
        op.drop_table(table)
