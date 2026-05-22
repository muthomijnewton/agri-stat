# 🌾 AgricStat

Agricultural Intelligence & Forecasting Infrastructure for Cooperative-Scale Decision Making

AgricStat is a production-grade agricultural analytics platform built to help farms, cooperatives, distributors, and agricultural retailers optimize inventory, forecast product demand, reduce waste, and improve operational decision-making through intelligent statistical modeling.

Designed for fragmented agricultural markets where visibility, trust, and forecasting precision are often weak, AgricStat transforms historical transaction data into actionable inventory intelligence.

## Why AgricStat Exists

Agricultural systems across emerging and fragmented markets often face:

- Inconsistent inventory visibility
- Overstocking and spoilage losses
- Reactive purchasing decisions
- Weak demand forecasting capability
- Limited operational analytics
- Poor planning coordination across supply actors

These inefficiencies reduce profitability, increase waste, and weaken supply chain resilience.

AgricStat addresses this by providing predictive decision-support infrastructure for agricultural businesses operating in dynamic real-world environments.

## Core Capabilities

### Intelligent Inventory Management

Centralized product tracking across operational inventory layers with:

- Product lifecycle visibility
- Stock-level monitoring
- Historical inventory state analysis
- Soft-delete archival controls

### Transaction Intelligence

Track and analyze all operational movement:

- Purchase records
- Sales records
- Historical transaction patterns
- Product-specific movement analysis
- Temporal trend analysis

### Predictive Demand Forecasting

Forecast future product demand using statistical models including:

- Prophet forecasting
- ARIMA forecasting
- Confidence interval estimation
- Forecast accuracy monitoring (MAPE scoring)
- Seasonal demand pattern recognition

This enables proactive planning instead of reactive correction.

### Inventory Optimization Engine

Automatically recommends ideal stock levels using adaptive inventory logic based on:

- Historical demand behavior
- Supply lead-time assumptions
- Safety stock calculations
- Demand variability buffers

Recommendation workflow:

- Pending → Approved → Implemented

### Decision Intelligence Dashboard

Operational insights surfaced visually through:

- Product performance metrics
- Inventory status visibility
- Forecast trends
- Recommendation status tracking
- Forecast confidence visualization

Built for fast executive interpretation.

## Production Architecture

AgricStat is structured as a modern modular full-stack platform.

### Backend Infrastructure

- Framework: FastAPI
- Language: Python 3.13
- Database: PostgreSQL
- ORM: SQLAlchemy 2.0
- Forecasting Engine: Prophet + StatsModels ARIMA
- API Documentation: OpenAPI / Swagger
- Server Runtime: Uvicorn ASGI

Core backend responsibilities:

- Business logic orchestration
- Forecast generation
- Inventory recommendation processing
- Data validation
- API exposure
- Persistence control

### Frontend Platform

- Framework: React 18
- Build System: Vite
- Routing: React Router
- HTTP Layer: Axios
- Styling: Modular CSS Architecture

Capabilities:

- Responsive multi-device UI
- Operational dashboards
- Data-entry workflows
- Forecast visualization
- Recommendation approval pipelines

### Mobile Layer

- Framework: Flutter

Mobile parity includes:

- Product access
- Transaction management
- Forecast visibility
- Inventory recommendation workflows
- Field-operational accessibility

Designed for mobile-first agricultural environments.

## Platform Structure

```
agric-stat/

backend/
    app/
        routes/
        models/
        services/
        core/
        main.py

frontend/
    src/
        pages/
        components/
        services/
        styles/

mobile/
    lib/
        screens/
        widgets/
        services/
        models/

docs/
    API.md
    ARCHITECTURE.md
```

## Technical Quality Standards

AgricStat follows production engineering discipline:

- Modular service separation
- Test-driven backend validation
- Environment configuration isolation
- Relative-path documentation portability
- Clean deployment readiness
- Structured API contracts
- Scalable maintainability patterns

## Testing Coverage

Backend validation suite includes:

- API route testing
- Forecast service testing
- Database integration validation
- Business-rule enforcement tests
- Data consistency assurance

Run tests:

```bash
pytest tests/ -v
```

Coverage mode:

```bash
pytest tests/ --cov=app
```

## Local Deployment

### Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend:

```bash
cd frontend
npm install
npm run dev
```

### Application Access:

**Frontend:**

http://localhost:5173

**Backend API Docs:**

http://localhost:8000/docs

## Strategic Use Cases

AgricStat is designed for:

- **Agricultural Cooperatives** - Shared forecasting and inventory planning
- **Regional Distributors** - Demand visibility across distribution points
- **Retail Agricultural Networks** - Sales intelligence and stock optimization
- **Supply Coordination Hubs** - Cross-actor inventory synchronization
- **Agricultural Data Modernization Projects** - Digital agricultural intelligence infrastructure

## Future Infrastructure Evolution

Planned expansion includes:

- Multi-tenant cooperative environments
- Advanced forecasting ensembles
- PDF and CSV reporting exports
- Role-based authorization systems
- Real-time event notifications
- Collaborative operational planning
- Historical anomaly detection

### Potential Decentralized Extensions

AgricStat is intentionally architected to support future decentralized trust integrations such as:

- Verifiable inventory event anchoring
- Cooperative transaction immutability
- Supply chain audit proofs
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
- **Frontend issues**: Check [frontend/README.md](frontend/README.md)
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
