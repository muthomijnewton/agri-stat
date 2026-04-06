import { useState, useEffect } from 'react'
import { productsAPI, transactionsAPI, forecastsAPI, recommendationsAPI } from '../services/api'
import '../css/pages.css'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalTransactions: 0,
    recentForecasts: 0,
    pendingRecommendations: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const [products, transactions, forecasts, recommendations] = await Promise.all([
          productsAPI.getAll(0, 100),
          transactionsAPI.getAll(0, 100),
          forecastsAPI.getAll(0, 100),
          recommendationsAPI.getAll(0, 100),
        ])

        setStats({
          totalProducts: products.data.length,
          totalTransactions: transactions.data.length,
          recentForecasts: forecasts.data.length,
          pendingRecommendations: recommendations.data.filter(r => r.status === 'pending').length,
        })
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) return <div className="loading">Loading dashboard...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="container">
      <h1>Dashboard</h1>
      <p className="text-muted">Welcome to the Agricultural Statistics Dashboard</p>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.totalProducts}</h3>
          <p>Total Products</p>
          <span className="stat-icon">🌾</span>
        </div>

        <div className="stat-card">
          <h3>{stats.totalTransactions}</h3>
          <p>Total Transactions</p>
          <span className="stat-icon">📊</span>
        </div>

        <div className="stat-card">
          <h3>{stats.recentForecasts}</h3>
          <p>Recent Forecasts</p>
          <span className="stat-icon">📈</span>
        </div>

        <div className="stat-card pending">
          <h3>{stats.pendingRecommendations}</h3>
          <p>Pending Recommendations</p>
          <span className="stat-icon">⚠️</span>
        </div>
      </div>

      <div className="card mt-20">
        <h2>Overview</h2>
        <p>This dashboard helps agricultural distributors:</p>
        <ul>
          <li>📦 Manage product inventory and transaction records</li>
          <li>📊 Forecast demand using advanced statistical models (Prophet & ARIMA)</li>
          <li>💡 Receive intelligent inventory recommendations</li>
          <li>📉 Monitor trends and reduce agricultural waste</li>
        </ul>
      </div>

      <div className="card">
        <h2>Getting Started</h2>
        <ol>
          <li>Add your agricultural products in the <strong>Products</strong> section</li>
          <li>Record sales and transactions in the <strong>Transactions</strong> section</li>
          <li>View demand predictions in the <strong>Forecasts</strong> section</li>
          <li>Review and approve inventory recommendations</li>
        </ol>
      </div>
    </div>
  )
}
