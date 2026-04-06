"""Tests for Products API endpoints."""
import pytest
from app.models.models import Product


def test_get_products_empty(client):
    """Test getting products when database is empty."""
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client, db):
    """Test creating a new product."""
    product_data = {
        "name": "Maize",
        "category": "Grains",
        "description": "Yellow maize",
        "unit_price": 30.00,
        "unit": "kg"
    }
    response = client.post("/api/products", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Maize"
    assert float(data["unit_price"]) == 30.00
    assert data["is_active"] is True


def test_get_product_by_id(client, sample_product):
    """Test retrieving a product by ID."""
    response = client.get(f"/api/products/{sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["name"] == "Test Rice"


def test_get_product_not_found(client):
    """Test retrieving a non-existent product."""
    response = client.get("/api/products/999")
    assert response.status_code == 404


def test_update_product(client, sample_product):
    """Test updating a product."""
    update_data = {
        "name": "Premium Rice",
        "unit_price": 35.00
    }
    response = client.put(f"/api/products/{sample_product.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Premium Rice"
    assert float(data["unit_price"]) == 35.00


def test_delete_product(client, sample_product):
    """Test deleting a product (soft delete via is_active flag)."""
    response = client.delete(f"/api/products/{sample_product.id}")
    assert response.status_code == 204
    
    # Verify product is soft-deleted
    response = client.get(f"/api/products/{sample_product.id}")
    assert response.status_code == 404


def test_get_products_with_pagination(client, db):
    """Test getting products with pagination."""
    # Create 5 products
    for i in range(5):
        product = Product(
            name=f"Product {i}",
            category="Test",
            unit_price=10.00 + i,
            unit="kg",
            is_active=True
        )
        db.add(product)
    db.commit()
    
    # Test pagination
    response = client.get("/api/products?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    response = client.get("/api/products?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
