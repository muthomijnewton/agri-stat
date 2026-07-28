import { useState, useEffect } from 'react'
import { recommendationsAPI, productsAPI, exportsAPI } from '../services/api'
import '../css/pages.css'

function IconCheck() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function IconX() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

function IconInfo() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 16, height: 16 }}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="8" />
      <line x1="12" y1="12" x2="12" y2="16" />
    </svg>
  )
}

function IconDownload() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="7 10 12 15 17 10"/>
      <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  )
}

function IconZap() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  )
}

function IconZapAll() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
      <line x1="20" y1="2" x2="20" y2="6" /><line x1="22" y1="4" x2="18" y2="4" />
    </svg>
  )
}

function IconChevron({ open }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ width: 14, height: 14, transition: 'transform 0.2s', transform: open ? 'rotate(180deg)' : 'none' }}>
      <polyline points="6 9 12 15 18 9" />
    </svg>
  )
}

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [exporting, setExporting] = useState(false)

  // Generate single
  const [genProduct,   setGenProduct]   = useState('')
  const [generating,   setGenerating]   = useState(false)

  // Batch generate
  const [batchOpen,    setBatchOpen]    = useState(false)
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchResults, setBatchResults] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [recs, prods] = await Promise.all([
        recommendationsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setRecommendations(recs.data)
      setProducts(prods.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId)
    return product ? product.name : 'Unknown'
  }

  // â”€â”€ Generate single â”€â”€
  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!genProduct) return
    try {
      setGenerating(true)
      setError(null)
      setSuccessMsg(null)
      const res = await recommendationsAPI.generate(parseInt(genProduct))
      setSuccessMsg(`${res.data.message} â€” ${res.data.recommended_quantity} units recommended.`)
      await fetchData()
      setTimeout(() => setSuccessMsg(null), 5000)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setGenerating(false)
    }
  }

  // â”€â”€ Batch generate all â”€â”€
  const handleGenerateAll = async () => {
    try {
      setBatchRunning(true)
      setBatchResults(null)
      setError(null)
      const res = await recommendationsAPI.generateAll()
      setBatchResults(res.data)
      await fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setBatchRunning(false)
    }
  }

  const handleApprove = async (id) => {
    try {
      await recommendationsAPI.approve(id)
      setSuccessMsg('Recommendation approved!')
      fetchData()
      setTimeout(() => setSuccessMsg(null), 3000)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const handleImplement = async (id) => {
    try {
      await recommendationsAPI.implement(id)
      setSuccessMsg('Recommendation marked as implemented!')
      fetchData()
      setTimeout(() => setSuccessMsg(null), 3000)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this recommendation?')) {
      try {
        await recommendationsAPI.delete(id)
        setSuccessMsg('Recommendation deleted!')
        fetchData()
        setTimeout(() => setSuccessMsg(null), 3000)
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message)
      }
    }
  }

  const filteredRecs =
    statusFilter === 'all'
      ? recommendations
      : recommendations.filter((r) => r.status === statusFilter)

  const handleExport = async () => {
    try {
      setExporting(true)
      const filters = {}
      if (statusFilter !== 'all') filters.status = statusFilter
      await exportsAPI.recommendations(filters)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setExporting(false)
    }
  }

  if (loading && recommendations.length === 0)
    return <div className="loading">Loading recommendations...</div>

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'pending':     return 'badge-warning'
      case 'approved':    return 'badge-info'
      case 'implemented': return 'badge-success'
      default:            return 'badge-secondary'
    }
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Inventory Recommendations</h1>
        <button
          className="btn-secondary"
          onClick={handleExport}
          disabled={exporting}
          title="Export recommendations as CSV"
        >
          <IconDownload /> {exporting ? 'Exportingâ€¦' : 'Export CSV'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

      {/* â”€â”€ Generate Single Recommendation Panel â”€â”€ */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '0.9375rem', color: 'var(--gray-800)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <IconZap /> Generate New Recommendation
        </h3>
        <form onSubmit={handleGenerate}>
          <div className="form-row">
            <div className="form-group">
              <label>Product *</label>
              <select
                value={genProduct}
                onChange={(e) => setGenProduct(e.target.value)}
                required
              >
                <option value="">Select a product</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ flexShrink: 0, alignSelf: 'flex-end' }}>
              <button
                type="submit"
                className="btn-primary"
                disabled={generating || !genProduct}
                style={{ width: '100%' }}
              >
                {generating
                  ? <><span className="spinner-inline" /> Generatingâ€¦</>
                  : <><IconZap /> Generate</>}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* â”€â”€ Batch Generate All Panel â”€â”€ */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <button
          type="button"
          onClick={() => setBatchOpen(o => !o)}
          style={{
            width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            background: 'none', border: 'none', cursor: 'pointer', padding: 0,
            fontSize: '0.9375rem', fontWeight: 600, color: 'var(--gray-800)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <IconZapAll /> Generate All Products
          </span>
          <IconChevron open={batchOpen} />
        </button>

        {batchOpen && (
          <div style={{ marginTop: '1rem' }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Generate recommendations for every active product in one click.
              Products with no forecasts are skipped automatically.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn-primary"
                onClick={handleGenerateAll}
                disabled={batchRunning}
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                {batchRunning
                  ? <><span className="spinner-inline" /> Runningâ€¦</>
                  : <><IconZapAll /> Generate All</>}
              </button>
              {batchResults && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setBatchResults(null)}
                  style={{ fontSize: '0.8rem' }}
                >
                  Clear Log
                </button>
              )}
            </div>

            {batchRunning && !batchResults && (
              <div className="batch-log" style={{ marginTop: '1rem' }}>
                <p className="batch-log-running">â³ Generating recommendations for all productsâ€¦</p>
              </div>
            )}

            {batchResults && (
              <div style={{ marginTop: '1rem' }}>
                <div className="batch-summary">
                  <span className="batch-stat batch-stat--total">
                    {batchResults.summary.total_products} products
                  </span>
                  <span className="batch-stat batch-stat--success">
                    âœ“ {batchResults.summary.succeeded} succeeded
                  </span>
                  {batchResults.summary.skipped > 0 && (
                    <span className="batch-stat batch-stat--skip">
                      â€” {batchResults.summary.skipped} skipped
                    </span>
                  )}
                  {batchResults.summary.failed > 0 && (
                    <span className="batch-stat batch-stat--error">
                      âœ— {batchResults.summary.failed} failed
                    </span>
                  )}
                </div>

                <ul className="batch-log">
                  {batchResults.results.map((r) => (
                    <li key={r.product_id} className={`batch-log-item batch-log-item--${r.status}`}>
                      <span className="batch-log-status">
                        {r.status === 'success' ? 'âœ“' : r.status === 'skipped' ? 'â€”' : 'âœ—'}
                      </span>
                      <span className="batch-log-name">{r.product_name}</span>
                      <span className="batch-log-msg">{r.message}</span>
                      {r.status === 'success' && (
                        <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                          {r.recommended_quantity} units
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* â”€â”€ Filter â”€â”€ */}
      <div className="card filters">
        <label>Filter by Status:</label>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="implemented">Implemented</option>
        </select>
      </div>

      <div className="recommendations-grid">
        {filteredRecs.map((rec) => (
          <div key={rec.id} className={`recommendation-card card ${rec.status}`}>
            <div className="card-header">
              <h3>{getProductName(rec.product_id)}</h3>
              <span className={`badge ${getStatusBadgeColor(rec.status)}`}>
                {rec.status}
              </span>
            </div>

            <div className="card-body">
              <div className="metric">
                <span className="label">Recommended Quantity:</span>
                <span className="value">{rec.recommended_quantity} units</span>
              </div>

              <div className="metric">
                <span className="label">Current Quantity:</span>
                <span className="value">{rec.current_quantity || 'N/A'}</span>
              </div>

              {rec.min_quantity && (
                <div className="metric">
                  <span className="label">Minimum Stock:</span>
                  <span className="value">{rec.min_quantity}</span>
                </div>
              )}

              {rec.max_quantity && (
                <div className="metric">
                  <span className="label">Maximum Capacity:</span>
                  <span className="value">{rec.max_quantity}</span>
                </div>
              )}

              <div className="metric">
                <span className="label">Date:</span>
                <span className="value">
                  {new Date(rec.recommendation_date).toLocaleDateString()}
                </span>
              </div>

              {rec.reason && (
                <div className="metric" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span className="label">Reason:</span>
                  <p className="reason-text">{rec.reason}</p>
                </div>
              )}
            </div>

            <div className="card-actions">
              {rec.status === 'pending' && (
                <>
                  <button className="btn-primary" onClick={() => handleApprove(rec.id)}>
                    <IconCheck /> Approve
                  </button>
                  <button className="btn-danger" onClick={() => handleDelete(rec.id)}>
                    <IconX /> Delete
                  </button>
                </>
              )}

              {rec.status === 'approved' && (
                <button className="btn-primary" onClick={() => handleImplement(rec.id)}>
                  <IconCheck /> Mark as Implemented
                </button>
              )}

              {rec.status === 'implemented' && (
                <button className="btn-danger" onClick={() => handleDelete(rec.id)}>
                  <IconX /> Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredRecs.length === 0 && !loading && (
        <div className="card text-center">
          <p className="text-muted">
            {statusFilter === 'all'
              ? 'No recommendations yet. Use the panel above to generate one!'
              : `No ${statusFilter} recommendations.`}
          </p>
        </div>
      )}

      <div className="card info-box">
        <h3><IconInfo /> About Recommendations</h3>
        <p>
          Recommendations are calculated based on:
        </p>
        <ul>
          <li>Recent demand forecasts</li>
          <li>Supply lead times (typically 3 days)</li>
          <li>Safety stock calculations (1.5Ã— multiplier)</li>
          <li>Current inventory levels</li>
        </ul>
        <p>
          <strong>Formula:</strong> Avg Daily Demand Ã— 3 days Ã— 1.5 safety factor
        </p>
        <p>
          <strong>Workflow:</strong> Pending â†’ Approve â†’ Implement
        </p>
      </div>
    </div>
  )
}
