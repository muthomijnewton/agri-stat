# 🌾 Agricultural Statistics Dashboard

A production-ready full-stack application for agricultural businesses to track inventory, forecast demand, optimize stock levels, and reduce waste through AI-powered analytics.

**Quick Links:** [Get Started](GET_STARTED.md) • [API Docs](http://localhost:8000/docs) • [System Overview](#-technology-stack)

## 📋 What Does This App Do?

The Agricultural Statistics Dashboard helps you:

- **Track Inventory** - Manage all your agricultural products in one place
- **Monitor Sales** - Record and analyze every transaction
- **Predict Demand** - Use AI to forecast future product demand
- **Optimize Stock** - Get smart recommendations for inventory levels
- **Reduce Waste** - Avoid overstocking that leads to spoilage
- **Take Action** - Make data-driven decisions with visual analytics

**Perfect for:** Farms, cooperatives, agricultural distributors, agricultural retailers

---

## ⚡ Quick Start (2 Minutes)

### System Requirements
- Python 3.13+
- Node.js 18+  
- Git (optional, for cloning)

### Get It Running

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # (venv\Scripts\activate on Windows)
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Then open:** http://localhost:3001

✅ **That's it! App is running.**

### Need Detailed Help?
👉 **[Complete Setup Guide for Windows/macOS/Linux](GET_STARTED.md)**

```
agric-stat-dash/
├── backend/                    # FastAPI REST API (Python)
│   ├── app/
│   │   ├── routes/            # API endpoint handlers
│   │   ├── models/            # SQLAlchemy ORM models (User, Product, Transaction, Forecast, Recommendation)
│   │   ├── services/          # Business logic (forecasting, inventory optimization)
│   │   ├── core/              # Configuration and database settings
│   │   └── main.py            # FastAPI application entry point
│   ├── tests/                 # pytest test suite (55+ tests)
│   ├── requirements.txt       # Python package dependencies
│   └── README.md              # Backend-specific documentation
├── frontend/                  # React + Vite web application
│   ├── src/
│   │   ├── pages/            # Dashboard pages (5 pages)
│   │   │   ├── Dashboard.jsx  # Main dashboard with stats
│   │   │   ├── Products.jsx   # Product management
│   │   │   ├── Transactions.jsx
│   │   │   ├── Forecasts.jsx
│   │   │   └── Recommendations.jsx
│   │   ├── components/        # Reusable React components (8+)
│   │   ├── services/          # API client (api.js with Axios)
│   │   └── styles/            # CSS stylesheets
│   ├── package.json          # npm dependencies
│   ├── vite.config.js        # Vite bundler configuration
│   └── README.md              # Frontend-specific documentation
├── mobile/                    # Flutter mobile application
│   ├── lib/
│   │   ├── screens/          # Mobile screens (5 screens matching web)
│   │   ├── widgets/          # Reusable Flutter widgets
│   │   ├── models/           # Data models with JSON serialization
│   │   ├── services/         # Dio API client
│   │   └── main.dart         # App entry point
│   ├── pubspec.yaml          # Flutter package dependencies
│   └── README.md              # Mobile-specific documentation
├── docs/                      # Project documentation
│   ├── API.md                # REST API endpoint reference
│   └── ARCHITECTURE.md       # System architecture
├── .gitignore                # Git ignore configuration
├── .env.example              # Example environment variables
├── RUN_LOCALLY.md            # Complete local setup guide ⭐ START HERE
├── QUICK_START.md            # Quick reference for starting servers
├── SYSTEM_STATUS.md          # Current system status overview
└── README.md                 # This file
```

---

## 🚀 Quick Start (3 Steps)

> ⭐ **For detailed setup**: See [RUN_LOCALLY.md](RUN_LOCALLY.md)

### Prerequisites
```bash
python --version      # 3.13+
node --version       # 18+
npm --version        # 9+
```

### Step 1: Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn app.main:app --reload --port 8000
```
✅ Backend running: http://localhost:8000/docs

### Step 2: Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend running: http://localhost:5173

### Step 3: Open App
Open http://localhost:5173 in your browser

---

## 📚 Documentation

| Document | For |
|----------|-----|
| **[GET_STARTED.md](GET_STARTED.md)** | Complete setup guide with troubleshooting |
| **[README.md](README.md)** | This file - Project overview |

---

## 🔧 Development

### Run Tests
```bash
cd backend
pytest tests/ -v              # All tests
pytest tests/ --cov=app      # With coverage report
```

### API Documentation
When backend is running: http://localhost:8000/docs (Swagger UI)

### Project Commands
```bash
# Backend
cd backend && PYTHONPATH=. python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest tests/ -v
```

---

## 🌐 API Endpoints

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get details
- `PUT /api/products/{id}` - Update
- `DELETE /api/products/{id}` - Delete

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Record transaction

### Forecasts
- `GET /api/forecasts` - List forecasts
- `POST /api/forecasts` - Create forecast

### Recommendations
- `GET /api/recommendations` - List recommendations
- `PUT /api/recommendations/{id}/approve` - Approve

**Full docs**: http://localhost:8000/docs

---

## 🐛 Troubleshooting

See detailed troubleshooting guide in [RUN_LOCALLY.md](RUN_LOCALLY.md)

**Quick fixes**:
```bash
# Port 8000 in use
lsof -i :8000 && kill -9 <PID>

# npm issues
npm cache clean --force && npm install

# Python imports
export PYTHONPATH=./backend
```

---

## 🚢 Deployment

See each component's README:
- [backend/README.md](backend/README.md) - Backend deployment
- [frontend/README.md](frontend/README.md) - Frontend deployment
- [mobile/README.md](mobile/README.md) - Mobile deployment

---

## 📝 Git & GitHub Notes

### Use Relative Paths in Documentation
✅ **DO**:
```markdown
cd backend          # Relative path
npm install         # Uses current directory
```

❌ **DON'T**:
```markdown
cd /home/user/projects/agric-stat-dash/backend   # Absolute path - breaks for others
```

### Never Commit
```
.env                # Secrets
venv/ node_modules/ # Dependencies
__pycache__/        # Python cache
.DS_Store dist/     # OS files & builds
```

### Environment Setup
```bash
# Create from template
cp .env.example .env
# Edit with your values
nano .env
```

---

## 📋 Checklist Before Pushing

- [ ] Used relative paths in all documentation
- [ ] Run tests: `cd backend && pytest tests/ -v`
- [ ] Check `.gitignore` excludes sensitive files
- [ ] `.env` file NOT committed (use `.env.example`)
- [ ] `node_modules/`, `venv/` NOT committed
- [ ] README points to [RUN_LOCALLY.md](RUN_LOCALLY.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes & test: `pytest tests/ -v`
4. Use relative paths in docs
5. Commit: `git commit -m "feat: description"`
6. Push: `git push origin feature/name`
7. Create Pull Request

---

## 📧 Support

- **Documentation**: See [RUN_LOCALLY.md](RUN_LOCALLY.md) first
- **Backend issues**: Check [backend/README.md](backend/README.md)
- **Frontend issues**: Check [frontend/README.md](frontend/README.md)
- **GitHub issues**: Create an issue in this repository

---

## 🛠️ Technology Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (Python 3.13) |
| Database | PostgreSQL 12+ |
| ORM | SQLAlchemy 2.0 |
| Forecasting | Prophet & ARIMA (StatsModels) |
| API Docs | Swagger/OpenAPI |
| Async | Uvicorn ASGI Server |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18 |
| Build Tool | Vite |
| Routing | React Router DOM |
| HTTP Client | Axios |
| Styling | CSS3 + CSS Variables |
| Layout | CSS Grid/Flexbox |

### Database
| Table | Purpose |
|-------|---------|
| users | User accounts and roles |
| products | Agricultural product inventory |
| transactions | Sales and purchase records |
| forecasts | AI demand predictions |
| inventory_recommendations | Stock level suggestions |

---

## 📦 Core Modules

### 1. **Admin Module**
- Manage users and system settings
- Configure forecasting parameters
- Set safety stock multipliers

### 2. **Data Management Module**
- Add/edit/delete products
- Record transactions
- Track historical data
- Data validation and cleanup

### 3. **Demand Forecasting Module**
- Analyze transaction history
- Generate forecasts using Prophet/ARIMA
- Calculate confidence intervals
- Model accuracy tracking (MAPE)

### 4. **Inventory Recommendation Module**
- Calculate optimal stock levels
- Apply safety stock formulas
- Consider lead times
- Track recommendation workflow (pending → approved → implemented)

### 5. **Reporting Module**
- Dashboard with KPIs
- Trend analysis
- Forecast visualization
- Recommendation tracking

---

## 🔌 API Endpoints

### Products
```
GET    /api/products              # List products (paginated)
GET    /api/products/{id}         # Get product details
POST   /api/products              # Create product
PUT    /api/products/{id}         # Update product
DELETE /api/products/{id}         # Delete product (soft delete)
```

### Transactions
```
GET    /api/transactions                           # List with filters
GET    /api/transactions/{id}                      # Get details
POST   /api/transactions                           # Record transaction
PUT    /api/transactions/{id}                      # Update
DELETE /api/transactions/{id}                      # Delete
```

Filters: `product_id`, `start_date`, `end_date`

### Forecasts
```
GET    /api/forecasts                              # List forecasts
GET    /api/forecasts/{id}                         # Get details
GET    /api/forecasts/product/{product_id}        # Product forecasts
POST   /api/forecasts                              # Create forecast
PUT    /api/forecasts/{id}                         # Update
DELETE /api/forecasts/{id}                         # Delete
```

### Recommendations
```
GET    /api/recommendations                        # List recommendations
GET    /api/recommendations/{id}                   # Get details
GET    /api/recommendations/product/{product_id}  # Product recommendations
POST   /api/recommendations                        # Create recommendation
PATCH  /api/recommendations/{id}/approve          # Approve (pending → approved)
PATCH  /api/recommendations/{id}/implement        # Implement (approved → implemented)
PUT    /api/recommendations/{id}                   # Update
DELETE /api/recommendations/{id}                   # Delete
```

---

## 🖥️ Web Frontend Features

### Dashboard
- Real-time statistics (products, transactions, forecasts, pending recommendations)
- Quick access to all modules
- System overview and instructions

### Products Management
- Add new agricultural products
- Set product categories and pricing
- View all products in a table
- Delete products (soft delete)

### Transactions
- Record sales or purchases
- Auto-calculate totals
- Filter by date range and product
- View transaction history

### Demand Forecasts
- View AI-generated predictions
- Filter by product
- See confidence intervals (lower/upper bounds)
- Monitor forecast accuracy (MAPE %)
- Understand forecasting methods (Prophet vs ARIMA)

### Inventory Recommendations
- View recommended stock levels
- Track recommendation status (pending → approved → implemented)
- Approve recommendations
- Mark as implemented
- View recommendation rationale

### UI Features
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Color-coded status badges
- ✅ Intuitive forms with validation
- ✅ Loading indicators
- ✅ Error handling
- ✅ Success notifications

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agric_stat_db
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agric_stat_db

# FastAPI
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=True

# Forecasting
FORECAST_DAYS=30
FORECAST_MODEL=prophet

# URLs
WEB_URL=http://localhost:3000
MOBILE_API_URL=http://192.168.1.100:8000

# Environment
ENVIRONMENT=development
```

**Frontend (.env in web/):**
```env
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 📊 Database Setup

### Using Script:
```bash
./setup_db.sh
```

### Using Python:
```bash
source venv/bin/activate
python init_db.py
```

### Manual PostgreSQL:
```sql
CREATE DATABASE agric_stat_db;
```

---

## 🧪 Testing

### Backend Tests
```bash
source venv/bin/activate
python -m pytest backend/tests/ -v
```

### Frontend Tests
```bash
cd web
npm test
```

---

## 📦 Building for Production

### Backend
```bash
# No build needed, just configure production environment
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd web
npm run build
# Deploy dist/ folder to web hosting
```

---

## 🚀 Deployment Options

### Backend
- **Heroku** - `git push heroku main`
- **Railway** - Connect GitHub repo
- **DigitalOcean** - Docker deployment
- **AWS** - EC2 + RDS

### Frontend
- **Vercel** - Connect GitHub repo
- **Netlify** - Drag & drop `dist/` folder
- **GitHub Pages** - Static hosting
- **AWS S3 + CloudFront** - CDN

---

## 📚 Key Features Explained

### Demand Forecasting
- **Method 1 - Prophet:** Facebook's time-series library, great for seasonal data
- **Method 2 - ARIMA:** Classical statistical approach for trends
- **Accuracy:** Calculated using MAPE (Mean Absolute Percentage Error)

### Inventory Recommendations Formula
```
Recommended Stock = (Avg Daily Demand × Lead Time) × Safety Factor
                  = (Avg Daily Demand × 3 days) × 1.5
```

This ensures:
- Enough stock for 3-day supply chain lead time
- 50% safety buffer for demand variability

### Workflow
```
1. Add Products → 2. Record Transactions → 3. System Generates Forecasts
   → 4. System Creates Recommendations → 5. Approve Recommendations
   → 6. Implement in Warehouse
```

---

## 📝 Development Guide

### Adding a New API Endpoint

```python
# backend/app/api/endpoints/new_feature.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

@router.get("/")
def get_all(db: Session = Depends(get_db)):
    # Implementation
    pass
```

### Adding a New React Page

```jsx
// web/src/pages/NewPage.jsx
import { useState, useEffect } from 'react'
import { api } from '../services/api'

export default function NewPage() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    loadData()
  }, [])
  
  const loadData = async () => {
    // Implementation
  }
  
  return <div>Your component</div>
}
```

---

## 🐛 Troubleshooting

### Backend Issues
```
Issue: Database connection refused
Fix: Check PostgreSQL is running and credentials in .env

Issue: Port 8000 already in use
Fix: lsof -i :8000 then kill process or use different port

Issue: Module not found errors
Fix: Ensure virtual environment is activated and pip install -r requirements.txt
```

### Frontend Issues
```
Issue: API not responding
Fix: Check backend is running at http://localhost:8000

Issue: Port 5173 already in use
Fix: npm run dev -- --port 3000 (use different port)

Issue: node_modules conflicts
Fix: rm -rf node_modules && npm install
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with descriptive commits
3. Test thoroughly
4. Push and create pull request

---

## 📄 License

**University of Eastern Africa, Baraton**  
INSY 492 - Senior Project (2026)

---

## 📞 Support

For questions or issues:
1. Check API documentation: `http://localhost:8000/docs`
2. Review README files in backend/ and web/ directories
3. Check error messages and logs
4. Review code comments for implementation details

---

## ✨ Future Enhancements

- [ ] User authentication and authorization (JWT)
- [ ] Mobile app (React Native or Flutter)
- [ ] Advanced data visualization (Recharts charts)
- [ ] Email notifications for recommendations
- [ ] Data export (CSV, PDF reports)
- [ ] Multi-user collaboration
- [ ] Historical trend analysis
- [ ] Seasonal adjustment
- [ ] Real-time notifications
- [ ] Batch recommendations generation

---

**Last Updated:** April 6, 2026

Happy forecasting! 🌾📊
