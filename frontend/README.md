# Frontend - React with Vite

This is the React frontend for the Agricultural Statistics Dashboard.

## Setup

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable React components
│   ├── pages/             # Page components (Dashboard, Products, etc.)
│   ├── services/          # API service layer (axios)
│   ├── styles/            # CSS stylesheets
│   ├── App.jsx            # Main App component with routing
│   └── main.jsx           # Entry point
├── public/                # Static assets
├── vite.config.js         # Vite configuration
├── package.json           # Dependencies and scripts
└── index.html             # HTML template
```

## Features

- **Dashboard** - Overview with statistics and charts
- **Products** - Manage agricultural products
- **Transactions** - View sales/transaction history
- **Forecasts** - View demand predictions
- **Recommendations** - Inventory recommendations with approval workflow
- **Charts** - Interactive data visualizations using Recharts

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

All API calls are handled through `src/services/api.js`:

- `productsAPI` - Product CRUD operations
- `transactionsAPI` - Transaction management
- `forecastsAPI` - Demand forecasts
- `recommendationsAPI` - Inventory recommendations

## Styling

The application uses CSS modules and custom stylesheets for layout and styling.

Key style files:

- `styles/App.css` - Main app styles
- `styles/Dashboard.css` - Dashboard page styles
- `styles/Navbar.css` - Navigation styles
- Individual page CSS files in `styles/`

## Dependencies

- **React** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **date-fns** - Date utilities

## Running with Backend

Make sure the FastAPI backend is running on `http://localhost:8000`:

```bash
# In another terminal
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Then start the React frontend:

```bash
cd frontend
npm run dev
```
