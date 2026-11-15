from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Date, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime
from app.models.foundation import DEFAULT_ORGANIZATION_ID

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False,
                             default=DEFAULT_ORGANIZATION_ID, server_default=DEFAULT_ORGANIZATION_ID, index=True)

    # ==========================
    # ACCOUNT INFORMATION
    # ==========================

    username = Column(String(80), unique=True, nullable=False, index=True)

    email = Column(String(120), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    full_name = Column(String(255))

    phone = Column(String(30))

    profile_photo = Column(String(255), nullable=True)

    # ==========================
    # BUSINESS INFORMATION
    # ==========================

    business_name = Column(String(255))

    business_type = Column(
        String(100),
        default="Farmer",
    )

    # ==========================
    # LOCATION
    # ==========================

    country = Column(
        String(100),
        default="Kenya",
    )

    county = Column(String(100))

    sub_county = Column(String(100))

    village = Column(String(100))

    # ==========================
    # FARM INFORMATION
    # ==========================

    farm_size = Column(String(100))

    primary_crop = Column(String(100))

    primary_livestock = Column(String(100))

    # ==========================
    # PREFERENCES
    # ==========================

    currency = Column(
        String(10),
        default="KES",
    )

    bio = Column(Text)

    # ==========================
    # ACCOUNT STATUS
    # ==========================

    is_admin = Column(
        Boolean,
        default=False,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # ==========================
    # RELATIONSHIPS
    # ==========================

    transactions = relationship(
        "Transaction",
        back_populates="user",
    )

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False,
                             default=DEFAULT_ORGANIZATION_ID, server_default=DEFAULT_ORGANIZATION_ID, index=True)
    sku = Column(String(100))
    shelf_life_days = Column(Integer)
    optimal_temp_min_c = Column(Numeric(8, 3))
    optimal_temp_max_c = Column(Numeric(8, 3))
    __table_args__ = (
        UniqueConstraint("organization_id", "sku", name="uq_product_org_sku"),
        CheckConstraint("shelf_life_days IS NULL OR shelf_life_days > 0", name="ck_product_shelf_life"),
    )
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100))
    description = Column(Text)
    unit_price = Column(Numeric(10, 2))
    unit = Column(String(50))  # kg, pieces, liters, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")
    inventory_recommendations = relationship("InventoryRecommendation", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(String(20), nullable=False, default="sale")  # 'sale' or 'purchase'
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_demand = Column(Integer, nullable=False)
    confidence_lower = Column(Numeric(10, 2))  # Lower confidence interval
    confidence_upper = Column(Numeric(10, 2))  # Upper confidence interval
    model_type = Column(String(50))  # 'prophet', 'arima', etc.
    accuracy_score = Column(Numeric(5, 2))  # MAPE, RMSE, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="forecasts")


class InventoryRecommendation(Base):
    __tablename__ = "inventory_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    recommended_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer)
    min_quantity = Column(Integer)  # Minimum safe stock level
    max_quantity = Column(Integer)  # Maximum storage capacity
    recommendation_date = Column(Date, nullable=False, index=True)
    reason = Column(Text)  # Why this recommendation was made
    status = Column(String(50), default="pending")  # pending, approved, implemented
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_recommendations")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="info")  # info, warning, danger, success
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
