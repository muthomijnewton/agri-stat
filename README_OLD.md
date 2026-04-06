# Agricultural Statistics Dashboard

A web and mobile application for demand forecasting and inventory optimization to reduce agricultural produce waste.

## Project Structure

```
agric-stat-dash/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration and core settings
│   │   ├── api/            # API routes and endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database configuration
│   │   └── main.py         # FastAPI app initialization
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── web/                    # Web frontend (HTML/CSS/JavaScript)
│   └── src/
│       ├── components/     # Reusable components
│       ├── pages/          # Page components
│       ├── css/            # Stylesheets
│       └── assets/         # Images, fonts, etc.
├── mobile/                 # Mobile app (React Native/Flutter)
│   └── src/
│       ├── screens/        # Mobile screens
│       ├── components/     # Reusable mobile components
│       └── services/       # API services
├── docs/                   # Documentation
├── venv/                   # Python virtual environment
├── .env                    # Environment variables (not committed)
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

### 1. Backend Setup
```bash
source venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

### 2. Web Frontend Setup
(To be configured with HTML/CSS/JavaScript or a framework like React)

### 3. Mobile App Setup
(To be configured with React Native or Flutter)

## Modules

- **Admin Module** - Manage users, datasets, and system settings
- **Data Management Module** - Store and organize produce transaction data
- **Demand Forecasting Module** - Generate short-term demand predictions
- **Inventory Recommendation Module** - Suggest optimal produce quantities
- **Reporting Module** - Display insights and demand trends

## Technologies

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **Forecasting**: Prophet or ARIMA
- **Frontend**: HTML, CSS, JavaScript
- **Mobile**: React Native or Flutter
- **Version Control**: Git

## License

University of Eastern Africa, Baraton - Senior Project
Student: Newton Jones Muthomi (SNEWJO2011)
