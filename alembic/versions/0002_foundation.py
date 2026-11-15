"""Phase 1 foundation; additive migration preserving legacy product IDs."""
from alembic import op
import sqlalchemy as sa

revision = "0002_foundation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # Frozen schema snapshot: do not import application models into migrations.
    op.create_table('organizations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('locations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('location_type', sa.String(length=16), nullable=False),
    sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=False),
    sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=False),
    sa.Column('weather_grid_key', sa.String(length=64), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("location_type IN ('FARM','DEPOT','SHOP','MARKET')", name='ck_location_type'),
    sa.CheckConstraint('latitude BETWEEN -90 AND 90', name='ck_location_lat'),
    sa.CheckConstraint('longitude BETWEEN -180 AND 180', name='ck_location_lon'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_weather_grid_key'), 'locations', ['weather_grid_key'], unique=False)
    op.create_index(op.f('ix_locations_organization_id'), 'locations', ['organization_id'], unique=False)
    op.create_table('supply_routes',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('origin_location_id', sa.String(length=36), nullable=False),
    sa.Column('dest_location_id', sa.String(length=36), nullable=False),
    sa.Column('total_distance_km', sa.Numeric(precision=12, scale=3), nullable=True),
    sa.Column('unpaved_ratio', sa.Numeric(precision=7, scale=6), nullable=True),
    sa.Column('unknown_surface_ratio', sa.Numeric(precision=7, scale=6), nullable=True),
    sa.Column('base_lead_time_days', sa.Numeric(precision=10, scale=4), nullable=False),
    sa.Column('adjusted_lead_time_days', sa.Numeric(precision=10, scale=4), nullable=True),
    sa.Column('current_risk_level', sa.String(length=16), nullable=False),
    sa.Column('route_geometry', sa.JSON(), nullable=True),
    sa.Column('inspected_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('base_lead_time_days > 0', name='ck_route_lead_time'),
    sa.CheckConstraint('origin_location_id <> dest_location_id', name='ck_route_endpoints'),
    sa.CheckConstraint('unknown_surface_ratio BETWEEN 0 AND 1', name='ck_route_unknown'),
    sa.CheckConstraint('unpaved_ratio BETWEEN 0 AND 1', name='ck_route_unpaved'),
    sa.ForeignKeyConstraint(['dest_location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['origin_location_id'], ['locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supply_routes_organization_id'), 'supply_routes', ['organization_id'], unique=False)
    op.create_table('inventory_batches',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('location_id', sa.String(length=36), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('batch_code', sa.String(length=100), nullable=False),
    sa.Column('quantity_on_hand', sa.Numeric(precision=16, scale=4), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=16, scale=4), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('is_synthetic', sa.Boolean(), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('expires_at IS NULL OR expires_at > received_at', name='ck_batch_expiry'),
    sa.CheckConstraint('quantity_on_hand >= 0 AND unit_cost >= 0', name='ck_batch_nonnegative'),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'location_id', 'product_id', 'batch_code', name='uq_batch_code')
    )
    op.create_index(op.f('ix_inventory_batches_organization_id'), 'inventory_batches', ['organization_id'], unique=False)
    op.create_table('weather_observations',
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('weather_grid_key', sa.String(length=64), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('is_forecast', sa.Boolean(), nullable=False),
    sa.Column('rainfall_mm', sa.Numeric(precision=12, scale=4), nullable=True),
    sa.Column('temp_max_c', sa.Numeric(precision=8, scale=4), nullable=True),
    sa.Column('temp_min_c', sa.Numeric(precision=8, scale=4), nullable=True),
    sa.Column('soil_moisture_0_to_7cm', sa.Numeric(precision=10, scale=6), nullable=True),
    sa.Column('evapotranspiration_mm', sa.Numeric(precision=12, scale=4), nullable=True),
    sa.Column('source', sa.String(length=64), nullable=False),
    sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('organization_id', 'weather_grid_key', 'date', 'is_forecast')
    )
    op.create_table('import_runs',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('source', sa.String(length=32), nullable=False),
    sa.Column('source_url', sa.Text(), nullable=False),
    sa.Column('content_sha256', sa.String(length=64), nullable=False),
    sa.Column('row_count', sa.Integer(), nullable=False),
    sa.Column('imported_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_runs_organization_id'), 'import_runs', ['organization_id'], unique=False)
    op.create_table('market_observations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('location_id', sa.String(length=36), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('price', sa.Numeric(precision=16, scale=4), nullable=False),
    sa.Column('price_type', sa.String(length=32), nullable=False),
    sa.Column('currency', sa.String(length=8), nullable=False),
    sa.Column('base_unit', sa.String(length=16), nullable=False),
    sa.Column('volume', sa.Numeric(precision=16, scale=4), nullable=True),
    sa.Column('frequency', sa.String(length=16), nullable=False),
    sa.Column('source', sa.String(length=32), nullable=False),
    sa.Column('source_key', sa.String(length=64), nullable=False),
    sa.Column('import_run_id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['import_run_id'], ['import_runs.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'source_key', name='uq_market_source_key')
    )
    op.create_index(op.f('ix_market_observations_organization_id'), 'market_observations', ['organization_id'], unique=False)
    # ### end Alembic commands ###

    op.execute("INSERT INTO organizations (id, name, created_at) VALUES ('00000000-0000-0000-0000-000000000001', 'Local organization', CURRENT_TIMESTAMP)")
    for table in ("users", "products"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("organization_id", sa.String(36), server_default="00000000-0000-0000-0000-000000000001", nullable=False))
            batch.create_foreign_key("fk_" + table + "_organization", "organizations", ["organization_id"], ["id"])
            batch.create_index("ix_" + table + "_organization_id", ["organization_id"])
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("sku", sa.String(100)))
        batch.add_column(sa.Column("shelf_life_days", sa.Integer()))
        batch.add_column(sa.Column("optimal_temp_min_c", sa.Numeric(8, 3)))
        batch.add_column(sa.Column("optimal_temp_max_c", sa.Numeric(8, 3)))
        batch.create_unique_constraint("uq_product_org_sku", ["organization_id", "sku"])
        batch.create_check_constraint("ck_product_shelf_life", "shelf_life_days IS NULL OR shelf_life_days > 0")
    # The legacy initializer added this outside Alembic. Handle both paths.
    if "transaction_type" not in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("transactions")}:
        op.add_column("transactions", sa.Column("transaction_type", sa.String(20), server_default="sale", nullable=False))
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
        op.execute("ALTER TABLE locations ADD COLUMN geom geography(Point,4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude::double precision, latitude::double precision),4326)::geography) STORED")
        op.execute("CREATE INDEX ix_locations_geom ON locations USING GIST (geom)")
        op.execute("ALTER TABLE supply_routes ADD COLUMN route_geom geography(LineString,4326) GENERATED ALWAYS AS (CASE WHEN route_geometry IS NULL OR route_geometry::text = 'null' THEN NULL ELSE ST_SetSRID(ST_GeomFromGeoJSON(route_geometry::text),4326)::geography END) STORED")
        op.execute("CREATE INDEX ix_supply_routes_geom ON supply_routes USING GIST (route_geom)")
        op.execute("SELECT create_hypertable('weather_observations', 'date', chunk_time_interval => INTERVAL '30 days', if_not_exists => TRUE)")


def downgrade():
    # This removes Phase 1 data; keep the old transaction_type compatibility fix.
    for table in ("market_observations", "import_runs", "weather_observations", "inventory_batches", "supply_routes", "locations"):
        op.drop_table(table)
    with op.batch_alter_table("products") as batch:
        batch.drop_constraint("uq_product_org_sku", type_="unique")
        batch.drop_constraint("ck_product_shelf_life", type_="check")
        for name in ("sku", "shelf_life_days", "optimal_temp_min_c", "optimal_temp_max_c"):
            batch.drop_column(name)
    for table in ("products", "users"):
        with op.batch_alter_table(table) as batch:
            batch.drop_constraint("fk_" + table + "_organization", type_="foreignkey")
            batch.drop_index("ix_" + table + "_organization_id")
            batch.drop_column("organization_id")
    op.drop_table("organizations")
