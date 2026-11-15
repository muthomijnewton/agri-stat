import os
import sys

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend",
    )
)

sys.path.insert(0, BASE_DIR)


from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

from app.core.config import DATABASE_URL
from app.db.database import Base
from app.models import models, operations, planning

# Alembic Config object
config = context.config

# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all SQLAlchemy models
target_metadata = Base.metadata


# =====================================
# OFFLINE MIGRATIONS
# =====================================

def run_migrations_offline() -> None:
    """
    Run migrations without connecting to the database.
    """

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# =====================================
# ONLINE MIGRATIONS
# =====================================

def run_migrations_online() -> None:
    """
    Run migrations connected to the database.
    """

    supplied_connection = config.attributes.get("connection")
    if supplied_connection is not None:
        context.configure(connection=supplied_connection, target_metadata=target_metadata,
                          version_table_schema=config.attributes.get("version_table_schema"),
                          compare_type=True, render_as_batch=supplied_connection.dialect.name == "sqlite")
        with context.begin_transaction():
            context.run_migrations()
        return

    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# =====================================
# ENTRY POINT
# =====================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
