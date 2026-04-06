"""Tests for Forecasts API endpoints."""
import pytest


def test_get_forecasts_empty(client):
    """Test getting forecasts when database is empty."""
    response = client.get("/api/forecasts")
    assert response.status_code == 200
    assert response.json() == []


def test_create_forecast(client, sample_product, db):
    """Test creating a new forecast."""
    forecast_data = {
        "product_id": sample_product.id,
        "forecast_date": "2026-04-20",
        "predicted_demand": 200,
        "confidence_lower": 160,
        "confidence_upper": 240,
        "model_type": "arima",
        "accuracy_score": 0.88
    }
    response = client.post("/api/forecasts", json=forecast_data)
    assert response.status_code == 201
    data = response.json()
    assert data["predicted_demand"] == 200
    assert data["model_type"] == "arima"


def test_get_forecast_by_id(client, sample_forecast):
    """Test retrieving a forecast by ID."""
    response = client.get(f"/api/forecasts/{sample_forecast.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_forecast.id
    assert data["predicted_demand"] == 150


def test_get_forecast_not_found(client):
    """Test retrieving a non-existent forecast."""
    response = client.get("/api/forecasts/999")
    assert response.status_code == 404


def test_get_forecasts_by_product(client, sample_forecast, sample_product):
    """Test retrieving forecasts for a specific product."""
    response = client.get(f"/api/forecasts/product/{sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["product_id"] == sample_product.id


def test_update_forecast(client, sample_forecast):
    """Test updating a forecast."""
    update_data = {
        "predicted_demand": 175,
        "accuracy_score": 0.95
    }
    response = client.put(f"/api/forecasts/{sample_forecast.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_demand"] == 175
    assert data["accuracy_score"] == 0.95


def test_delete_forecast(client, sample_forecast):
    """Test deleting a forecast."""
    response = client.delete(f"/api/forecasts/{sample_forecast.id}")
    assert response.status_code == 200
    
    # Verify forecast is deleted
    response = client.get(f"/api/forecasts/{sample_forecast.id}")
    assert response.status_code == 404
