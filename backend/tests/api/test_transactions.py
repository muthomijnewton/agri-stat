"""Tests for Transactions API endpoints."""
import pytest
from datetime import datetime, timedelta


def test_get_transactions_empty(client):
    """Test getting transactions when database is empty."""
    response = client.get("/api/transactions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_transaction(client, sample_product, sample_user, db):
    """Test creating a new transaction."""
    transaction_data = {
        "product_id": sample_product.id,
        "user_id": sample_user.id,
        "quantity": 20,
        "unit_price": 25.50,
        "total_price": 510.00,
        "transaction_date": "2026-04-06",
        "notes": "Bulk purchase"
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 20
    assert data["product_id"] == sample_product.id


def test_get_transaction_by_id(client, sample_transaction):
    """Test retrieving a transaction by ID."""
    response = client.get(f"/api/transactions/{sample_transaction.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_transaction.id
    assert data["quantity"] == 10


def test_get_transaction_not_found(client):
    """Test retrieving a non-existent transaction."""
    response = client.get("/api/transactions/999")
    assert response.status_code == 404


def test_update_transaction(client, sample_transaction):
    """Test updating a transaction."""
    update_data = {
        "quantity": 25,
        "total_price": 637.50
    }
    response = client.put(f"/api/transactions/{sample_transaction.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 25


def test_delete_transaction(client, sample_transaction):
    """Test deleting a transaction."""
    response = client.delete(f"/api/transactions/{sample_transaction.id}")
    assert response.status_code == 200
    
    # Verify transaction is deleted
    response = client.get(f"/api/transactions/{sample_transaction.id}")
    assert response.status_code == 404


def test_filter_transactions_by_product(client, sample_transaction, sample_product, sample_user, db):
    """Test filtering transactions by product_id."""
    response = client.get(f"/api/transactions?product_id={sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == sample_product.id


def test_filter_transactions_by_date_range(client, sample_transaction):
    """Test filtering transactions by date range."""
    response = client.get(
        "/api/transactions?start_date=2026-04-01&end_date=2026-04-30"
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1
