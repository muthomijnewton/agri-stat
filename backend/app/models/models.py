from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
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
