"""Confirmed demand calendars and model evaluation runs."""
from alembic import op
import sqlalchemy as sa
revision = '0005_planning'
down_revision = '0004_farm_sales'
branch_labels = depends_on = None


def upgrade():
    for name in ('demand_days', 'forecast_runs'):
        columns = [sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('location_id', sa.String(36), sa.ForeignKey('locations.id'), nullable=False),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False)]
        if name == 'demand_days':
            columns += [sa.Column('date', sa.Date(), nullable=False), sa.Column('quantity', sa.Numeric(16,4), nullable=False),
                sa.Column('stockout', sa.Boolean(), nullable=False), sa.Column('source', sa.String(200), nullable=False),
                sa.UniqueConstraint('organization_id','location_id','product_id','date',name='uq_demand_day'),
                sa.CheckConstraint('quantity >= 0',name='ck_demand_quantity')]
        else:
            columns += [sa.Column('route_id',sa.String(36),sa.ForeignKey('supply_routes.id'),nullable=False),
                sa.Column('status',sa.String(30),nullable=False),sa.Column('result',sa.JSON(),nullable=False)]
        op.create_table(name,*columns)
        op.create_index('ix_'+name+'_organization_id',name,['organization_id'])


def downgrade():
    op.drop_table('forecast_runs')
    op.drop_table('demand_days')
