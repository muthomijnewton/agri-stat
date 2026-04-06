import React, { useState, useEffect } from 'react'
import { recommendationsAPI } from '../services/api'
import '../styles/Recommendations.css'

function Recommendations() {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const response = await recommendationsAPI.list(0, 100)
      setRecommendations(response.data)
    } catch (err) {
      setError('Failed to load recommendations')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id) => {
    try {
      await recommendationsAPI.approve(id)
      fetchRecommendations()
    } catch (err) {
      setError('Failed to approve recommendation')
      console.error(err)
    }
  }

  const handleImplement = async (id) => {
    try {
      await recommendationsAPI.implement(id)
      fetchRecommendations()
    } catch (err) {
      setError('Failed to implement recommendation')
      console.error(err)
    }
  }

  if (loading) return <div className="loading">Loading recommendations...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="recommendations-page">
      <h1>Inventory Recommendations</h1>
      
      <div className="recommendations-grid">
        {recommendations.length === 0 ? (
          <p className="text-center">No recommendations found</p>
        ) : (
          recommendations.map(rec => (
            <div key={rec.id} className={`recommendation-card status-${rec.status}`}>
              <div className="card-header">
                <h3>{rec.product?.name || 'Unknown Product'}</h3>
                <span className={`status-badge ${rec.status}`}>{rec.status}</span>
              </div>
              
              <div className="card-body">
                <div className="recommendation-item">
                  <label>Recommended Quantity:</label>
                  <span className="value">{rec.recommended_quantity} units</span>
                </div>
                
                <div className="recommendation-item">
                  <label>Current Quantity:</label>
                  <span className="value">{rec.current_quantity || '-'} units</span>
                </div>
                
                <div className="recommendation-item">
                  <label>Min / Max:</label>
                  <span className="value">
                    {rec.min_quantity || '-'} / {rec.max_quantity || '-'}
                  </span>
                </div>
                
                {rec.reason && (
                  <div className="recommendation-reason">
                    <label>Reason:</label>
                    <p>{rec.reason}</p>
                  </div>
                )}
              </div>
              
              <div className="card-footer">
                {rec.status === 'pending' && (
                  <>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => handleApprove(rec.id)}
                    >
                      ✓ Approve
                    </button>
                  </>
                )}
                {rec.status === 'approved' && (
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleImplement(rec.id)}
                  >
                    ✓ Implement
                  </button>
                )}
                {rec.status === 'implemented' && (
                  <span className="status-text">Implemented</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Recommendations
