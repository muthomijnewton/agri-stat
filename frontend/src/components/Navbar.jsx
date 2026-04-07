import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/Navbar.css";

function Navbar({ onLogout }) {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    if (onLogout) {
      onLogout();
    }
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🌾 AgriStat
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/products" className="nav-link">
              Products
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/transactions" className="nav-link">
              Transactions
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/forecasts" className="nav-link">
              Forecasts
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/recommendations" className="nav-link">
              Recommendations
            </Link>
          </li>
          <li className="nav-item user-info">
            <span className="username">{user.username || 'User'}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
