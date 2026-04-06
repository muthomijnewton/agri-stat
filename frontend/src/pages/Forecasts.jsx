import React, { useState, useEffect } from 'react'
import { forecastsAPI } from '../services/api'
import ForecastChart from '../components/ForecastChart'
import '../styles/Forecasts.css'

function Forecasts() {
  const [forecasts, setForecasts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchForecasts()
  }, [])

  const fetchForecasts = async () => {
    try {
      setLoading(true)
      const response = await forecastsAPI.list(0, 100)
      setForecasts(response.data)
    } catch (err) {
      setError('Failed to load forecasts')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading forecasts...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="forecasts-page">
      <h1>Demand Forecasts</h1>
      
      <ForecastChart forecasts={forecasts} />

      <div className="forecasts-list">
        <h2>Forecast Details</h2>
        <div className="table-container">
          <table className="forecasts-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Forecast Date</th>
                <th>Predicted Demand</th>
                <th>Confidence Lower</th>
                <th>Confidence Upper</th>
                <th>Model</th>
                <th>Accuracy</th>
              </tr>
            </thead>
            <tbody>
              {forecasts.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center">No forecasts found</td>
                </tr>
              ) : (
                forecasts.map(f => (
                  <tr key={f.id}>
                    <td>{f.product?.name || 'Unknown'}</td>
                    <td>{new Date(f.forecast_date).toLocaleDateString()}</td>
                    <td>{f.predicted_demand}</td>
                    <td>{f.confidence_lower || '-'}</td>
                    <td>{f.confidence_upper || '-'}</td>
                    <td>{f.model_type || '-'}</td>
                    <td>{f.accuracy_score ? f.accuracy_score.toFixed(2) + '%' : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Forecasts
