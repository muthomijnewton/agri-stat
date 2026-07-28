# Backend

FastAPI application for AgricStat Dash. Provides a REST API for authentication, products, transactions, demand forecasting, inventory recommendations, statistics, CSV exports, and notifications.

For project-level setup and running instructions see [GET_STARTED.md](../GET_STARTED.md).  
For deployment see [DEPLOYMENT.md](../DEPLOYMENT.md).  
For the web frontend see [web/README.md](../web/README.md).

---

## Table of Contents

- [Technology Stack](#technology-stack)
- [Directory Layout](#directory-layout)
- [Setup](#setup)
- [Configuration](#configuration)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Forecasting and Recommendations](#forecasting-and-recommendations)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Testing](#testing)

---

## Technology Stack

| Component     | Package                  | Version    |
|---------------|--------------------------|------------|
| Framework     | FastAPI                  | 0.104+     |
| Server        | Uvicorn                  | 0.24+      |
| ORM           | SQLAlchemy               | 2.0+       |
| Migrations    | Alembic                  | 1.18+      |
| Database      | SQLite (dev) / PostgreSQL (prod) | — |
| Validation    | Pydantic                 | 2.8+       |
| Auth          | PyJWT + passlib[bcrypt]  | 2.8 / 1.7.4 |
| Forecasting   | Prophet, statsmodels     | 1.1.5+, 0.14+ |
| Rate limiting | SlowAPI                  | 0.1.9      |
| Testing       | pytest, httpx            | 8.0+ / 0.23 |

---

## Directory Layout

```
backend/
├── app/
│   ├── main.py                 Application entry point, middleware, lifespan handler
│   ├── api/
│   │   ├── routes.py           Registers all endpoint routers under api_router
│   │   └── endpoints/
│   │       ├── auth.py         POST /api/auth/login, GET/PATCH /api/auth/me
│   │       ├── products.py     CRUD /api/products
│   │       ├── transactions.py CRUD /api/transactions
│   │       ├── forecasts.py    CRUD + generate /api/forecasts
│   │       ├── recommendations.py  CRUD + workflow /api/recommendations
│   │       ├── stats.py        GET /api/stats/*
│   │       ├── exports.py      GET /api/exports/* (CSV downloads)
│   │       ├── notifications.py  /api/notifications
│   │       └── downloads.py    File download helpers
│   ├── core/
│   │   ├── config.py           All settings: DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS,
│   │   │                       FORECAST_DAYS, FORECAST_MODEL, DEBUG
│   │   ├── security.py         Password hashing (bcrypt), JWT create/verify
│   │   └── limiter.py          SlowAPI limiter instance
│   ├── db/
│   │   └── database.py         SQLAlchemy engine and session factory
│   ├── models/
│   │   └── models.py           ORM models: User, Product, Transaction, Forecast,
│   │                           InventoryRecommendation, Notification
│   ├── schemas/
│   │   └── schemas.py          Pydantic request/response schemas for all models
│   └── services/
│       └── forecasting.py      Prophet and ARIMA forecast logic, recommendation calculation
├── tests/
│   ├── conftest.py             Pytest fixtures: test DB, test client, sample objects
│   ├── api/
│   │   ├── test_products.py
│   │   ├── test_transactions.py
│   │   ├── test_forecasts.py
│   │   └── test_recommendations.py
│   ├── models/
│   │   └── test_models.py
│   ├── services/
│   │   └── test_forecasting.py
│   └── test_integration.py
├── init_db.py                  Schema creation + sample data seeder
├── requirements.txt            Full dependencies (local development, includes ML)
├── requirements-render.txt     Lightweight (Render free tier, excludes ML)
├── requirements-prod.txt       Alternative production variant
├── render.yaml                 Render.com deployment config
├── pytest.ini                  Pytest configuration
└── .env.example                Environment variable template
```

---

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation is available at `http://localhost:8000/docs` once the server is running.

### Environment file

Copy the example and fill in required values:

```bash
cp .env.example .env
```

The only required variable is `SECRET_KEY`. The application will raise a `RuntimeError` at startup if it is missing or left as the placeholder:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Configuration

All configuration is in `app/core/config.py`, which reads from environment variables (loaded from `backend/.env` if present).

| Variable         | Required | Default                           | Description                                               |
|------------------|----------|-----------------------------------|-----------------------------------------------------------|
| `SECRET_KEY`     | Yes      | —                                 | JWT signing key. Must be a random hex string.             |
| `DATABASE_URL`   | No       | `sqlite:///backend/agric_stat.db` | SQLite (omit) or PostgreSQL connection string.            |
| `ALLOWED_ORIGINS`| No       | localhost ports 3000, 5173, 8080  | Comma-separated CORS origins.                             |
| `DEBUG`          | No       | `False`                           | Enables SQLAlchemy echo when `true`.                      |
| `BACKEND_HOST`   | No       | `127.0.0.1`                       | Bind address (for reference; set in the uvicorn command). |
| `BACKEND_PORT`   | No       | `8000`                            | Port (for reference; set in the uvicorn command).         |
| `FORECAST_DAYS`  | No       | `30`                              | Number of days to forecast ahead.                         |
| `FORECAST_MODEL` | No       | `prophet`                         | Default model: `prophet` or `arima`.                     |

For PostgreSQL, note that `postgres://` URLs are automatically normalized to `postgresql://` (required by SQLAlchemy 2).

---

## Database

### Models

| Table                     | Key columns                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------|
| `users`                   | id, username, email, password (bcrypt), full_name, is_admin, is_active                         |
| `products`                | id, name, category, unit, unit_price, is_active (soft delete)                                  |
| `transactions`            | id, product_id, user_id, transaction_type (sale/purchase), quantity, unit_price, total_price, transaction_date |
| `forecasts`               | id, product_id, forecast_date, predicted_demand, confidence_lower, confidence_upper, model_type, accuracy_score |
| `inventory_recommendations`| id, product_id, recommended_quantity, current_quantity, min_quantity, max_quantity, status (pending/approved/implemented) |
| `notifications`           | id, title, message, type (info/warning/danger/success), read                                   |

### Initialize / Reset

```bash
# From backend/ with venv activated
python init_db.py
```

This runs at startup automatically via the lifespan handler in `main.py`. It is safe to run multiple times — it skips seeding if data already exists.

To reset to a clean state:

```bash
rm agric_stat.db          # macOS/Linux
del agric_stat.db         # Windows
python init_db.py
```

### Migrations

Alembic is configured for schema migrations. The initial migration is in `alembic/versions/0001_initial.py`.

```bash
# From the repository root
alembic upgrade head
```

For local SQLite development, `init_db.py` is simpler and does not require running Alembic.

---

## API Endpoints

All routes are registered under `/api`. Full interactive documentation: `http://localhost:8000/docs`.

### Auth

```
POST   /api/auth/login     Body: { username, password }  →  { access_token, token_type }
GET    /api/auth/me        Returns current user profile
PATCH  /api/auth/me        Update profile or change password
```

### Products

```
GET    /api/products               Query: skip, limit
GET    /api/products/{id}
POST   /api/products
PUT    /api/products/{id}
DELETE /api/products/{id}          Soft delete (sets is_active=false)
```

### Transactions

```
GET    /api/transactions           Query: skip, limit, product_id, start_date, end_date
GET    /api/transactions/{id}
POST   /api/transactions
PUT    /api/transactions/{id}
DELETE /api/transactions/{id}
```

### Forecasts

```
GET    /api/forecasts              Query: skip, limit, product_id
GET    /api/forecasts/{id}
POST   /api/forecasts
PUT    /api/forecasts/{id}
DELETE /api/forecasts/{id}
POST   /api/forecasts/generate/{product_id}   Query: model (prophet|arima|auto)
POST   /api/forecasts/generate-all            Query: model (prophet|arima|auto)
```

### Recommendations

```
GET    /api/recommendations        Query: skip, limit, status
GET    /api/recommendations/{id}
POST   /api/recommendations
PUT    /api/recommendations/{id}
DELETE /api/recommendations/{id}
PATCH  /api/recommendations/{id}/approve      pending -> approved
PATCH  /api/recommendations/{id}/implement    approved -> implemented
POST   /api/recommendations/generate/{product_id}
POST   /api/recommendations/generate-all
```

### Stats

```
GET    /api/stats/summary
GET    /api/stats/transactions-daily           Query: days (default 30)
GET    /api/stats/revenue-by-product           Query: days (default 30)
GET    /api/stats/transaction-type-split       Query: days (default 30)
GET    /api/stats/forecast-accuracy-trend      Query: limit (default 20)
GET    /api/stats/recommendation-status-breakdown
GET    /api/stats/top-products-by-quantity     Query: days, limit
```

### Exports (CSV)

```
GET    /api/exports/transactions               Query: product_id, start_date, end_date
GET    /api/exports/forecasts                  Query: product_id
GET    /api/exports/recommendations            Query: status
```

### Notifications

```
GET    /api/notifications/
GET    /api/notifications/unread-count
PATCH  /api/notifications/{id}/read
PATCH  /api/notifications/read-all
```

### Health

```
GET    /health
GET    /api/health
```

---

## Forecasting and Recommendations

Forecast generation is in `app/services/forecasting.py`.

### How forecasts are generated

1. The endpoint retrieves the product's historical transaction data.
2. If `model=auto`, it selects Prophet when sufficient data is available, falling back to ARIMA.
3. The selected model is fitted and generates `FORECAST_DAYS` daily predictions.
4. Results (predicted demand, confidence interval, MAPE) are stored in the `forecasts` table.

### How recommendations are calculated

The recommendation formula uses the forecast to compute a reorder quantity:

```
avg_daily_demand = mean of predicted_demand over forecast period
recommended_quantity = avg_daily_demand × lead_time_days × safety_factor
```

Where `lead_time_days = 3` and `safety_factor = 1.5` (hardcoded in `forecasting.py`).

The `min_quantity` field on the recommendation stores the safety stock floor. The low-stock banner on the dashboard flags products where `current_quantity < min_quantity`.

### Availability

Prophet and statsmodels are included in `requirements.txt` (local development). They are excluded from `requirements-render.txt` (Render free tier). See [RENDER_FIX.md](../RENDER_FIX.md) for details.

---

## Authentication

Passwords are hashed with bcrypt via passlib. JWT tokens are issued on login and verified on protected endpoints.

Key files:
- `app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`
- `app/api/endpoints/auth.py` — login endpoint, current-user dependency

Protected endpoints use a `Depends(get_current_user)` dependency that extracts and validates the JWT from the `Authorization: Bearer <token>` header.

---

## Rate Limiting

SlowAPI middleware is applied globally. Individual endpoints can add `@limiter.limit("X/minute")` decorators. The limiter instance is in `app/core/limiter.py`. Exceeded limits return HTTP 429 with a JSON error body.

---

## Testing

The test suite uses pytest with an in-memory SQLite database. No running backend or network access is required.

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

Test fixtures are defined in `tests/conftest.py`. Each test gets an isolated database session.

To run a single file or test:

```bash
pytest tests/api/test_products.py -v
pytest tests/api/test_products.py::test_create_product -v
```

For coverage HTML report:

```bash
pytest tests/ --cov=app --cov-report=html
# Report at: htmlcov/index.html
```
