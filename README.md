# AgricStat Dash

AgricStat Dash is a full-stack platform for demand forecasting, inventory optimization, and operational analytics in agricultural supply chains.

The repository includes a FastAPI backend, a React-based web frontend, and a Flutter mobile client.

## Repository Overview

- `backend/` - FastAPI application, database configuration, models, services, and API endpoints.
- `web/` - React frontend application built with Vite.
- `mobile/` - Flutter application for mobile device access.
- `alembic/` - Database migration configuration.
- `requirements.txt` - Python dependency file for backend runtime.
- `run_backend.sh` - Shell script to start the backend server.
- `run_frontend.sh` - Shell script to start the web frontend.

## Backend

The backend is implemented in Python with FastAPI and SQLAlchemy.

Key backend features:

- REST API for products, transactions, forecasts, recommendations, notifications, downloads, and authentication.
- Forecasting services based on Prophet and ARIMA.
- Inventory recommendation calculations using forecasted demand.
- Automatic sample data seeding at startup via `backend/init_db.py`.
- Default database configuration using SQLite, with optional PostgreSQL support through `DATABASE_URL`.

### Backend Requirements

Install runtime dependencies from the repository root or inside `backend/`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Starting the Backend

```bash
python backend/init_db.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend exposes OpenAPI documentation at:

`http://localhost:8000/docs`

## Web Frontend

The primary web frontend is located in `web/` and uses React with Vite.

### Web Frontend Setup

```bash
cd web
npm install
npm run dev
```

The frontend expects the backend API to be available at `http://localhost:8000`.

## Mobile Client

The mobile client is implemented with Flutter under `mobile/`.

The mobile application is intended to provide product access, transaction management, forecast viewing, and recommendation workflows on mobile devices.

## Development Notes

- `backend/app/core/config.py` sets environment defaults for database connection, API metadata, CORS origins, and forecasting settings.
- `backend/app/api/routes.py` registers API routers for authentication, products, transactions, forecasts, recommendations, downloads, and notifications.
- `backend/app/services/forecasting.py` handles demand forecasting and inventory recommendation calculations.

## Testing

Run backend tests from the `backend/` directory:

```bash
cd backend
pytest tests/ -v
```

For coverage:

```bash
pytest tests/ --cov=app
```

## Environment Configuration

The backend supports environment configuration via `.env` files and the `DATABASE_URL` variable.

If `DATABASE_URL` is not set, the backend uses a local SQLite database file at `backend/agric_stat.db`.

## Recommended Startup

From the repository root:

1. Create and activate a Python virtual environment.
2. Install backend dependencies.
3. Initialize the database and sample data.
4. Start the backend server.
5. Start the web frontend.

This README reflects the current repository structure, runtime dependencies, and startup process without presentation enhancements.
- Tamper-resistant historical forecasting logs
- Agricultural credit reputation layers

This creates strong interoperability potential with decentralized infrastructure ecosystems such as Cardano.

## Project Origin

Developed as advanced applied software engineering research through [University of Eastern Africa, Baraton](https://ueab.ac.ke) (INSY 492 Senior Project, 2026)

AgricStat reflects production-focused engineering designed for practical deployment beyond academic demonstration.

## Vision

Agricultural modernization requires more than digitization.

It requires decision intelligence infrastructure that makes fragmented systems more predictable, efficient, and resilient.

AgricStat exists to provide that operational intelligence layer.

---

## 📧 Support

- **Documentation**: See [RUN_LOCALLY.md](RUN_LOCALLY.md) first
- **Backend issues**: Check [backend/README.md](backend/README.md)
- **Frontend issues**: Check [web/README.md](web/README.md)
- **GitHub issues**: Create an issue in this repository

---

## 🛠️ Technology Stack

### Backend

| Component   | Technology                    |
| ----------- | ----------------------------- |
| Framework   | FastAPI (Python 3.13)         |
| Database    | PostgreSQL 12+                |
| ORM         | SQLAlchemy 2.0                |
| Forecasting | Prophet & ARIMA (StatsModels) |
| API Docs    | Swagger/OpenAPI               |
| Async       | Uvicorn ASGI Server           |

### Frontend

| Component   | Technology           |
| ----------- | -------------------- |
| Framework   | React 18             |
| Build Tool  | Vite                 |
| Routing     | React Router DOM     |
| HTTP Client | Axios                |
| Styling     | CSS3 + CSS Variables |
| Layout      | CSS Grid/Flexbox     |

### Database

| Table                     | Purpose                        |
| ------------------------- | ------------------------------ |
| users                     | User accounts and roles        |
| products                  | Agricultural product inventory |
| transactions              | Sales and purchase records     |
| forecasts                 | AI demand predictions          |
| inventory_recommendations | Stock level suggestions        |

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
import { useState, useEffect } from "react";
import { api } from "../services/api";

export default function NewPage() {
  const [data, setData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    // Implementation
  };

  return <div>Your component</div>;
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
