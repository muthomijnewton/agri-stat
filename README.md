# Agricultural Statistics Dashboard

A web and mobile application for demand forecasting and inventory optimization to reduce agricultural produce waste.

## 🌾 Overview

This system helps agricultural distributors by:
- 📊 Analyzing historical sales data
- 📈 Forecasting future demand using AI (Prophet & ARIMA models)
- 💡 Recommending optimal inventory levels
- 📉 Reducing agricultural waste through better planning

**University of Eastern Africa, Baraton**  
**Course:** INSY 492 - Senior Project  
**Student:** Newton Jones Muthomi (SNEWJO2011)  
**Supervisor:** Omari Dickson

---

## 📁 Project Structure

```
agric-stat-dash/
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── endpoints/     # (products, transactions, forecasts, recommendations)
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── services/          # Business logic (forecasting, calculations)
│   │   ├── db/                # Database configuration
│   │   ├── core/              # Settings and configuration
│   │   └── main.py            # FastAPI app entry point
│   ├── tests/                 # Unit and integration tests
│   └── requirements.txt       # Python dependencies
├── web/                       # React 18 Frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── Transactions.jsx
│   │   │   ├── Forecasts.jsx
│   │   │   └── Recommendations.jsx
│   │   ├── services/          # API integration layer
│   │   ├── css/               # Stylesheets
│   │   ├── App.jsx            # Main React component
│   │   └── main.jsx           # React entry point
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite build configuration
│   ├── index.html            # HTML entry
│   └── README.md             # Frontend documentation
├── mobile/                     # Mobile app (Coming Soon)
│   └── src/
│       ├── screens/          # Mobile screens
│       ├── components/       # Reusable components
│       └── services/         # API services
├── docs/                      # Documentation
├── venv/                      # Python virtual environment
├── .env                       # Environment variables (local, not committed)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── requirements-base.txt      # Core dependencies (minimal)
├── init_db.py                # Database initialization script
├── setup_db.sh               # Database setup shell script
├── run_backend.sh            # Backend startup script
├── run_frontend.sh           # Frontend startup script
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Option 1: Run Both Services

**Terminal 1 - Backend:**
```bash
./run_backend.sh
# Backend at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
# Frontend at http://localhost:5173
```

### Option 2: Manual Setup

**Backend:**
```bash
source venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd web
npm install
npm run dev
```

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
