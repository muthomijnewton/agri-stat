import React from 'react'
import { Link } from 'react-router-dom'
import '../styles/Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🌾 AgriStat Dashboard
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">Home</Link>
          </li>
          <li className="nav-item">
            <Link to="/products" className="nav-link">Products</Link>
          </li>
          <li className="nav-item">
            <Link to="/transactions" className="nav-link">Transactions</Link>
          </li>
          <li className="nav-item">
            <Link to="/forecasts" className="nav-link">Forecasts</Link>
          </li>
          <li className="nav-item">
            <Link to="/recommendations" className="nav-link">Recommendations</Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navbar
