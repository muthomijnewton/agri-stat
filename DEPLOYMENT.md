# Deployment

This guide covers deploying AgricStat Dash using free-tier services: the FastAPI backend to Render and the React frontend to Vercel. Both services auto-deploy from GitHub on every push to `main`.

For local development setup, see [GET_STARTED.md](GET_STARTED.md).  
For notes on build failures caused by heavy ML libraries, see [RENDER_FIX.md](RENDER_FIX.md).

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1 — Push to GitHub](#step-1--push-to-github)
- [Step 2 — Deploy Backend to Render](#step-2--deploy-backend-to-render)
- [Step 3 — Deploy Frontend to Vercel](#step-3--deploy-frontend-to-vercel)
- [Step 4 — Connect Frontend and Backend](#step-4--connect-frontend-and-backend)
- [Deployment Checklist](#deployment-checklist)
- [Free Tier Limits](#free-tier-limits)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## Overview

| Component | Service    | Notes                                    |
|-----------|------------|------------------------------------------|
| Backend   | Render     | FastAPI + Uvicorn, Python 3.11           |
| Database  | Render     | Managed PostgreSQL (free tier, 90 days)  |
| Frontend  | Vercel     | React + Vite, static CDN hosting         |

Estimated setup time: 25–35 minutes.

---

## Prerequisites

- GitHub account with the repository pushed
- Render account — https://render.com (free, sign up with GitHub)
- Vercel account — https://vercel.com (free, sign up with GitHub)

---

## Step 1 — Push to GitHub

If not already on GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<username>/agric-stat-dash.git
git branch -M main
git push -u origin main
```

Confirm these files are present before deploying:

- `backend/requirements-render.txt` — lightweight dependency list (excludes Prophet/statsmodels)
- `backend/render.yaml` — Render service configuration
- `web/package.json` — frontend dependencies
- `web/vite.config.js` — Vite build configuration

---

## Step 2 — Deploy Backend to Render

### 2a. Create the PostgreSQL database

1. Log in to https://render.com.
2. Click **New +** > **PostgreSQL**.
3. Fill in:
   - Name: `agric-stat-db`
   - Region: closest to your users
   - Plan: **Free**
4. Click **Create Database**.
5. On the database info page, copy the **Internal Database URL**. You will need it in the next step.

### 2b. Create the web service

1. Click **New +** > **Web Service**.
2. Connect your GitHub repository.
3. Fill in:
   - Name: `agric-stat-backend`
   - Environment: **Python**
   - Build Command: `pip install -r backend/requirements-render.txt`
   - Start Command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Plan: **Free**
4. Under **Environment Variables**, add:

   | Key               | Value                                        |
   |-------------------|----------------------------------------------|
   | `DATABASE_URL`    | Internal Database URL from step 2a           |
   | `SECRET_KEY`      | Output of `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `PYTHONUNBUFFERED`| `true`                                       |
   | `DEBUG`           | `false`                                      |
   | `ALLOWED_ORIGINS` | Set after getting Vercel URL (step 4)        |

5. Click **Create Web Service**.
6. Wait for the first deployment to complete (2–4 minutes). Watch the **Logs** tab for errors.
7. Once deployed, note the backend URL: `https://agric-stat-backend-<hash>.onrender.com`.

### 2c. Verify the backend

```bash
curl https://<your-backend>.onrender.com/docs
curl https://<your-backend>.onrender.com/api/products
```

The `/docs` URL should return the Swagger UI page. The `/api/products` endpoint should return an array (populated with seed data on first startup).

The database schema is created and seeded automatically when the backend starts. No manual `init_db.py` step is needed on Render.

---

## Step 3 — Deploy Frontend to Vercel

### 3a. Import the project

1. Log in to https://vercel.com.
2. Click **Add New...** > **Project**.
3. Import your GitHub repository.
4. Configure:
   - Framework Preset: **Vite**
   - Root Directory: `web`
   - Build Command: `npm run build`
   - Output Directory: `dist`

### 3b. Set the environment variable

Under **Environment Variables**, add:

| Key            | Value                                              |
|----------------|----------------------------------------------------|
| `VITE_API_URL` | `https://<your-backend>.onrender.com/api`          |

Replace `<your-backend>` with the actual Render subdomain from step 2b.

5. Click **Deploy**.
6. Wait 1–2 minutes. Note your frontend URL: `https://agric-stat-<hash>.vercel.app`.

---

## Step 4 — Connect Frontend and Backend

Update the backend CORS configuration to allow requests from your Vercel domain:

1. Go to the Render dashboard > `agric-stat-backend` > **Environment**.
2. Set `ALLOWED_ORIGINS` to your Vercel URL:
   ```
   https://agric-stat-<hash>.vercel.app
   ```
3. Save. Render will redeploy automatically.

### Final URLs

| Resource     | URL                                              |
|--------------|--------------------------------------------------|
| Frontend     | `https://agric-stat-<hash>.vercel.app`           |
| Backend API  | `https://<your-backend>.onrender.com/api`        |
| API Docs     | `https://<your-backend>.onrender.com/docs`       |

---

## Deployment Checklist

### Before deploying

- [ ] Code committed and pushed to GitHub `main`
- [ ] `backend/requirements-render.txt` exists and does not include Prophet or statsmodels
- [ ] `web/package.json` and `web/vite.config.js` are committed
- [ ] No secrets committed (`.env` files in `.gitignore`)

### Render (backend + database)

- [ ] PostgreSQL service created; Internal Database URL copied
- [ ] Web service created with correct build and start commands
- [ ] `DATABASE_URL`, `SECRET_KEY`, `PYTHONUNBUFFERED`, `DEBUG` set
- [ ] First deployment completed without errors
- [ ] `/api/products` returns data

### Vercel (frontend)

- [ ] Project imported with Root Directory set to `web`
- [ ] `VITE_API_URL` set to the Render backend URL + `/api`
- [ ] Deployment completed without errors
- [ ] Frontend URL noted

### Post-deployment

- [ ] `ALLOWED_ORIGINS` on Render updated with the Vercel URL
- [ ] Backend redeployed after CORS update
- [ ] Login works (admin / admin123)
- [ ] Dashboard shows products, transactions, forecasts, recommendations
- [ ] CSV export works on Transactions, Forecasts, Recommendations pages

---

## Free Tier Limits

| Service          | Limit                          | Implication                                      |
|------------------|--------------------------------|--------------------------------------------------|
| Render backend   | 512 MB RAM, 0.5 CPU            | Adequate for the app; no concurrent-load testing |
| Render free tier | Spins down after 15 min idle   | First request after idle takes ~5–10 seconds     |
| Render PostgreSQL| 256 MB storage, 90-day expiry  | Back up data before expiry or upgrade plan       |
| Vercel           | 100 GB bandwidth/month         | Sufficient for demos and development             |

To keep the backend warm, send a periodic ping to the `/docs` or `/api/products` endpoint using a free service such as UptimeRobot.

---

## Troubleshooting

### Backend fails to build

The most common cause is Prophet or statsmodels being included in the requirements file. Render's free tier cannot compile these from source.

Use `backend/requirements-render.txt` as the build command input, not `backend/requirements.txt`.

See [RENDER_FIX.md](RENDER_FIX.md) for the full explanation and the difference between the two requirement files.

### Frontend shows CORS errors

The `ALLOWED_ORIGINS` backend variable does not include the exact Vercel URL (including `https://`). Update it and wait for the Render service to redeploy.

### Backend returns 502 or 503

The free-tier instance is spinning up after being idle. Wait 10–15 seconds and retry.

### "No sample data" after deployment

The seeder runs on first startup when the database is empty. If the database was recreated or wiped, restart the Render web service from the dashboard to trigger the seeder again.

### Login fails

Verify that `SECRET_KEY` is set in Render environment variables. Without it, the backend will fail to generate or validate JWT tokens.

### Frontend deployed but API calls fail

Check the browser network tab (F12 > Network). If the API URL is wrong, update `VITE_API_URL` in Vercel environment variables and redeploy.

---

## Architecture

```
Browser
   |
   | HTTPS
   v
Vercel CDN  (React SPA, static assets)
   |
   | HTTPS  /api/*
   v
Render Web Service  (FastAPI + Uvicorn)
   |
   | Internal network
   v
Render PostgreSQL  (agric_stat_db)
```

The frontend is a static single-page application served from Vercel's CDN. It communicates with the backend exclusively via the `/api` prefix. The backend connects to the managed PostgreSQL instance using the internal network URL, which does not count against egress limits.
