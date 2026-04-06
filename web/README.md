# React Frontend - Agricultural Statistics Dashboard

Modern React web application for the Agricultural Statistics Dashboard system.

## Features

- 📊 **Dashboard** - Real-time statistics and overview
- 🌾 **Products Management** - Add, edit, and manage agricultural products
- 📈 **Transactions** - Record and track sales transactions
- 📉 **Forecasts** - View AI-powered demand predictions
- 💡 **Recommendations** - Intelligent inventory stock level recommendations
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API communication
- **Recharts** - Data visualization (optional)

## Setup

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

The app will start at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file in the `web` directory:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

Or copy from the example:

```bash
cp .env.example .env
```

## Project Structure

```
src/
├── pages/              # Page components
│   ├── Dashboard.jsx   # Main dashboard
│   ├── Products.jsx    # Product management
│   ├── Transactions.jsx    # Transaction records
│   ├── Forecasts.jsx   # Demand forecasts
│   └── Recommendations.jsx  # Inventory recommendations
├── components/         # Reusable components
├── services/          # API integration
│   └── api.js         # Axios instance and API calls
├── css/               # Stylesheets
├── App.jsx            # Main app component
└── main.jsx           # React DOM render
```

## API Integration

The app connects to the FastAPI backend at `http://localhost:8000/api` by default.

### Key API Endpoints

- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Record transaction
- `GET /api/forecasts` - View forecasts
- `GET /api/recommendations` - View recommendations

## Quick Start

1. **Start the backend:**
   ```bash
   cd backend
   ./run_backend.sh
   ```

2. **Install and start the frontend:**
   ```bash
   cd web
   npm install
   npm run dev
   ```

3. **Open browser:**
   Navigate to `http://localhost:5173`

## Features in Detail

### Dashboard
- Overview statistics
- Quick links to all modules
- System information

### Products
- Add new agricultural products
- Set prices and units
- View all product inventory

### Transactions
- Record sales and purchases
- Track by date range
- Calculate totals automatically

### Forecasts
- View AI-generated demand predictions
- Filter by product
- See confidence intervals

### Recommendations
- Get optimal stock level suggestions
- Approve recommendations
- Mark as implemented
- Track recommendation workflow

## Styling

The application uses:
- **CSS Grid** for responsive layouts
- **CSS Variables** for theming
- **Dark and light** color schemes
- Mobile-first responsive design

### Color Scheme

- Primary: Green (#2ecc71) - for success and primary actions
- Secondary: Blue (#3498db) - for secondary information
- Warning: Orange (#f39c12) - for pending items
- Danger: Red (#e74c3c) - for destructive actions

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Contributing

For development:

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Commit and push
5. Create a pull request

## License

University of Eastern Africa, Baraton - Senior Project
Student: Newton Jones Muthomi (SNEWJO2011)
