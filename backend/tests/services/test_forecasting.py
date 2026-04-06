"""Tests for the Forecasting Service."""
import pytest
from datetime import datetime, timedelta
from app.services.forecasting import ForecastingService
from app.models.models import Product, Transaction, User
import pandas as pd


@pytest.fixture
def forecasting_service():
    """Create a forecasting service instance."""
    return ForecastingService()


@pytest.fixture
def product_with_transactions(db):
    """Create a product with sample transaction history."""
    product = Product(
        name="Test Wheat",
        category="Grains",
        unit_price=20.00,
        unit="kg",
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed",
        full_name="Test",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add transactions across 30 days
    base_date = datetime.now()
    for i in range(30):
        transaction_date = (base_date - timedelta(days=30-i)).strftime("%Y-%m-%d")
        transaction = Transaction(
            product_id=product.id,
            user_id=user.id,
            quantity=100 + (i * 2),  # Increasing trend
            unit_price=20.00,
            total_price=(100 + i * 2) * 20.00,
            transaction_date=transaction_date,
            notes="Test transaction"
        )
        db.add(transaction)
    
    db.commit()
    return product


def test_get_transaction_history(db, forecasting_service, product_with_transactions):
    """Test retrieving transaction history for a product."""
    history = forecasting_service.get_transaction_history(
        db, product_with_transactions.id
    )
    
    assert len(history) > 0
    assert "date" in history.columns
    assert "quantity" in history.columns


def test_calculate_inventory_recommendation(forecasting_service):
    """Test inventory recommendation calculation."""
    avg_daily_demand = 50  # units per day
    lead_time = 3  # days
    safety_factor = 1.5
    
    recommendation = forecasting_service.calculate_inventory_recommendation(
        avg_daily_demand, lead_time, safety_factor
    )
    
    # Formula: Avg Daily Demand × Lead Time × Safety Factor
    expected = 50 * 3 * 1.5
    assert recommendation == expected


def test_calculate_inventory_recommendation_with_different_params(forecasting_service):
    """Test inventory recommendation with various parameters."""
    test_cases = [
        (100, 5, 1.0, 500),     # (demand, lead_time, factor, expected)
        (75, 2, 2.0, 300),
        (150, 7, 1.2, 1260),
    ]
    
    for demand, lead_time, factor, expected in test_cases:
        result = forecasting_service.calculate_inventory_recommendation(
            demand, lead_time, factor
        )
        assert result == expected


def test_prophet_forecast_basic(db, forecasting_service, product_with_transactions):
    """Test Prophet forecast generation."""
    history = forecasting_service.get_transaction_history(
        db, product_with_transactions.id
    )
    
    if len(history) >= 10:  # Prophet needs minimum historical data
        forecast = forecasting_service.forecast_prophet(history)
        
        assert "forecast" in forecast
        assert "accuracy" in forecast
        assert len(forecast["forecast"]) > 0
        assert 0 <= forecast["accuracy"] <= 1


def test_arima_forecast_basic(db, forecasting_service, product_with_transactions):
    """Test ARIMA forecast generation."""
    history = forecasting_service.get_transaction_history(
        db, product_with_transactions.id
    )
    
    if len(history) >= 10:
        forecast = forecasting_service.forecast_arima(history)
        
        assert "forecast" in forecast
        assert "accuracy" in forecast
        assert len(forecast["forecast"]) > 0
        assert 0 <= forecast["accuracy"] <= 1


def test_forecast_with_insufficient_data(db, forecasting_service):
    """Test forecasting with insufficient historical data."""
    # Create product with minimal data
    product = Product(
        name="New Product",
        category="Test",
        unit_price=10.00,
        unit="kg",
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    history = forecasting_service.get_transaction_history(db, product.id)
    
    # Should return empty or handle gracefully
    assert len(history) == 0
