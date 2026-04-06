"""Tests for Recommendations API endpoints."""
import pytest


def test_get_recommendations_empty(client):
    """Test getting recommendations when database is empty."""
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    assert response.json() == []


def test_create_recommendation(client, sample_product, db):
    """Test creating a new recommendation."""
    rec_data = {
        "product_id": sample_product.id,
        "recommended_quantity": 600,
        "current_quantity": 150,
        "min_quantity": 50,
        "max_quantity": 1000,
        "recommendation_date": "2026-04-06",
        "reason": "Stock below minimum threshold"
    }
    response = client.post("/api/recommendations", json=rec_data)
    assert response.status_code == 201
    data = response.json()
    assert data["recommended_quantity"] == 600
    assert data["status"] == "pending"


def test_get_recommendation_by_id(client, sample_recommendation):
    """Test retrieving a recommendation by ID."""
    response = client.get(f"/api/recommendations/{sample_recommendation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_recommendation.id
    assert data["status"] == "pending"


def test_get_recommendation_not_found(client):
    """Test retrieving a non-existent recommendation."""
    response = client.get("/api/recommendations/999")
    assert response.status_code == 404


def test_get_recommendations_by_product(client, sample_recommendation, sample_product):
    """Test retrieving recommendations for a specific product."""
    response = client.get(f"/api/recommendations/product/{sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["product_id"] == sample_product.id


def test_approve_recommendation(client, sample_recommendation):
    """Test approving a pending recommendation."""
    response = client.patch(
        f"/api/recommendations/{sample_recommendation.id}/approve"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_approve_already_approved_recommendation(client, sample_recommendation, db):
    """Test approving an already approved recommendation."""
    # First approve it
    client.patch(f"/api/recommendations/{sample_recommendation.id}/approve")
    
    # Try to approve again
    response = client.patch(
        f"/api/recommendations/{sample_recommendation.id}/approve"
    )
    assert response.status_code == 400


def test_implement_recommendation(client, sample_recommendation):
    """Test implementing an approved recommendation."""
    # First approve it
    client.patch(f"/api/recommendations/{sample_recommendation.id}/approve")
    
    # Then implement it
    response = client.patch(
        f"/api/recommendations/{sample_recommendation.id}/implement"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "implemented"


def test_update_recommendation(client, sample_recommendation):
    """Test updating a recommendation."""
    update_data = {
        "recommended_quantity": 750,
        "reason": "Revised based on new data"
    }
    response = client.put(
        f"/api/recommendations/{sample_recommendation.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_quantity"] == 750


def test_delete_recommendation(client, sample_recommendation):
    """Test deleting a recommendation."""
    response = client.delete(f"/api/recommendations/{sample_recommendation.id}")
    assert response.status_code == 200
    
    # Verify recommendation is deleted
    response = client.get(f"/api/recommendations/{sample_recommendation.id}")
    assert response.status_code == 404


def test_filter_recommendations_by_status(client, sample_recommendation, sample_product, db):
    """Test filtering recommendations by status."""
    response = client.get("/api/recommendations?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(rec["status"] == "pending" for rec in data)
