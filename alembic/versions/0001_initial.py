"""Initial schema - create all tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-26 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("profile_photo", sa.String(length=255), nullable=True),
        sa.Column("business_name", sa.String(length=255), nullable=True),
        sa.Column("business_type", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("county", sa.String(length=100), nullable=True),
        sa.Column("sub_county", sa.String(length=100), nullable=True),
        sa.Column("village", sa.String(length=100), nullable=True),
        sa.Column("farm_size", sa.String(length=100), nullable=True),
        sa.Column("primary_crop", sa.String(length=100), nullable=True),
        sa.Column("primary_livestock", sa.String(length=100), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # products
    # ------------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)

    # ------------------------------------------------------------------
    # transactions
    # ------------------------------------------------------------------
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(op.f("ix_transactions_product_id"), "transactions", ["product_id"], unique=False)
    op.create_index(op.f("ix_transactions_transaction_date"), "transactions", ["transaction_date"], unique=False)

    # ------------------------------------------------------------------
    # forecasts
    # ------------------------------------------------------------------
    op.create_table(
        "forecasts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("predicted_demand", sa.Integer(), nullable=False),
        sa.Column("confidence_lower", sa.Numeric(10, 2), nullable=True),
        sa.Column("confidence_upper", sa.Numeric(10, 2), nullable=True),
        sa.Column("model_type", sa.String(length=50), nullable=True),
        sa.Column("accuracy_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_forecasts_id"), "forecasts", ["id"], unique=False)
    op.create_index(op.f("ix_forecasts_product_id"), "forecasts", ["product_id"], unique=False)
    op.create_index(op.f("ix_forecasts_forecast_date"), "forecasts", ["forecast_date"], unique=False)

    # ------------------------------------------------------------------
    # inventory_recommendations
    # ------------------------------------------------------------------
    op.create_table(
        "inventory_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("recommended_quantity", sa.Integer(), nullable=False),
        sa.Column("current_quantity", sa.Integer(), nullable=True),
        sa.Column("min_quantity", sa.Integer(), nullable=True),
        sa.Column("max_quantity", sa.Integer(), nullable=True),
        sa.Column("recommendation_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_recommendations_id"), "inventory_recommendations", ["id"], unique=False)
    op.create_index(op.f("ix_inventory_recommendations_product_id"), "inventory_recommendations", ["product_id"], unique=False)
    op.create_index(op.f("ix_inventory_recommendations_recommendation_date"), "inventory_recommendations", ["recommendation_date"], unique=False)

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_inventory_recommendations_recommendation_date"), table_name="inventory_recommendations")
    op.drop_index(op.f("ix_inventory_recommendations_product_id"), table_name="inventory_recommendations")
    op.drop_index(op.f("ix_inventory_recommendations_id"), table_name="inventory_recommendations")
    op.drop_table("inventory_recommendations")

    op.drop_index(op.f("ix_forecasts_forecast_date"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_product_id"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_id"), table_name="forecasts")
    op.drop_table("forecasts")

    op.drop_index(op.f("ix_transactions_transaction_date"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_product_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_id"), table_name="transactions")
    op.drop_table("transactions")

    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
