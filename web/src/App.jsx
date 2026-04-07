import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Transactions from "./pages/Transactions";
import Forecasts from "./pages/Forecasts";
import Recommendations from "./pages/Recommendations";
import "./css/App.css";

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="navbar-brand">
            <h1>🌾 Agricultural Business</h1>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/">Dashboard</Link>
            </li>
            <li>
              <Link to="/products">Products</Link>
            </li>
            <li>
              <Link to="/transactions">Transactions</Link>
            </li>
            <li>
              <Link to="/forecasts">Forecasts</Link>
            </li>
            <li>
              <Link to="/recommendations">Recommendations</Link>
            </li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/forecasts" element={<Forecasts />} />
            <Route path="/recommendations" element={<Recommendations />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>
            &copy; 2026 Agricultural Statistics Dashboard
        </footer>
      </div>
    </Router>
  );
}

export default App;
