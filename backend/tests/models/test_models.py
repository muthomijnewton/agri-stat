"""Tests for database models."""
import pytest
from datetime import datetime
from app.models.models import User, Product, Transaction, Forecast, InventoryRecommendation


def test_user_model_creation(db):
    """Test User model creation and validation."""
    user = User(
        username="johndoe",
        email="john@example.com",
        password="hashed_password_123",
        full_name="John Doe",
        is_admin=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.username == "johndoe"
    assert user.email == "john@example.com"


def test_product_model_creation(db):
    """Test Product model creation."""
    product = Product(
        name="Tomato",
        category="Vegetables",
        description="Fresh red tomatoes",
        unit_price=15.50,
        unit="kg",
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    assert product.id is not None
    assert product.name == "Tomato"
    assert product.unit_price == 15.50


def test_product_soft_delete(db):
    """Test product soft delete functionality."""
    product = Product(
        name="Lettuce",
        category="Vegetables",
        unit_price=10.00,
        unit="kg",
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    product_id = product.id
    
    # Soft delete
    product.is_active = False
    db.commit()
    
    # Query only active products
    active_product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    assert active_product is None


def test_transaction_model_creation(db, sample_product, sample_user):
    """Test Transaction model creation."""
    transaction = Transaction(
        product_id=sample_product.id,
        user_id=sample_user.id,
        quantity=50,
        unit_price=25.50,
        total_price=1275.00,
        transaction_date="2026-04-06",
        notes="Bulk order"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    assert transaction.id is not None
    assert transaction.quantity == 50
    assert transaction.total_price == 1275.00


def test_transaction_relationships(db, sample_transaction):
    """Test Transaction relationships with Product and User."""
    transaction = db.query(Transaction).filter(
        Transaction.id == sample_transaction.id
    ).first()
    
    assert transaction.product is not None
    assert transaction.user is not None
    assert transaction.product.id == sample_transaction.product_id


def test_forecast_model_creation(db, sample_product):
    """Test Forecast model creation."""
    forecast = Forecast(
        product_id=sample_product.id,
        forecast_date="2026-04-20",
        predicted_demand=250,
        confidence_lower=200,
        confidence_upper=300,
        model_type="prophet",
        accuracy_score=0.94
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    
    assert forecast.id is not None
    assert forecast.predicted_demand == 250
    assert forecast.model_type == "prophet"


def test_inventory_recommendation_model_creation(db, sample_product):
    """Test InventoryRecommendation model creation."""
    recommendation = InventoryRecommendation(
        product_id=sample_product.id,
        recommended_quantity=700,
        current_quantity=200,
        min_quantity=100,
        max_quantity=1000,
        recommendation_date="2026-04-06",
        reason="Peak season preparation",
        status="pending"
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    
    assert recommendation.id is not None
    assert recommendation.status == "pending"
    assert recommendation.recommended_quantity == 700


def test_recommendation_status_workflow(db, sample_recommendation):
    """Test recommendation status workflow."""
    recommendation = sample_recommendation
    
    # Initial status should be pending
    assert recommendation.status == "pending"
    
    # Change to approved
    recommendation.status = "approved"
    db.commit()
    db.refresh(recommendation)
    assert recommendation.status == "approved"
    
    # Change to implemented
    recommendation.status = "implemented"
    db.commit()
    db.refresh(recommendation)
    assert recommendation.status == "implemented"


def test_model_timestamps(db, sample_product):
    """Test that model timestamps are created."""
    product = db.query(Product).filter(
        Product.id == sample_product.id
    ).first()
    
    assert product.created_at is not None
    assert product.updated_at is not None
