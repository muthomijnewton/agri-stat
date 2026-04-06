import React, { useState, useEffect } from 'react'import React, { useEffect, useState } from 'react'












































































export default Dashboard}  )    </div>      </div>        <RecentTransactions />        <DemandChart />      <div className="dashboard-grid">      </div>        />          icon="🔮"          value={stats.recentForecasts}          title="Recent Forecasts"         <StatCard         />          icon="📊"          value={stats.totalTransactions}          title="Total Transactions"         <StatCard         />          icon="📦"          value={stats.totalProducts}          title="Total Products"         <StatCard       <div className="stats-grid">            <h1>Dashboard</h1>    <div className="dashboard">  return (  if (error) return <div className="error">{error}</div>  if (loading) return <div className="loading">Loading dashboard...</div>  }    }      setLoading(false)    } finally {      console.error(err)      setError('Failed to load dashboard data')    } catch (err) {      })        recentForecasts: forecastsRes.data.length        totalTransactions: transactionsRes.data.length,        totalProducts: productsRes.data.length,      setStats({      ])        forecastsAPI.list(0, 100)        transactionsAPI.list(0, 100),        productsAPI.list(0, 100),      const [productsRes, transactionsRes, forecastsRes] = await Promise.all([      setLoading(true)    try {  const fetchDashboardData = async () => {  }, [])    fetchDashboardData()  useEffect(() => {  const [error, setError] = useState(null)  const [loading, setLoading] = useState(true)  })    recentForecasts: 0    totalTransactions: 0,    totalProducts: 0,  const [stats, setStats] = useState({function Dashboard() {import '../styles/Dashboard.css'import DemandChart from '../components/DemandChart'import RecentTransactions from '../components/RecentTransactions'import StatCard from '../components/StatCard'import { productsAPI, transactionsAPI, forecastsAPI } from '../services/api'import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
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

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch all data in parallel
      const [productsRes, transactionsRes, recommendationsRes, forecastsRes] = await Promise.all([
        productsAPI.list(0, 100),
        transactionsAPI.list(0, 100),
        recommendationsAPI.list(0, 100),
        forecastsAPI.list(0, 100)
      ])

      // Calculate statistics
      const pendingRecs = recommendationsRes.data.filter(r => r.status === 'pending').length
      
      setStats({
        totalProducts: productsRes.data.length,
        totalTransactions: transactionsRes.data.length,
        pendingRecommendations: pendingRecs,
        activeForecasts: forecastsRes.data.length
      })

      // Prepare forecast data for chart (last 30 days)
      const sortedForecasts = forecastsRes.data
        .sort((a, b) => new Date(a.forecast_date) - new Date(b.forecast_date))
        .slice(-30)
      setForecastData(sortedForecasts.map(f => ({
        date: f.forecast_date,
        demand: f.predicted_demand,
        lower: f.confidence_lower || 0,
        upper: f.confidence_upper || 0
      })))

      // Prepare transaction trends
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

      setError(null)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data')
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
      
      {error && <div className="error-message">{error}</div>}

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
