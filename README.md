# AgricStat Dash

AgricStat Dash is a full-stack platform for demand forecasting, inventory optimization, and operational analytics in agricultural supply chains. It is developed as part of INSY 492 (Senior Project, 2026) at the University of Eastern Africa, Baraton.

The repository contains a FastAPI backend, a React web frontend, and a Flutter mobile client.

---

## Table of Contents

- [Repository Layout](#repository-layout)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Backend](#backend)
- [Web Frontend](#web-frontend)
- [Mobile Client](#mobile-client)
- [API Reference](#api-reference)
- [Database](#database)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Origin](#project-origin)

---

## Repository Layout

```
agric-stat-dash/
├── backend/            FastAPI application (models, services, API endpoints)
│   ├── app/
│   │   ├── api/        Route registrations and endpoint modules
│   │   ├── core/       Configuration, security, rate limiting
│   │   ├── db/         Database session and connection setup
│   │   ├── models/     SQLAlchemy ORM models
│   │   ├── schemas/    Pydantic request/response schemas
│   │   └── services/   Forecasting and recommendation logic
│   ├── tests/          Pytest test suite
│   ├── init_db.py      Database initializer and sample data seeder
│   └── requirements.txt
├── web/                React frontend (Vite)
│   └── src/
│       ├── pages/      Dashboard, Products, Transactions, Forecasts,
│       │               Recommendations, Analytics, Profile, Login
│       ├── components/ NotificationBell, Paginator, RequireAuth
│       ├── services/   api.js — Axios instance and all API helpers
│       ├── context/    AuthContext
│       └── css/        Stylesheets
├── mobile/             Flutter mobile client
├── alembic/            Database migration scripts
├── .env.example        Root-level environment template
└── requirements.txt    Python dependencies (mirrors backend/requirements.txt)
```

---

## Technology Stack

### Backend

| Component   | Technology                       |
|-------------|----------------------------------|
| Framework   | FastAPI (Python 3.13)            |
| Server      | Uvicorn (ASGI)                   |
| ORM         | SQLAlchemy 2.0                   |
| Database    | SQLite (default) / PostgreSQL    |
| Migrations  | Alembic                          |
| Forecasting | Prophet, ARIMA via statsmodels   |
| Auth        | JWT (python-jose)                |
| API Docs    | Swagger / OpenAPI (auto-generated) |

### Frontend

| Component   | Technology           |
|-------------|----------------------|
| Framework   | React 18             |
| Build Tool  | Vite 5               |
| Routing     | React Router DOM 6   |
| HTTP Client | Axios                |
| Charts      | Recharts             |
| Styling     | CSS3 + CSS Variables |

### Database Tables

| Table                     | Purpose                              |
|---------------------------|--------------------------------------|
| users                     | User accounts and hashed credentials |
| products                  | Agricultural product inventory       |
| transactions              | Sales and purchase records           |
| forecasts                 | Demand forecast results              |
| inventory_recommendations | Computed stock level suggestions     |

---

## Quick Start

See [GET_STARTED.md](GET_STARTED.md) for platform-specific setup instructions (Windows, macOS, Linux).

**Short version (Linux/macOS):**

```bash
# 1. Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd web
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.  
API documentation: `http://localhost:8000/docs`

Default login: `admin` / `admin123` (created by `init_db.py`)

---

## Backend

The backend is a FastAPI application that exposes a REST API, handles authentication, runs forecasting models, and computes inventory recommendations.

Key source files:

- `backend/app/main.py` — application entry point, middleware, startup hook
- `backend/app/core/config.py` — all configuration (database URL, CORS origins, JWT secret, forecasting settings)
- `backend/app/api/routes.py` — router registration
- `backend/app/services/forecasting.py` — Prophet and ARIMA forecasting logic, recommendation calculations

See [backend/README.md](backend/README.md) for full backend documentation.

### Starting the Backend

```bash
cd backend
source venv/bin/activate         # Windows: venv\Scripts\activate
python init_db.py                # Creates tables and seeds sample data
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and set at minimum:

```env
SECRET_KEY=<output of: python -c "import secrets; print(secrets.token_hex(32))">
ALLOWED_ORIGINS=http://localhost:5173
```

Leave `DATABASE_URL` unset to use SQLite. Set it to a PostgreSQL URL for production.

---

## Web Frontend

The frontend is a React SPA located in `web/`. It communicates with the backend API and provides:

- Dashboard with KPI cards, revenue charts, and a low-stock alert banner
- Products management (add, view, soft-delete)
- Transactions (record, filter by date/product, CSV export)
- Forecasts (view Prophet/ARIMA predictions with confidence intervals, CSV export)
- Recommendations (generate single or batch, approve, implement, CSV export)
- Analytics page with transaction and forecast trend charts
- Profile page with password change

See [web/README.md](web/README.md) for frontend documentation.

### Starting the Frontend

```bash
cd web
npm install
npm run dev       # http://localhost:5173
npm run build     # production build → web/dist/
```

The frontend reads `VITE_API_URL` from `web/.env`. Default: `http://localhost:8000/api`.

---

## Mobile Client

The mobile client is a Flutter application in `mobile/`. It covers product browsing, transaction management, forecast viewing, and recommendation workflows on Android and iOS.

See `mobile/README.md` for setup and build instructions.

---

## API Reference

All endpoints are prefixed `/api`. Interactive documentation is available at `http://localhost:8000/docs` when the backend is running.

### Auth

```
POST   /api/auth/login          Authenticate, returns JWT token
GET    /api/auth/me             Current user profile
PATCH  /api/auth/me             Update profile / change password
```

### Products

```
GET    /api/products            List (paginated: skip, limit)
GET    /api/products/{id}       Get by ID
POST   /api/products            Create
PUT    /api/products/{id}       Update
DELETE /api/products/{id}       Soft delete
```

### Transactions

```
GET    /api/transactions        List (filters: product_id, start_date, end_date)
GET    /api/transactions/{id}   Get by ID
POST   /api/transactions        Record new transaction
PUT    /api/transactions/{id}   Update
DELETE /api/transactions/{id}   Delete
```

### Forecasts

```
GET    /api/forecasts                         List (filters: product_id)
GET    /api/forecasts/{id}                    Get by ID
POST   /api/forecasts                         Create manually
PUT    /api/forecasts/{id}                    Update
DELETE /api/forecasts/{id}                    Delete
POST   /api/forecasts/generate/{product_id}   Run forecast model for one product
POST   /api/forecasts/generate-all            Run forecast model for all products
```

### Recommendations

```
GET    /api/recommendations                        List (filters: status)
GET    /api/recommendations/{id}                   Get by ID
POST   /api/recommendations                        Create manually
PUT    /api/recommendations/{id}                   Update
DELETE /api/recommendations/{id}                   Delete
PATCH  /api/recommendations/{id}/approve           Transition: pending -> approved
PATCH  /api/recommendations/{id}/implement         Transition: approved -> implemented
POST   /api/recommendations/generate/{product_id}  Generate for one product
POST   /api/recommendations/generate-all           Generate for all products
```

### Stats / Analytics

```
GET    /api/stats/summary
GET    /api/stats/transactions-daily?days=30
GET    /api/stats/revenue-by-product?days=30
GET    /api/stats/transaction-type-split?days=30
GET    /api/stats/forecast-accuracy-trend?limit=20
GET    /api/stats/recommendation-status-breakdown
GET    /api/stats/top-products-by-quantity?days=30&limit=10
```

### Exports (CSV)

```
GET    /api/exports/transactions
GET    /api/exports/forecasts
GET    /api/exports/recommendations
```

### Notifications

```
GET    /api/notifications/
GET    /api/notifications/unread-count
PATCH  /api/notifications/{id}/read
PATCH  /api/notifications/read-all
```

---

## Database

The default database is SQLite stored at `backend/agric_stat.db`. No setup is required for local development.

To use PostgreSQL, set `DATABASE_URL` in `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/agric_stat_db
```

### Initialize / Reset

```bash
cd backend
source venv/bin/activate
python init_db.py          # Creates tables and seeds sample data
```

To reset to a clean state, delete `backend/agric_stat.db` and re-run `init_db.py`.

Sample data seeded on first run:

- 10 products (tomatoes, maize, beans, potatoes, etc.)
- 90 transactions across 30 days
- 20 demand forecasts
- 5 inventory recommendations

---

## Configuration

### Backend (`backend/.env`)

```env
# Database — leave unset to use SQLite
DATABASE_URL=postgresql://user:password@host:5432/agric_stat_db

# Server
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=False

# Security (required — generate a random value)
SECRET_KEY=replace-with-output-of-secrets-token-hex-32

# CORS — comma-separated list of allowed frontend origins
ALLOWED_ORIGINS=http://localhost:5173

# Forecasting
FORECAST_DAYS=30
FORECAST_MODEL=prophet
```

### Frontend (`web/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

---

## Testing

Run backend tests from the `backend/` directory:

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
pytest tests/ --cov=app        # with coverage
```

The test suite uses an in-memory SQLite database and does not require the server to be running.

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions to deploy the backend to Render and the frontend to Vercel using free-tier accounts.

For notes on working around build failures with heavy ML libraries on free-tier hosts, see [RENDER_FIX.md](RENDER_FIX.md).

---

## Project Origin

Developed as advanced applied software engineering research at the [University of Eastern Africa, Baraton](https://ueab.ac.ke) (INSY 492 Senior Project, 2026).

The platform is designed for practical deployment in agricultural supply chain contexts, not only as an academic demonstration.
