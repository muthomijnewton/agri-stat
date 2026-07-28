import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import api, { recommendationsAPI, productsAPI } from '../services/api'
import '../css/pages.css'

/* ---- SVG icons ---- */
function IconBox() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
}
function IconArrowRightLeft() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>
}
function IconTrendingUp() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
}
function IconAlertCircle() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
}
function IconThumbsUp() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
}
function IconCheckCircle() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
}
function IconDatabase() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
}
function IconListOrdered() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg>
}
function IconAlertTriangle() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 16, height: 16, flexShrink: 0 }}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
}

/* ---- Pie chart colour palette ---- */
const PIE_COLORS = ['#16a34a','#2563eb','#d97706','#7c3aed','#dc2626','#0891b2','#65a30d','#db2777','#ea580c','#4f46e5']

/* ---- Tooltip formatters ---- */
function RevenueTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      <p style={{ color: '#16a34a' }}>Revenue: KES {Number(payload[0]?.value).toLocaleString()}</p>
    </div>
  )
}

function PieTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{payload[0].name}</p>
      <p style={{ color: payload[0].payload.fill }}>KES {Number(payload[0].value).toLocaleString()}</p>
    </div>
  )
}

/* ---- Axis tick: shorten date to "Jul 28" ---- */
function shortDate(str) {
  if (!str) return ''
  const d = new Date(str)
  return d.toLocaleDateString('en-KE', { month: 'short', day: 'numeric' })
}

export default function Dashboard() {
  const [stats,       setStats]       = useState({ total_products: 0, total_transactions: 0, total_forecasts: 0, pending_recommendations: 0, approved_recommendations: 0, implemented_recommendations: 0 })
  const [dailyData,   setDailyData]   = useState([])
  const [productData, setProductData] = useState([])
  const [lowStock,    setLowStock]    = useState([])
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        const [s, d, p, recs, prods] = await Promise.all([
          api.get('/stats/summary'),
          api.get('/stats/transactions-daily?days=30'),
          api.get('/stats/revenue-by-product?days=30'),
          recommendationsAPI.getAll(0, 100),
          productsAPI.getAll(0, 100),
        ])
        setStats(s.data)
        setDailyData(d.data)
        setProductData(p.data)

        // Flag recommendations where current stock is below minimum
        const productMap = Object.fromEntries(prods.data.map(p => [p.id, p.name]))
        const alerts = recs.data.filter(
          r => r.min_quantity != null &&
               r.current_quantity != null &&
               r.current_quantity < r.min_quantity
        ).map(r => ({
          id:               r.id,
          name:             productMap[r.product_id] ?? `Product #${r.product_id}`,
          current_quantity: r.current_quantity,
          min_quantity:     r.min_quantity,
          status:           r.status,
        }))
        setLowStock(alerts)
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="loading">Loading dashboard…</div>
  if (error)   return <div className="error">Error: {error}</div>

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="text-muted">Agricultural supply chain overview — last 30 days</p>
        </div>
      </div>

      {/* ── Low Stock Alert Banner ── */}
      {lowStock.length > 0 && (
        <div className="low-stock-banner">
          <div className="low-stock-banner__header">
            <IconAlertTriangle />
            <strong>{lowStock.length} product{lowStock.length > 1 ? 's' : ''} below minimum stock level</strong>
          </div>
          <ul className="low-stock-banner__list">
            {lowStock.map(item => (
              <li key={item.id} className="low-stock-banner__item">
                <span className="low-stock-banner__name">{item.name}</span>
                <span className="low-stock-banner__qty">
                  {item.current_quantity} / {item.min_quantity} min
                </span>
                <span className={`badge ${item.status === 'pending' ? 'badge-warning' : item.status === 'approved' ? 'badge-info' : 'badge-success'}`}>
                  {item.status}
                </span>
              </li>
            ))}
          </ul>
          <a href="/recommendations" className="low-stock-banner__link">
            View Recommendations →
          </a>
        </div>
      )}

      {/* ── KPI Cards ── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-icon green"><IconBox /></div>
          <div className="stat-card-body">
            <h3>{stats.total_products}</h3>
            <p>Total Products</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon blue"><IconArrowRightLeft /></div>
          <div className="stat-card-body">
            <h3>{stats.total_transactions}</h3>
            <p>Total Transactions</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon purple"><IconTrendingUp /></div>
          <div className="stat-card-body">
            <h3>{stats.total_forecasts}</h3>
            <p>Active Forecasts</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon amber"><IconAlertCircle /></div>
          <div className="stat-card-body">
            <h3>{stats.pending_recommendations}</h3>
            <p>Pending Recommendations</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon blue"><IconThumbsUp /></div>
          <div className="stat-card-body">
            <h3>{stats.approved_recommendations}</h3>
            <p>Approved Recommendations</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon green"><IconCheckCircle /></div>
          <div className="stat-card-body">
            <h3>{stats.implemented_recommendations}</h3>
            <p>Implemented Recommendations</p>
          </div>
        </div>
      </div>

      {/* ── Charts ── */}
      <div className="charts-grid">

        {/* Daily Revenue Bar Chart */}
        <div className="chart-card">
          <h3>Daily Revenue (KES) — Last 30 Days</h3>
          {dailyData.length === 0 ? (
            <div className="chart-empty">No transaction data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={dailyData} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tickFormatter={shortDate}
                  tick={{ fontSize: 11, fill: '#6b7280' }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#6b7280' }}
                  tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v}
                  width={42}
                />
                <Tooltip content={<RevenueTooltip />} />
                <Bar dataKey="revenue" fill="#16a34a" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Revenue by Product Pie Chart */}
        <div className="chart-card">
          <h3>Revenue by Product (KES) — Last 30 Days</h3>
          {productData.length === 0 ? (
            <div className="chart-empty">No transaction data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={productData}
                  dataKey="revenue"
                  nameKey="product"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={false}
                >
                  {productData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
                <Legend
                  formatter={(val) => <span style={{ fontSize: '0.75rem', color: '#374151' }}>{val}</span>}
                  iconSize={10}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

      </div>

      {/* ── Overview + Getting Started ── */}
      <div className="overview-grid">
        <div className="overview-card">
          <h3><IconDatabase />Platform Overview</h3>
          <ul>
            <li>Manage product inventory and transaction records</li>
            <li>Forecast demand using Prophet &amp; ARIMA models</li>
            <li>Receive intelligent inventory recommendations</li>
            <li>Monitor trends and reduce agricultural waste</li>
          </ul>
        </div>
        <div className="overview-card">
          <h3><IconListOrdered />Getting Started</h3>
          <ol>
            <li>Add your agricultural products in <strong>Products</strong></li>
            <li>Record sales and purchases in <strong>Transactions</strong></li>
            <li>View demand predictions in <strong>Forecasts</strong></li>
            <li>Review and approve inventory <strong>Recommendations</strong></li>
          </ol>
        </div>
      </div>
    </div>
  )
}
