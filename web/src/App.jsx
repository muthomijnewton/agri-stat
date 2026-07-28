import { BrowserRouter as Router, Routes, Route, Link, NavLink, Navigate, useNavigate } from 'react-router-dom'

import { AuthProvider, useAuth } from './context/AuthContext'
import RequireAuth from './components/RequireAuth'
import NotificationBell from './components/NotificationBell'

import Dashboard       from './pages/Dashboard'
import Products        from './pages/Products'
import Transactions    from './pages/Transactions'
import Forecasts       from './pages/Forecasts'
import Recommendations from './pages/Recommendations'
import Analytics       from './pages/Analytics'
import Login           from './pages/Login'
import Profile         from './pages/Profile'

import './css/App.css'

/* ---- Inline SVG icons (no emoji, no extra dependency) ---- */

function IconLeaf() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
    </svg>
  )
}

function IconGrid() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>
  )
}

function IconBox() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    </svg>
  )
}

function IconArrowRightLeft() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/>
    </svg>
  )
}

function IconTrendingUp() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
    </svg>
  )
}

function IconClipboard() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
    </svg>
  )
}

function IconUser() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  )
}

function IconBarChart2() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  )
}

/* ---- Navbar ---- */

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  if (!isAuthenticated) return null

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <div className="navbar-brand-icon">
          <IconLeaf />
        </div>
        <h1>AgriStat</h1>
      </Link>

      <ul className="nav-links">
        <li>
          <NavLink to="/" end>
            <IconGrid /><span>Dashboard</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/products">
            <IconBox /><span>Products</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/transactions">
            <IconArrowRightLeft /><span>Transactions</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/forecasts">
            <IconTrendingUp /><span>Forecasts</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/recommendations">
            <IconClipboard /><span>Recommendations</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/analytics">
            <IconBarChart2 /><span>Analytics</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/profile">
            <IconUser /><span>Profile</span>
          </NavLink>
        </li>
      </ul>

      <div className="nav-user">
        <NotificationBell />
        {user && (
          <Link to="/profile" className="nav-username" title="View profile">
            <IconUser />
            {user.username}
          </Link>
        )}
        <button className="btn-logout" onClick={handleLogout}>Sign out</button>
      </div>
    </nav>
  )
}

/* ---- App layout ---- */

function AppLayout() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="app">
      <Navbar />

      <main className="main-content">
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Login />
          } />

          <Route path="/"                element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/products"        element={<RequireAuth><Products /></RequireAuth>} />
          <Route path="/transactions"    element={<RequireAuth><Transactions /></RequireAuth>} />
          <Route path="/forecasts"       element={<RequireAuth><Forecasts /></RequireAuth>} />
          <Route path="/recommendations" element={<RequireAuth><Recommendations /></RequireAuth>} />
          <Route path="/analytics"       element={<RequireAuth><Analytics /></RequireAuth>} />
          <Route path="/profile"         element={<RequireAuth><Profile /></RequireAuth>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {isAuthenticated && (
        <footer className="footer">
          <p>&copy; 2026 AgriStat — Agricultural Statistics Dashboard</p>
        </footer>
      )}
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </Router>
  )
}
