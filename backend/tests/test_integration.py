"""Integration and general API tests."""
import pytest


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_api_cors_headers(client):
    """Test that CORS headers are present in responses."""
    response = client.get("/api/products")
    # Check for the CORS header from the middleware
    assert response.status_code == 200
    # The header might be in different cases or forms depending on CORS middleware
    headers_lower = {k.lower(): v for k, v in response.headers.items()}
    assert any("access-control" in k for k in headers_lower.keys())


def test_api_root_path(client):
    """Test API root path."""
    response = client.get("/api/")
    # Should return 404 or handle gracefully
    assert response.status_code in [200, 404, 405]


def test_invalid_endpoint(client):
    """Test accessing invalid endpoint."""
    response = client.get("/api/invalid-endpoint")
    assert response.status_code == 404


def test_concurrent_operations(client, sample_product, db):
    """Test handling concurrent operations across different endpoints."""
    responses = []
    
    # Simulate concurrent reads
    for _ in range(3):
        response = client.get(f"/api/products/{sample_product.id}")
        responses.append(response)
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # All should return the same data
    data = [r.json() for r in responses]
    assert all(d["id"] == sample_product.id for d in data)


def test_empty_post_request(client):
    """Test POST request with empty/invalid data."""
    response = client.post("/api/products", json={})
    assert response.status_code == 422  # Validation error


def test_malformed_json(client):
    """Test handling of malformed JSON."""
    response = client.post(
        "/api/products",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code in [400, 422]
