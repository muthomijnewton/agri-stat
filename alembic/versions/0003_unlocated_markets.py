"""Keep real market records when a publisher supplies no coordinates."""
from alembic import op
import sqlalchemy as sa

revision = "0003_unlocated_markets"
down_revision = "0002_foundation"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("locations") as batch:
        batch.alter_column("latitude", existing_type=sa.Numeric(10, 7), nullable=True)
        batch.alter_column("longitude", existing_type=sa.Numeric(10, 7), nullable=True)
        batch.alter_column("weather_grid_key", existing_type=sa.String(64), nullable=True)
        batch.create_check_constraint("ck_location_coordinates", "(latitude IS NOT NULL AND longitude IS NOT NULL AND weather_grid_key IS NOT NULL) OR (location_type = 'MARKET' AND latitude IS NULL AND longitude IS NULL AND weather_grid_key IS NULL)")


def downgrade():
    missing = op.get_bind().execute(sa.text("SELECT count(*) FROM locations WHERE latitude IS NULL")).scalar()
    if missing:
        raise RuntimeError("Provide coordinates for unlocated markets before downgrading")
    with op.batch_alter_table("locations") as batch:
        batch.drop_constraint("ck_location_coordinates", type_="check")
        batch.alter_column("latitude", existing_type=sa.Numeric(10, 7), nullable=False)
        batch.alter_column("longitude", existing_type=sa.Numeric(10, 7), nullable=False)
        batch.alter_column("weather_grid_key", existing_type=sa.String(64), nullable=False)
