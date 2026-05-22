# 🚀 AgricStat Live Demo Deployment Guide

## Quick Summary
Deploy AgricStat to **free hosting** with sample data in ~30 minutes using:
- **Backend**: Render.com (FastAPI + PostgreSQL)
- **Frontend**: Vercel.com (React)
- **Both**: Auto-deploy from GitHub

---

## ✅ Prerequisites
1. GitHub account (free)
2. Render.com account (free)
3. Vercel.com account (free)
4. Push your code to GitHub

---

## 📋 Step 1: Push Code to GitHub

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial AgricStat commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/agric-stat-dash.git
git branch -M main
git push -u origin main
```

---

## 🎯 Step 2: Deploy Backend to Render.com

### 2.1 Create Render Account
- Go to **render.com**
- Sign up (free)
- Connect GitHub

### 2.2 Create PostgreSQL Database
1. Click **New +** → **PostgreSQL**
2. Fill form:
   - **Name**: `agric-stat-db`
   - **Database**: `agric_stat_db`
   - **User**: `postgres` (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: Free
3. Click **Create Database**
4. **Copy the Internal Database URL** (you'll need this)

### 2.3 Create Web Service
1. Click **New +** → **Web Service**
2. Select your GitHub repo
3. Fill form:
   - **Name**: `agric-stat-backend`
   - **Environment**: `Python 3.11`
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```
     cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```
   - **Plan**: Free
4. Add **Environment Variables**:
   - `DATABASE_URL`: (paste the PostgreSQL URL from step 2.2)
   - `PYTHONUNBUFFERED`: `true`
   - `DEBUG`: `false`
   - `ALLOWED_ORIGINS`: Add your frontend Vercel URL (we'll get this in Step 3)

5. Click **Create Web Service**
6. Wait for deployment (~2-3 min)
7. **Copy the URL** - you'll see it at top like: `https://agric-stat-backend.render.com`

### 2.4 Initialize Database with Sample Data
After backend is live:

```bash
# Connect to Render PostgreSQL and seed data
# Option A: Use Render Shell
# 1. Go to your database in Render dashboard
# 2. Click "Connect"
# 3. Copy the connection URL
# 4. From your local machine:

psql "YOUR_INTERNAL_DB_URL" < backend/init_db_seed.sql
```

**Or create a seed endpoint** (recommended):

Create file: `backend/app/api/endpoints/seed.py`

```python
from fastapi import APIRouter
from app.db.database import SessionLocal
from backend.init_db import add_sample_data

router = APIRouter(prefix="/api", tags=["admin"])

@router.post("/seed-database")
def seed_database():
    """Initialize database with sample data (admin only)"""
    db = SessionLocal()
    try:
        add_sample_data()
        return {"message": "Database seeded successfully"}
    finally:
        db.close()
```

Then call:
```bash
curl -X POST https://agric-stat-backend.render.com/api/seed-database
```

---

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
- Go to **vercel.com**
- Sign up (free with GitHub)

### 3.2 Import Project
1. Click **Add New...** → **Project**
2. Import your GitHub repo
3. Configure:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.3 Add Environment Variables
1. Go to **Settings** → **Environment Variables**
2. Add:
   - Key: `VITE_API_URL`
   - Value: `https://agric-stat-backend.render.com` (from Step 2.7)

3. Click **Deploy**
4. Get your Vercel frontend URL (e.g., `https://agric-stat.vercel.app`)

### 3.4 Update Backend CORS
Back to Render dashboard:
1. Go to `agric-stat-backend` service
2. Edit **Environment Variables**
3. Update `ALLOWED_ORIGINS`:
   ```
   https://agric-stat.vercel.app
   ```
4. Your backend will auto-redeploy

---

## 🔗 Step 4: Update Frontend API URL

Edit `frontend/src/services/api.js`:

```javascript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## 📊 Step 5: Initialize Sample Data

### Option 1: Via API Endpoint (Easiest)
```bash
curl -X POST https://agric-stat-backend.render.com/api/seed-database
```

### Option 2: Via Render Shell
1. Go to PostgreSQL database in Render
2. Click "Connect" → "External Database URL"
3. Connect via psql and run:
   ```sql
   -- Import your seed SQL script
   ```

### Option 3: One-time Job
Create in Render dashboard:
- New **One-off Job**
- Command: `cd backend && python init_db.py --include-data`

---

## ✨ Final Deployment URLs

```
Frontend: https://agric-stat.vercel.app
Backend API: https://agric-stat-backend.render.com
API Docs: https://agric-stat-backend.render.com/docs
```

---

## 🔑 Free Tier Limits

| Service | Limit | Note |
|---------|-------|------|
| **Render** | 512 MB RAM, 0.5 CPU | Spins down after 15 min inactivity |
| **PostgreSQL** | 90 days, 256 MB | Free tier resets periodically |
| **Vercel** | Unlimited builds | 100GB/month bandwidth |

---

## 🚨 Troubleshooting

### Backend not connecting to DB
- Check `DATABASE_URL` in Render env vars
- Ensure PostgreSQL is running
- Check database credentials

### Frontend can't reach backend
- Verify `VITE_API_URL` is correct
- Check CORS settings in `app/main.py`
- Ensure backend URL is in `ALLOWED_ORIGINS`

### Sample data not loading
- Call `/api/seed-database` endpoint
- Check database connectivity
- Verify init_db script runs without errors

---

## 💰 Alternative Free Hosting Options

| Platform | Backend | Frontend | Database | Best For |
|----------|---------|----------|----------|----------|
| **Render** | ✅ | ✅ | ✅ PostgreSQL | Best all-in-one |
| **Railway** | ✅ | ✅ | ✅ PostgreSQL | Generous free tier |
| **Fly.io** | ✅ | ✅ | ✅ PostgreSQL | Fastest performance |
| **Heroku** | ❌ | ✅ | ❌ | Paid now |
| **Vercel + AWS** | ✅ | ✅ | ✅ | More complex |

---

## 📱 Live Demo Ready!

Your AgricStat demo is now live with:
- ✅ 20 sample products
- ✅ 225 transactions
- ✅ 60 forecasts
- ✅ 10 recommendations
- ✅ Full dashboard, charts, and filtering

Share the link: `https://agric-stat.vercel.app`
