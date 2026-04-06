# Backend Testing Guide

## Overview

The backend test suite provides comprehensive testing coverage for the Agricultural Statistics Dashboard API. It includes:

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test API endpoints and database interactions
- **Model Tests**: Verify ORM model creation and relationships
- **Service Tests**: Test business logic (forecasting, calculations)

## Test Statistics

- **Total Tests**: 55
- **Passing**: 25+
- **Coverage Areas**: Products, Transactions, Forecasts, Recommendations, Models, Services

## Running Tests

### Prerequisites

Make sure you're in the backend directory:

```bash
cd backend
```

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/api/test_products.py -v
```

### Run Specific Test

```bash
python -m pytest tests/api/test_products.py::test_create_product -v
```

### Run Tests with Coverage Report

```bash
python -m pytest tests/ -v --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests and Show Output

```bash
python -m pytest tests/ -v -s
```

The `-s` flag shows all print statements and logging output.

## Test Structure

### Fixtures (`conftest.py`)

The test suite uses pytest fixtures for common setup:

- **`engine`**: Creates a fresh SQLite test database for each test
- **`db_session`**: Provides a database session
- **`client`**: FastAPI test client with overridden dependencies
- **`sample_product`**: Pre-created product for testing
- **`sample_user`**: Pre-created user for testing
- **`sample_transaction`**: Pre-created transaction for testing
- **`sample_forecast`**: Pre-created forecast for testing
- **`sample_recommendation`**: Pre-created recommendation for testing

### Test Files

- **`tests/api/`**: API endpoint tests
  - `test_products.py`: Product CRUD operations
  - `test_transactions.py`: Transaction management
  - `test_forecasts.py`: Forecast generation and retrieval
  - `test_recommendations.py`: Inventory recommendations

- **`tests/models/`**: Database model tests
  - `test_models.py`: ORM model creation, relationships, and timestamps

- **`tests/services/`**: Business logic tests
  - `test_forecasting.py`: Forecasting algorithms and calculations

- **`test_integration.py`**: Integration and general API tests

## Common Test Patterns

### Testing API Endpoints

```python
def test_get_products(client):
    """Test retrieving products."""
    response = client.get("/api/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Testing with Fixtures

```python
def test_create_transaction(client, sample_product, sample_user):
    """Test creating a transaction."""
    transaction_data = {
        "product_id": sample_product.id,
        "user_id": sample_user.id,
        "quantity": 10,
        "unit_price": 25.50,
        "total_price": 255.00,
        "transaction_date": "2026-04-06"
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 201
```

## Test Status and Known Issues

### Passing Tests (25+)

✅ Product CRUD operations  
✅ Basic transaction operations  
✅ User model creation  
✅ Database table creation  
✅ Health check endpoint  
✅ Pagination  
✅ Basic forecasts  

### Areas for Improvement

⚠️ Foreign key constraint handling in certain edge cases  
⚠️ Complex filtering sometimes requires additional setup  
⚠️ Some service tests need more historical data  

## Debugging Tests

### View Database Contents During Test

```python
def test_debug(db_session):
    """Debug test to inspect database."""
    from sqlalchemy import inspect
    
    inspector = inspect(db_session.get_bind())
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    # Query data
    products = db_session.query(Product).all()
    print(f"Products: {products}")
```

### View HTTP Responses

```python
def test_debug_response(client):
    """Debug HTTP responses."""
    response = client.get("/api/products")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.json()}")
```

## Performance Notes

- Tests run in ~2-3 seconds
- Each test gets its own fresh database
- Uses file-based SQLite for proper isolation
- No external services required

## Continuous Integration

To run tests in CI/CD pipelines:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=xml --cov-report=term

# Exit with error code if coverage below threshold
python -m pytest tests/ --cov=app --cov-fail-under=70
```

## Contributing

When adding new tests:

1. Create test in appropriate file (`test_*.py`)
2. Use descriptive test names
3. Include docstrings
4. Use fixtures for common setup
5. Test both success and error cases

Example:

```python
def test_get_product_not_found(client):
    """Test retrieving a non-existent product returns 404."""
    response = client.get("/api/products/99999")
    assert response.status_code == 404
```
