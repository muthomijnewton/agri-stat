import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  LineChart, Line,
} from 'recharts'
import api from '../services/api'
import '../css/pages.css'

/* ---- SVG icons ---- */
function IconBarChart2() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
}
function IconRefresh() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
}

/* ---- Colour palette ---- */
const COLORS = ['#16a34a', '#2563eb', '#d97706', '#7c3aed', '#dc2626', '#0891b2', '#65a30d', '#db2777']
const TYPE_COLORS = { sale: '#16a34a', purchase: '#2563eb' }
const STATUS_COLORS = { pending: '#d97706', approved: '#2563eb', implemented: '#16a34a' }

/* ---- Custom tooltips ---- */
function TypeTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label" style={{ textTransform: 'capitalize' }}>{d.type}</p>
      <p>Count: <strong>{d.count}</strong></p>
      <p>Revenue: <strong>KES {Number(d.revenue).toLocaleString()}</strong></p>
      <p>Quantity: <strong>{Number(d.quantity).toLocaleString()} units</strong></p>
    </div>
  )
}

function AccuracyTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      <p style={{ color: '#2563eb' }}>Avg MAPE: <strong>{payload[0]?.value}%</strong></p>
      <p>Forecasts: <strong>{payload[0]?.payload?.count}</strong></p>
    </div>
  )
}

function StatusTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label" style={{ textTransform: 'capitalize' }}>{label}</p>
      <p>Count: <strong>{payload[0]?.value}</strong></p>
    </div>
  )
}

function TopProductsTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      <p style={{ color: '#7c3aed' }}>Qty sold: <strong>{Number(payload[0]?.value).toLocaleString()} units</strong></p>
      <p>Revenue: <strong>KES {Number(payload[0]?.payload?.revenue).toLocaleString()}</strong></p>
    </div>
  )
}

/* ---- Day-range selector ---- */
const DAY_OPTIONS = [7, 14, 30, 60, 90]

export default function Analytics() {
  const [days, setDays] = useState(30)

  const [typeSplit,    setTypeSplit]    = useState([])
  const [accuracyData, setAccuracyData] = useState([])
  const [statusData,   setStatusData]   = useState([])
  const [topProducts,  setTopProducts]  = useState([])

  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const load = async (d) => {
    try {
      setLoading(true)
      setError(null)
      const [ts, fa, rs, tp] = await Promise.all([
        api.get(`/stats/transaction-type-split?days=${d}`),
        api.get('/stats/forecast-accuracy-trend?limit=20'),
        api.get('/stats/recommendation-status-breakdown'),
        api.get(`/stats/top-products-by-quantity?days=${d}&limit=10`),
      ])
      setTypeSplit(ts.data)
      setAccuracyData(fa.data)
      setStatusData(rs.data)
      setTopProducts(tp.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(days) }, [days])

  /* ---- Summary totals from type split ---- */
  const totalRevenue  = typeSplit.reduce((s, r) => s + r.revenue, 0)
  const totalCount    = typeSplit.reduce((s, r) => s + r.count, 0)
  const totalQuantity = typeSplit.reduce((s, r) => s + r.quantity, 0)

  /* ---- Average MAPE ---- */
  const avgMape = accuracyData.length
    ? (accuracyData.reduce((s, r) => s + r.avg_mape, 0) / accuracyData.length).toFixed(1)
    : null

  return (
    <div className="container">

      {/* ── Header ── */}
      <div className="page-header">
        <div>
          <h1><IconBarChart2 /> Analytics &amp; Reports</h1>
          <p className="text-muted">Transaction trends, forecast accuracy, and inventory insights</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Day-range selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>Period:</span>
            <div style={{ display: 'flex', gap: '0.3rem' }}>
              {DAY_OPTIONS.map(d => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`btn-sm ${days === d ? 'btn-primary' : 'btn-outline'}`}
                  style={{
                    padding: '0.25rem 0.6rem',
                    fontSize: '0.8rem',
                    borderRadius: '0.375rem',
                    border: days === d ? 'none' : '1px solid #d1d5db',
                    background: days === d ? '#16a34a' : 'white',
                    color: days === d ? 'white' : '#374151',
                    cursor: 'pointer',
                  }}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>
          <button
            onClick={() => load(days)}
            className="btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <IconRefresh /> Refresh
          </button>
        </div>
      </div>

      {error && <div className="error">Error loading analytics: {error}</div>}

      {/* ── Summary KPI strip ── */}
      {!loading && (
        <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <div className="stat-card-body">
              <h3>KES {totalRevenue >= 1000 ? `${(totalRevenue / 1000).toFixed(1)}k` : totalRevenue.toFixed(0)}</h3>
              <p>Total Revenue ({days}d)</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-body">
              <h3>{totalCount.toLocaleString()}</h3>
              <p>Transactions ({days}d)</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-body">
              <h3>{totalQuantity.toLocaleString()}</h3>
              <p>Units Moved ({days}d)</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-body">
              <h3>{avgMape !== null ? `${avgMape}%` : '—'}</h3>
              <p>Avg Forecast MAPE</p>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading analytics…</div>
      ) : (
        <>
          {/* ── Row 1: Type Split + Recommendation Status ── */}
          <div className="charts-grid" style={{ marginBottom: '1.5rem' }}>

            {/* Transaction Type Split — Pie */}
            <div className="chart-card">
              <h3>Transaction Type Split — Last {days} Days</h3>
              {typeSplit.length === 0 ? (
                <div className="chart-empty">No transaction data for this period</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie
                      data={typeSplit}
                      dataKey="count"
                      nameKey="type"
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={90}
                      paddingAngle={4}
                      label={({ type, percent }) =>
                        `${type.charAt(0).toUpperCase() + type.slice(1)} ${(percent * 100).toFixed(0)}%`
                      }
                      labelLine={false}
                    >
                      {typeSplit.map((entry) => (
                        <Cell key={entry.type} fill={TYPE_COLORS[entry.type] ?? COLORS[0]} />
                      ))}
                    </Pie>
                    <Tooltip content={<TypeTooltip />} />
                    <Legend
                      formatter={(val) => (
                        <span style={{ fontSize: '0.78rem', color: '#374151', textTransform: 'capitalize' }}>{val}</span>
                      )}
                      iconSize={10}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Recommendation Status — Bar */}
            <div className="chart-card">
              <h3>Recommendation Status Breakdown</h3>
              {statusData.every(d => d.count === 0) ? (
                <div className="chart-empty">No recommendations yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={statusData} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="status"
                      tick={{ fontSize: 12, fill: '#6b7280', textTransform: 'capitalize' }}
                      tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)}
                    />
                    <YAxis
                      allowDecimals={false}
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      width={36}
                    />
                    <Tooltip content={<StatusTooltip />} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {statusData.map((entry) => (
                        <Cell key={entry.status} fill={STATUS_COLORS[entry.status] ?? '#6b7280'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* ── Row 2: Forecast Accuracy Trend + Top Products ── */}
          <div className="charts-grid">

            {/* Forecast Accuracy Trend — Line */}
            <div className="chart-card">
              <h3>Forecast Accuracy Trend (Avg MAPE %)</h3>
              <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.75rem' }}>
                Lower MAPE = more accurate forecasts
              </p>
              {accuracyData.length === 0 ? (
                <div className="chart-empty">No forecast accuracy data yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={accuracyData} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      tickFormatter={(v) => {
                        const d = new Date(v)
                        return d.toLocaleDateString('en-KE', { month: 'short', day: 'numeric' })
                      }}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      tickFormatter={(v) => `${v}%`}
                      width={44}
                    />
                    <Tooltip content={<AccuracyTooltip />} />
                    <Line
                      type="monotone"
                      dataKey="avg_mape"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={{ r: 4, fill: '#2563eb' }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Top Products by Quantity — Horizontal Bar */}
            <div className="chart-card">
              <h3>Top Products by Quantity Sold — Last {days} Days</h3>
              {topProducts.length === 0 ? (
                <div className="chart-empty">No sales data for this period</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart
                    data={topProducts}
                    layout="vertical"
                    margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}
                    />
                    <YAxis
                      type="category"
                      dataKey="product"
                      tick={{ fontSize: 11, fill: '#374151' }}
                      width={100}
                      tickFormatter={(v) => v.length > 14 ? `${v.slice(0, 13)}…` : v}
                    />
                    <Tooltip content={<TopProductsTooltip />} />
                    <Bar dataKey="quantity" radius={[0, 4, 4, 0]}>
                      {topProducts.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

          </div>
        </>
      )}
    </div>
  )
}
