"""Adopt an existing legacy database, then apply additive versioned migrations."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect

ROOT = Path(__file__).resolve().parents[3]
LEGACY_TABLES = {"users", "products", "transactions", "forecasts", "inventory_recommendations", "notifications"}


def migrate_database(engine):
    config = Config(str(ROOT / "alembic.ini"))
    tables = set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        current = connection.exec_driver_sql("SELECT version_num FROM alembic_version").scalar() if "alembic_version" in tables else None
    if current == ScriptDirectory.from_config(config).get_current_head():
        return
    existing = LEGACY_TABLES & tables
    if current is None and existing and existing != LEGACY_TABLES:
        raise RuntimeError("Partial legacy schema found; repair it before migrating. No tables were modified.")
    if current is None and existing:
        # Refuse to stamp an unrelated database just because its table names match.
        expected = {
            "users": {"id", "username", "email", "password", "is_admin", "updated_at"},
            "products": {"id", "name", "unit", "unit_price", "is_active"},
            "transactions": {"id", "product_id", "quantity", "transaction_date"},
            "forecasts": {"id", "product_id", "forecast_date", "predicted_demand"},
            "inventory_recommendations": {"id", "product_id", "status"},
            "notifications": {"id", "title", "message", "read"},
        }
        inspector = inspect(engine)
        for table, columns in expected.items():
            if not columns <= {column["name"] for column in inspector.get_columns(table)}:
                raise RuntimeError(f"Unrecognized legacy schema in {table}; not stamping")
    if engine.dialect.name == "sqlite" and engine.url.database and engine.url.database != ":memory:" and tables:
        backups = ROOT / "work" / "backups"
        backups.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        destination = backups / f"before-phase1-{stamp}.db"
        with sqlite3.connect(engine.url.database) as source, sqlite3.connect(destination) as target:
            source.backup(target)
        destination.chmod(0o600)
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        if current is None and existing:
            command.stamp(config, "0001_initial")
        command.upgrade(config, "head")
