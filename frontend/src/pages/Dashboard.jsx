import React, { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import StatCard from '../components/StatCard'
import RecentTransactions from '../components/RecentTransactions'
import DemandChart from '../components/DemandChart'
import { productsAPI, transactionsAPI, forecastsAPI, recommendationsAPI } from '../services/api'
import '../styles/Dashboard.css'

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1']

function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalTransactions: 0,
    pendingRecommendations: 0,
    activeForecasts: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [forecastData, setForecastData] = useState([])
  const [transactionTrends, setTransactionTrends] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  // Mock data for demonstration and testing
  const MOCK_STATS = {
    totalProducts: 24,
    totalTransactions: 156,
    pendingRecommendations: 8,
    activeForecasts: 12
  }

  const MOCK_FORECAST_DATA = [
    { date: '2024-03-07', demand: 120, lower: 100, upper: 140 },
    { date: '2024-03-08', demand: 135, lower: 115, upper: 155 },
    { date: '2024-03-09', demand: 145, lower: 125, upper: 165 },
    { date: '2024-03-10', demand: 130, lower: 110, upper: 150 },
    { date: '2024-03-11', demand: 155, lower: 135, upper: 175 },
    { date: '2024-03-12', demand: 165, lower: 145, upper: 185 },
    { date: '2024-03-13', demand: 150, lower: 130, upper: 170 },
    { date: '2024-03-14', demand: 175, lower: 155, upper: 195 },
    { date: '2024-03-15', demand: 185, lower: 165, upper: 205 },
    { date: '2024-03-16', demand: 170, lower: 150, upper: 190 }
  ]

  const MOCK_TRANSACTION_TRENDS = [
    { date: '2024-03-07', quantity: 45, revenue: 2250 },
    { date: '2024-03-08', quantity: 52, revenue: 2600 },
    { date: '2024-03-09', quantity: 48, revenue: 2400 },
    { date: '2024-03-10', quantity: 65, revenue: 3250 },
    { date: '2024-03-11', quantity: 70, revenue: 3500 },
    { date: '2024-03-12', quantity: 58, revenue: 2900 },
    { date: '2024-03-13', quantity: 72, revenue: 3600 },
    { date: '2024-03-14', quantity: 85, revenue: 4250 },
    { date: '2024-03-15', quantity: 78, revenue: 3900 },
    { date: '2024-03-16', quantity: 62, revenue: 3100 }
  ]

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch all data in parallel with timeout
      const fetchWithTimeout = (promise, timeout = 5000) => {
        return Promise.race([
          promise,
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), timeout)
          )
        ])
      }

      const [productsRes, transactionsRes, recommendationsRes, forecastsRes] = await Promise.all([
        fetchWithTimeout(productsAPI.list(0, 100)),
        fetchWithTimeout(transactionsAPI.list(0, 100)),
        fetchWithTimeout(recommendationsAPI.list(0, 100)),
        fetchWithTimeout(forecastsAPI.list(0, 100))
      ])

      // Calculate statistics from real data
      const pendingRecs = recommendationsRes.data?.filter(r => r.status === 'pending').length || 0
      
      setStats({
        totalProducts: productsRes.data?.length || 0,
        totalTransactions: transactionsRes.data?.length || 0,
        pendingRecommendations: pendingRecs,
        activeForecasts: forecastsRes.data?.length || 0
      })

      // Prepare forecast data for chart (last 30 days)
      if (forecastsRes.data && forecastsRes.data.length > 0) {
        const sortedForecasts = forecastsRes.data
          .sort((a, b) => new Date(a.forecast_date) - new Date(b.forecast_date))
          .slice(-30)
        setForecastData(sortedForecasts.map(f => ({
          date: f.forecast_date,
          demand: f.predicted_demand,
          lower: f.confidence_lower || 0,
          upper: f.confidence_upper || 0
        })))
      } else {
        setForecastData(MOCK_FORECAST_DATA)
      }

      // Prepare transaction trends
      if (transactionsRes.data && transactionsRes.data.length > 0) {
        const transactions = transactionsRes.data
          .sort((a, b) => new Date(a.transaction_date) - new Date(b.transaction_date))
          .slice(-30)
        
        const grouped = {}
        transactions.forEach(t => {
          const date = t.transaction_date
          if (!grouped[date]) {
            grouped[date] = { date, quantity: 0, revenue: 0 }
          }
          grouped[date].quantity += t.quantity
          grouped[date].revenue += parseFloat(t.total_price || 0)
        })

        setTransactionTrends(Object.values(grouped))
      } else {
        setTransactionTrends(MOCK_TRANSACTION_TRENDS)
      }

      // If real data is empty, use mock data for stats
      if (!productsRes.data?.length && !transactionsRes.data?.length) {
        setStats(MOCK_STATS)
      }

    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      console.warn('Using mock data for display')
      
      // Use mock data on error
      setStats(MOCK_STATS)
      setForecastData(MOCK_FORECAST_DATA)
      setTransactionTrends(MOCK_TRANSACTION_TRENDS)
      setError('Using demo data (API unavailable) - ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="dashboard loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard">
      <h1>Agricultural Statistics Dashboard</h1>
      
      {error && <div className="error-message" style={{backgroundColor: '#fff3cd', color: '#856404', padding: '10px 15px', borderRadius: '4px', marginBottom: '20px'}}>
        ℹ️ {error}
      </div>}

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p className="stat-value">{stats.totalProducts}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{stats.totalTransactions}</p>
        </div>
        <div className="stat-card">
          <h3>Pending Recommendations</h3>
          <p className="stat-value warning">{stats.pendingRecommendations}</p>
        </div>
        <div className="stat-card">
          <h3>Active Forecasts</h3>
          <p className="stat-value">{stats.activeForecasts}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Demand Forecast Chart */}
        <div className="chart-container">
          <h2>30-Day Demand Forecast</h2>
          {forecastData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={forecastData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="demand" stroke="#8884d8" name="Predicted Demand" />
                <Line type="monotone" dataKey="upper" stroke="#82ca9d" strokeDasharray="5 5" name="Upper Bound" />
                <Line type="monotone" dataKey="lower" stroke="#ffc658" strokeDasharray="5 5" name="Lower Bound" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No forecast data available</p>
          )}
        </div>

        {/* Transaction Trends Chart */}
        <div className="chart-container">
          <h2>Transaction Trends (Last 30 Days)</h2>
          {transactionTrends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={transactionTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="quantity" fill="#8884d8" name="Quantity Sold" />
                <Bar dataKey="revenue" fill="#82ca9d" name="Revenue" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No transaction data available</p>
          )}
        </div>
      </div>

      <button onClick={fetchDashboardData} className="refresh-btn">
        🔄 Refresh Data
      </button>
    </div>
  )
}

export default Dashboard

