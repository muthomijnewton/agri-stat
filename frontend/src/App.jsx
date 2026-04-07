import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Transactions from './pages/Transactions'
import Forecasts from './pages/Forecasts'
import Recommendations from './pages/Recommendations'
import Login from './pages/Login'
import './styles/App.css'

// Protected Route Component
function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const user = localStorage.getItem('isAuthenticated')
    if (user === 'true') {
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('user')
    localStorage.removeItem('isAuthenticated')
    setIsAuthenticated(false)
  }

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</div>
  }

  return (
    <Router>
      <div className="app">
        {isAuthenticated && <Navbar onLogout={handleLogout} />}
        <main className="main-content">
          <Routes>
            <Route path="/login" element={
              isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
            } />
            <Route path="/" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Products />
              </ProtectedRoute>
            } />
            <Route path="/transactions" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Transactions />
              </ProtectedRoute>
            } />
            <Route path="/forecasts" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Forecasts />
              </ProtectedRoute>
            } />
            <Route path="/recommendations" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Recommendations />
              </ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
