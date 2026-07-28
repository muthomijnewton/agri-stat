# Web Frontend

React single-page application for AgricStat Dash. Communicates with the FastAPI backend via a REST API.

For project-level setup instructions see [GET_STARTED.md](../GET_STARTED.md).  
For the backend, see [backend/README.md](../backend/README.md).  
For deployment, see [DEPLOYMENT.md](../DEPLOYMENT.md).

---

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Pages and Features](#pages-and-features)
- [API Integration](#api-integration)
- [Authentication](#authentication)
- [Styling](#styling)
- [Build and Preview](#build-and-preview)

---

## Technology Stack

| Package          | Version   | Purpose                           |
|------------------|-----------|-----------------------------------|
| React            | 18.2      | UI library                        |
| Vite             | 5         | Build tool and dev server         |
| React Router DOM | 6.18      | Client-side routing               |
| Axios            | 1.6       | HTTP client                       |
| Recharts         | 2.10      | Chart components                  |

No additional icon libraries or UI component frameworks are used. All icons are inline SVG defined in the component files.

---

## Project Structure

```
web/
├── index.html
├── vite.config.js          Vite config; dev proxy for /api -> localhost:8000
├── package.json
├── .env.example
└── src/
    ├── main.jsx            React DOM entry point
    ├── App.jsx             Router, layout, navigation bar, route definitions
    ├── context/
    │   └── AuthContext.jsx JWT token storage, user state, login/logout
    ├── services/
    │   └── api.js          Axios instance, all API helpers, CSV export utility,
    │                       401 interceptor (auto-redirect to /login)
    ├── components/
    │   ├── RequireAuth.jsx Redirect to /login if not authenticated
    │   ├── NotificationBell.jsx  Unread notification count + dropdown
    │   └── Paginator.jsx   Reusable pagination control
    ├── pages/
    │   ├── Login.jsx
    │   ├── Dashboard.jsx
    │   ├── Products.jsx
    │   ├── Transactions.jsx
    │   ├── Forecasts.jsx
    │   ├── Recommendations.jsx
    │   ├── Analytics.jsx
    │   └── Profile.jsx
    └── css/
        ├── index.css       Global reset and CSS variable definitions
        ├── App.css         Navigation bar, layout, footer
        ├── pages.css       Shared page styles (cards, tables, forms, badges,
        │                   charts, paginator, low-stock banner)
        └── profile.css     Profile page-specific styles
```

---

## Setup

```bash
cd web
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`. API requests to `/api/*` are proxied to `http://localhost:8000` by `vite.config.js`, so no CORS configuration is needed during local development.

---

## Environment Variables

Create `web/.env` by copying `web/.env.example`:

```bash
cp .env.example .env
```

```env
VITE_API_URL=http://localhost:8000/api
```

Only variables prefixed with `VITE_` are exposed to the browser bundle by Vite. The `api.js` service file reads this value:

```js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
```

For a Vercel deployment, set `VITE_API_URL` in the Vercel dashboard to point to the Render backend URL.

---

## Pages and Features

### Login (`/login`)

JWT login form. On success, the token and user object are stored in `localStorage` via `AuthContext`. Authenticated users are redirected to `/`.

### Dashboard (`/`)

- KPI cards: total products, total transactions, active forecasts, pending/approved/implemented recommendations
- Low-stock alert banner: lists products where current quantity is below minimum stock level (derived from recommendation data)
- Daily revenue bar chart (last 30 days)
- Revenue by product pie chart (last 30 days)
- Platform overview and getting-started guide

### Products (`/products`)

- Paginated product table
- Add product form (name, category, unit, price, current quantity, min/max quantity)
- Soft delete with confirmation dialog

### Transactions (`/transactions`)

- Paginated transaction table with filters: product, transaction type (sale/purchase), date range
- Add transaction form
- CSV export (filtered or full)

### Forecasts (`/forecasts`)

- Paginated forecast table with product filter
- Per-forecast detail: model used (Prophet or ARIMA), forecast date, predicted demand, confidence interval (lower/upper), MAPE accuracy
- Generate forecast for a single product or all products
- CSV export

### Recommendations (`/recommendations`)

- Generate recommendation for a single product or all products (batch generate with per-product result log)
- Filter by status: pending, approved, implemented
- Recommendation cards showing: recommended quantity, current quantity, min/max stock, reason
- Status transitions: pending -> Approve -> approved -> Mark as Implemented -> implemented
- Delete (pending or implemented)
- CSV export

### Analytics (`/analytics`)

- Daily transaction trend (line chart)
- Transaction type split: sales vs purchases (bar or pie chart)
- Top products by quantity
- Forecast accuracy trend

### Profile (`/profile`)

- View and update username, email, full name, organization, location, role
- Change password form (requires current password)

---

## API Integration

All API calls are defined in `src/services/api.js`. The file exports:

| Export                | Purpose                                              |
|-----------------------|------------------------------------------------------|
| `api` (default)       | Configured Axios instance, used for ad-hoc calls     |
| `productsAPI`         | getAll, getById, create, update, delete              |
| `transactionsAPI`     | getAll, create, update, delete                       |
| `forecastsAPI`        | getAll, getById, create, update, delete, generate, generateAll |
| `recommendationsAPI`  | getAll, getById, create, approve, implement, delete, generate, generateAll |
| `notificationsAPI`    | getAll, unreadCount, markRead, markAllRead           |
| `authAPI`             | login, getProfile, updateProfile                     |
| `statsAPI`            | summary, transactionsDaily, revenueByProduct, transactionTypeSplit, forecastAccuracyTrend, recommendationStatusBreakdown, topProductsByQuantity |
| `exportsAPI`          | transactions, forecasts, recommendations (CSV download) |
| `exportCSV`           | Low-level CSV download helper                        |

A response interceptor handles 401 responses globally: it clears stored credentials and redirects to `/login`.

---

## Authentication

`AuthContext` manages authentication state. On login, the JWT token is stored in `localStorage` under `agristat_token`. The Axios instance adds the `Authorization: Bearer <token>` header to every request via a request interceptor.

`RequireAuth` wraps protected routes. If `isAuthenticated` is false, it redirects to `/login` and preserves the originally requested path for post-login redirect.

---

## Styling

Styles are plain CSS using custom properties (CSS variables) defined in `css/index.css`. No CSS framework or preprocessor is used.

Key variables:

```css
--brand-600: #16a34a;   /* primary green */
--brand-700: #15803d;
--gray-100 through --gray-900
--radius-sm, --radius, --radius-lg
--shadow-sm, --shadow, --shadow-lg
```

Badge classes (`badge-success`, `badge-warning`, `badge-info`, `badge-secondary`) and button classes (`btn-primary`, `btn-secondary`, `btn-danger`) are defined in `pages.css` and used across all page components.

---

## Build and Preview

```bash
# Development server (with HMR)
npm run dev

# Production build → web/dist/
npm run build

# Preview production build locally
npm run preview
```

The production build outputs static files to `web/dist/`. Deploy this directory to any static host (Vercel, Netlify, S3, GitHub Pages).
