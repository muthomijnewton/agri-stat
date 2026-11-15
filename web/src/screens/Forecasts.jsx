import { useState, useEffect } from 'react'
import { forecastsAPI, productsAPI, exportsAPI } from '../services/api'
import '../css/pages.css'

function IconSparkles() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 16, height: 16 }}>
      <path d="M12 3v1m0 16v1M4.22 4.22l.7.7m13.16 13.16.7.7M3 12h1m16 0h1M4.22 19.78l.7-.7M18.36 5.64l.7-.7" />
      <circle cx="12" cy="12" r="3" />
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

function IconBarChart() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 16, height: 16 }}>
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
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

/** Safely format accuracy_score regardless of whether it is a number or string. */
function formatAccuracy(value) {
  if (value === null || value === undefined || value === '') return 'N/A'
  const num = typeof value === 'number' ? value : parseFloat(value)
  return isNaN(num) ? 'N/A' : `${num.toFixed(2)}%`
}

export default function Forecasts() {
  const [forecasts, setForecasts] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [selectedProduct, setSelectedProduct] = useState('')

  // Generate panel state
  const [genProduct, setGenProduct] = useState('')
  const [genModel, setGenModel] = useState('auto')
  const [generating, setGenerating] = useState(false)
  const [exporting, setExporting] = useState(false)

  // Batch generate state
  const [batchOpen,    setBatchOpen]    = useState(false)
  const [batchModel,   setBatchModel]   = useState('auto')
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchResults, setBatchResults] = useState(null)  // null = not run yet

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [fcsts, prods] = await Promise.all([
        forecastsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setForecasts(fcsts.data)
      setProducts(prods.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!genProduct) return
    try {
      setGenerating(true)
      setError(null)
      setSuccessMsg(null)
      const res = await forecastsAPI.generate(parseInt(genProduct), genModel)
      setSuccessMsg(
        `${res.data.message} — ${res.data.periods_generated} day(s) generated using ${res.data.model_used.toUpperCase()}.`
      )
      // Refresh the table so new rows appear
      await fetchData()
      setTimeout(() => setSuccessMsg(null), 5000)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setGenerating(false)
    }
  }

  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId)
    return product ? product.name : 'Unknown'
  }

  const filteredForecasts = selectedProduct
    ? forecasts.filter((f) => f.product_id === parseInt(selectedProduct))
    : forecasts

  const handleExport = async () => {
    try {
      setExporting(true)
      const filters = {}
      if (selectedProduct) filters.product_id = selectedProduct
      await exportsAPI.forecasts(filters)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setExporting(false)
    }
  }

  const handleGenerateAll = async () => {
    try {
      setBatchRunning(true)
      setBatchResults(null)
      setError(null)
      const res = await forecastsAPI.generateAll(batchModel)
      setBatchResults(res.data)
      await fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setBatchRunning(false)
    }
  }

  if (loading && forecasts.length === 0)
    return <div className="loading">Loading forecasts...</div>

  return (
    <div className="container">
      <div className="page-header">
        <h1>Demand Forecasts</h1>
        <button
          className="btn-secondary"
          onClick={handleExport}
          disabled={exporting}
          title="Export forecasts as CSV"
        >
          <IconDownload /> {exporting ? 'Exporting…' : 'Export CSV'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

      {/* ── Generate Forecast Panel ── */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '0.9375rem', color: 'var(--gray-800)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <IconSparkles /> Generate New Forecast
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
            <div className="form-group">
              <label>Model</label>
              <select value={genModel} onChange={(e) => setGenModel(e.target.value)}>
                <option value="auto">Auto (Prophet → ARIMA fallback)</option>
                <option value="prophet">Prophet</option>
                <option value="arima">ARIMA</option>
              </select>
            </div>
            <div className="form-group" style={{ flexShrink: 0, alignSelf: 'flex-end' }}>
              <button
                type="submit"
                className="btn-primary"
                disabled={generating || !genProduct}
                style={{ width: '100%' }}
              >
                {generating ? 'Generating…' : <><IconZap /> Generate Forecast</>}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* ── Batch Generate Panel ── */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        {/* Collapsible header */}
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
              Run forecast generation for every active product in one click.
              Products with insufficient history (&lt; 10 transactions) are skipped automatically.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
              <div className="form-group" style={{ marginBottom: 0, minWidth: 220 }}>
                <label>Model</label>
                <select value={batchModel} onChange={e => setBatchModel(e.target.value)} disabled={batchRunning}>
                  <option value="auto">Auto (Prophet → ARIMA fallback)</option>
                  <option value="prophet">Prophet</option>
                  <option value="arima">ARIMA</option>
                </select>
              </div>
              <button
                type="button"
                className="btn-primary"
                onClick={handleGenerateAll}
                disabled={batchRunning}
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                {batchRunning
                  ? <><span className="spinner-inline" /> Running…</>
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

            {/* Progress / results log */}
            {batchRunning && !batchResults && (
              <div className="batch-log" style={{ marginTop: '1rem' }}>
                <p className="batch-log-running">⏳ Generating forecasts for all products — this may take a moment…</p>
              </div>
            )}

            {batchResults && (
              <div style={{ marginTop: '1rem' }}>
                {/* Summary strip */}
                <div className="batch-summary">
                  <span className="batch-stat batch-stat--total">
                    {batchResults.summary.total_products} products
                  </span>
                  <span className="batch-stat batch-stat--success">
                    ✓ {batchResults.summary.succeeded} succeeded
                  </span>
                  {batchResults.summary.skipped > 0 && (
                    <span className="batch-stat batch-stat--skip">
                      — {batchResults.summary.skipped} skipped
                    </span>
                  )}
                  {batchResults.summary.failed > 0 && (
                    <span className="batch-stat batch-stat--error">
                      ✗ {batchResults.summary.failed} failed
                    </span>
                  )}
                  <span className="batch-stat batch-stat--periods">
                    {batchResults.summary.total_periods} total periods
                  </span>
                </div>

                {/* Per-product log */}
                <ul className="batch-log">
                  {batchResults.results.map((r) => (
                    <li key={r.product_id} className={`batch-log-item batch-log-item--${r.status}`}>
                      <span className="batch-log-status">
                        {r.status === 'success' ? '✓' : r.status === 'skipped' ? '—' : '✗'}
                      </span>
                      <span className="batch-log-name">{r.product_name}</span>
                      <span className="batch-log-msg">{r.message}</span>
                      {r.status === 'success' && (
                        <span className="badge badge-secondary" style={{ fontSize: '0.7rem', textTransform: 'uppercase' }}>
                          {r.model_used}
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

      {/* ── Filter ── */}
      <div className="card filters">        <label>Filter by Product:</label>
        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
          <option value="">All Products</option>
          {products.map((product) => (
            <option key={product.id} value={product.id}>
              {product.name}
            </option>
          ))}
        </select>
      </div>

      {/* ── Table ── */}
      <div className="table-responsive">
        <table className="card">
          <thead>
            <tr>
              <th>Product</th>
              <th>Forecast Date</th>
              <th>Predicted Demand</th>
              <th>Lower Bound</th>
              <th>Upper Bound</th>
              <th>Model</th>
              <th>Accuracy (MAPE)</th>
            </tr>
          </thead>
          <tbody>
            {filteredForecasts.map((forecast) => (
              <tr key={forecast.id}>
                <td>{getProductName(forecast.product_id)}</td>
                <td>{new Date(forecast.forecast_date).toLocaleDateString()}</td>
                <td className="text-strong">{forecast.predicted_demand}</td>
                <td>{forecast.confidence_lower ?? '-'}</td>
                <td>{forecast.confidence_upper ?? '-'}</td>
                <td>
                  <span className="badge badge-secondary" style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>
                    {forecast.model_type || 'N/A'}
                  </span>
                </td>
                <td>{formatAccuracy(forecast.accuracy_score)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredForecasts.length === 0 && !loading && (
        <div className="card text-center">
          <p className="text-muted">
            {selectedProduct
              ? 'No forecasts available for this product.'
              : 'No forecasts generated yet. Use the panel above to generate one!'}
          </p>
        </div>
      )}

      <div className="card info-box">
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <IconBarChart /> How Forecasting Works
        </h3>
        <p>The system uses advanced time-series forecasting models to predict future demand:</p>
        <ul>
          <li><strong>Prophet:</strong> Developed by Facebook, great for seasonal patterns</li>
          <li><strong>ARIMA:</strong> Classical approach for trend-based forecasting</li>
          <li><strong>Auto:</strong> Tries Prophet first, falls back to ARIMA if needed</li>
          <li><strong>Confidence Intervals:</strong> Shows the range of likely demand values</li>
          <li><strong>Accuracy Score:</strong> MAPE (Mean Absolute Percentage Error) of the model</li>
        </ul>
      </div>
    </div>
  )
}
