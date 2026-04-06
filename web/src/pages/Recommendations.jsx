import { useState, useEffect } from 'react'
import { recommendationsAPI, productsAPI } from '../services/api'
import '../css/pages.css'

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [recs, prods] = await Promise.all([
        recommendationsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setRecommendations(recs.data)
      setProducts(prods.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId)
    return product ? product.name : 'Unknown'
  }

  const handleApprove = async (id) => {
    try {
      await recommendationsAPI.approve(id)
      setSuccessMsg('Recommendation approved!')
      fetchData()
      setTimeout(() => setSuccessMsg(null), 3000)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleImplement = async (id) => {
    try {
      await recommendationsAPI.implement(id)
      setSuccessMsg('Recommendation marked as implemented!')
      fetchData()
      setTimeout(() => setSuccessMsg(null), 3000)
    } catch (err) {
      setError(err.message)
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
        setError(err.message)
      }
    }
  }

  const filteredRecs =
    statusFilter === 'all'
      ? recommendations
      : recommendations.filter((r) => r.status === statusFilter)

  if (loading && recommendations.length === 0)
    return <div className="loading">Loading recommendations...</div>

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'pending':
        return 'badge-warning'
      case 'approved':
        return 'badge-info'
      case 'implemented':
        return 'badge-success'
      default:
        return 'badge-secondary'
    }
  }

  return (
    <div className="container">
      <h1>Inventory Recommendations</h1>

      {error && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

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
          <div key={rec.id} className="recommendation-card card">
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
                <div className="metric">
                  <span className="label">Reason:</span>
                  <p className="reason-text">{rec.reason}</p>
                </div>
              )}
            </div>

            <div className="card-actions">
              {rec.status === 'pending' && (
                <>
                  <button className="btn-primary" onClick={() => handleApprove(rec.id)}>
                    ✓ Approve
                  </button>
                  <button className="btn-danger" onClick={() => handleDelete(rec.id)}>
                    ✕ Delete
                  </button>
                </>
              )}

              {rec.status === 'approved' && (
                <button className="btn-primary" onClick={() => handleImplement(rec.id)}>
                  ✓ Mark as Implemented
                </button>
              )}

              {rec.status === 'implemented' && (
                <button className="btn-danger" onClick={() => handleDelete(rec.id)}>
                  ✕ Delete
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
              ? 'No recommendations available yet.'
              : `No ${statusFilter} recommendations.`}
          </p>
        </div>
      )}

      <div className="card info-box">
        <h3>💡 About Recommendations</h3>
        <p>
          Recommendations are automatically generated based on:
        </p>
        <ul>
          <li>Recent demand forecasts</li>
          <li>Supply lead times (typically 3 days)</li>
          <li>Safety stock calculations (1.5x multiplier)</li>
          <li>Current inventory levels</li>
        </ul>
        <p>
          <strong>Workflow:</strong> Pending → Approve → Implement → Archive
        </p>
      </div>
    </div>
  )
}
