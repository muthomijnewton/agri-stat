# 🚀 AgricStat Live Demo - Quick Deployment Checklist

## ✅ Pre-Deployment (Local)

- [ ] Code committed to GitHub repository
- [ ] `.env.example` file exists with all required vars
- [ ] Backend `requirements.txt` is up-to-date
- [ ] Frontend `package.json` and `vite.config.js` configured
- [ ] Tests passing: `cd backend && pytest tests/ -v`
- [ ] App runs locally: Backend at `:8000`, Frontend at `:3000`

---

## 📍 Render.com Deployment (Backend + Database)

### Create PostgreSQL Database
- [ ] Go to render.com and sign in
- [ ] Click **New +** → **PostgreSQL**
- [ ] Name: `agric-stat-db`
- [ ] Region: Choose closest to your users
- [ ] Plan: **Free**
- [ ] Click **Create Database**
- [ ] **Copy Internal Database URL** and save it

### Create Web Service
- [ ] Click **New +** → **Web Service**
- [ ] Select your GitHub repository
- [ ] Fill in details:
  - [ ] Name: `agric-stat-backend`
  - [ ] Environment: `Python 3.11`
  - [ ] Build Command: `pip install -r backend/requirements.txt`
  - [ ] Start Command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - [ ] Plan: **Free**
- [ ] Add Environment Variables:
  - [ ] `DATABASE_URL`: Paste PostgreSQL URL from above
  - [ ] `PYTHONUNBUFFERED`: `true`
  - [ ] `DEBUG`: `false`
- [ ] Click **Create Web Service**
- [ ] Wait for deployment ⏳ (2-3 minutes)
- [ ] **Note your Backend URL**: `https://agric-stat-backend-xxxxx.render.com`

### Initialize Database
- [ ] Option A: Wait 5 min, then visit: `https://YOUR_BACKEND_URL/docs`
  - [ ] Find `/api/seed-database` endpoint
  - [ ] Click "Try it out" → "Execute"
- [ ] Option B: Use curl from terminal:
  ```bash
  curl -X POST https://YOUR_BACKEND_URL/api/seed-database
  ```
- [ ] Verify in API docs → `/api/products` shows 20+ products

---

## 🎨 Vercel Deployment (Frontend)

### Import Project
- [ ] Go to vercel.com and sign in
- [ ] Click **Add New** → **Project**
- [ ] Import your GitHub repository
- [ ] Select and import the repo

### Configure Build
- [ ] Framework: `Vite`
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build`
- [ ] Install Command: `npm install`
- [ ] Output Directory: `dist`

### Environment Variables
- [ ] Click **Environment Variables**
- [ ] Add: `VITE_API_URL` = `https://YOUR_BACKEND_URL`
  - [ ] Replace `YOUR_BACKEND_URL` with Render backend URL
- [ ] Click **Deploy**
- [ ] Wait for deployment ⏳ (1-2 minutes)
- [ ] **Note your Frontend URL**: `https://agric-stat-xxxxx.vercel.app`

---

## 🔐 Update Backend CORS

- [ ] Go back to Render dashboard
- [ ] Select `agric-stat-backend` service
- [ ] Go to **Environment**
- [ ] Edit `ALLOWED_ORIGINS`:
  ```
  https://YOUR_FRONTEND_URL
  ```
- [ ] Save and service will auto-redeploy

---

## 🧪 Test Live Deployment

### Test Backend
- [ ] Visit: `https://YOUR_BACKEND_URL/docs`
- [ ] See Swagger UI
- [ ] Try GET `/api/products` - should return 20 products
- [ ] Try GET `/api/forecasts` - should return 60 forecasts

### Test Frontend
- [ ] Visit: `https://YOUR_FRONTEND_URL`
- [ ] Login with `admin@agri` / `1234`
- [ ] Check Dashboard - should show stats and charts
- [ ] Navigate to Forecasts - should show 60 records
- [ ] Navigate to Recommendations - should show 10 records

### Test Data Verification
- [ ] Dashboard Stats:
  - [ ] Total Products: 20
  - [ ] Transactions: 225
  - [ ] Pending Recommendations: 4
  - [ ] Active Forecasts: 60

---

## 📊 Live Demo URLs

```
🌐 Frontend: https://YOUR_FRONTEND_URL
📡 Backend: https://YOUR_BACKEND_URL
📖 API Docs: https://YOUR_BACKEND_URL/docs
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `requirements.txt`, ensure Python 3.11+ |
| DB connection error | Verify `DATABASE_URL` env var in Render |
| Frontend shows 404 | Check `VITE_API_URL` environment variable |
| CORS error in browser | Add frontend URL to backend `ALLOWED_ORIGINS` |
| No sample data | Visit `/api/seed-database` endpoint to initialize |
| Render spins down | Restart service or use Paid Tier |

---

## 💾 Backup & Maintenance

- [ ] Enable **Render Database Backups** (Settings → Auto Backup)
- [ ] Set up **GitHub Actions** for CI/CD (optional)
- [ ] Monitor Render dashboard for quota usage
- [ ] PostgreSQL free tier resets every ~3 months

---

## 🎉 You're Done!

Your AgricStat demo is live with:
- ✅ FastAPI backend on Render
- ✅ React frontend on Vercel
- ✅ PostgreSQL database with sample data
- ✅ Automatic deploys on GitHub push
- ✅ Zero cost to host

**Share your demo:** `https://YOUR_FRONTEND_URL`

---

## 📈 Next Steps

For production deployment:
- Upgrade to Render **Paid Plan** ($7/month) for always-on backend
- Add **authentication** with JWT tokens
- Set up **environment-specific configs**
- Add **monitoring and error tracking** (Sentry)
- Enable **HTTPS** (already included)
- Scale database as needed
