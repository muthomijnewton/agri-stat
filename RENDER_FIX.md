# Render Build Fix

This document explains why the backend build fails on Render's free tier when using the default `requirements.txt`, and how `requirements-render.txt` solves it.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full deployment guide.

---

## The Problem

The standard `backend/requirements.txt` includes Prophet and statsmodels:

```
prophet>=1.1.5
statsmodels>=0.14.0
pandas>=2.0.0
numpy>=1.26.0
```

Both Prophet and statsmodels compile C extensions from source during `pip install`. Render's free-tier build environment does not have the necessary system build tools and memory headroom to complete this compilation. The build fails with:

```
ERROR: Failed building wheel for statsmodels
```

or:

```
ERROR: Failed building wheel for pystan
```

This is a constraint of the free-tier build environment, not a bug in the code.

---

## The Solution

`backend/requirements-render.txt` is a stripped-down dependency list that includes only the packages needed for the API to run. It omits Prophet, statsmodels, pandas, and numpy.

**Contents of `requirements-render.txt`:**

```
fastapi>=0.100.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.18.0
psycopg2-binary>=2.9.11
pydantic[email]>=2.8.0
email-validator>=1.3.1
python-dotenv>=1.0.0
python-docx>=1.0.0
```

The `backend/render.yaml` file already points to this file:

```yaml
buildCommand: pip install -r backend/requirements-render.txt
```

No manual changes are needed. The `render.yaml` configuration is picked up automatically when you deploy via the Render dashboard or via the Render CLI.

---

## What Still Works on Render

All API functionality except real-time forecast generation continues to work:

| Feature                                   | Works on Render |
|-------------------------------------------|-----------------|
| Authentication (login, profile)           | Yes             |
| Products CRUD                             | Yes             |
| Transactions CRUD                         | Yes             |
| Recommendations CRUD, approve, implement  | Yes             |
| Stats and analytics endpoints             | Yes             |
| CSV exports                               | Yes             |
| Notifications                             | Yes             |
| Dashboard (reads stored data)             | Yes             |
| Viewing existing forecasts from database  | Yes             |
| Generating new forecasts (Prophet/ARIMA)  | No              |

Forecast data seeded by `init_db.py` is stored in the database and displays correctly on the frontend. The generate endpoints (`POST /api/forecasts/generate/{product_id}` and `POST /api/forecasts/generate-all`) will return an error in the Render deployment.

---

## Requirement File Reference

| File                        | Purpose                              | Use when                        |
|-----------------------------|--------------------------------------|---------------------------------|
| `requirements.txt`          | Full stack with ML libraries         | Local development               |
| `requirements-render.txt`   | Lightweight, no ML compilation       | Render deployment               |
| `requirements-prod.txt`     | Alternative production variant       | Other hosted environments       |

---

## Updating the Render Build Command

If the Render service was created manually without using `render.yaml`, update the build command in the Render dashboard:

1. Go to the `agric-stat-backend` service.
2. Click **Settings** > **Build & Deploy**.
3. Set **Build Command** to:
   ```
   pip install -r backend/requirements-render.txt
   ```
4. Click **Save Changes**.
5. Click **Manual Deploy** > **Deploy latest commit**.

---

## Enabling Forecasting on Render (Optional)

Forecasting can be restored in a Render deployment by one of these approaches:

**Upgrade the Render plan.** Paid plans (Standard, $7/month) have a more capable build environment that can compile statsmodels.

**Use Railway instead.** Railway's build environment handles Python ML libraries reliably on its free tier. The same `requirements.txt` works without modification.

**Pre-compute forecasts locally.** Run forecast generation locally against the production database, then leave the results in the database for the deployed frontend to display. This is the pattern the current deployment uses.

---

## Local Development

Local development is unaffected. Use the full requirements file:

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

All forecasting features are available locally, including Prophet and ARIMA generation endpoints.
