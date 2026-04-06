import { useState, useEffect } from 'react'
import { forecastsAPI, productsAPI } from '../services/api'
import '../css/pages.css'

export default function Forecasts() {
  const [forecasts, setForecasts] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedProduct, setSelectedProduct] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [fcsts, prods] = await Promise.all([
        forecastsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setForecasts(fcsts.data)
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

  const filteredForecasts = selectedProduct
    ? forecasts.filter((f) => f.product_id === parseInt(selectedProduct))
    : forecasts

  if (loading && forecasts.length === 0)
    return <div className="loading">Loading forecasts...</div>

  return (
    <div className="container">
      <h1>Demand Forecasts</h1>

      {error && <div className="error">{error}</div>}

      <div className="card filters">
        <label>Filter by Product:</label>
        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
          <option value="">All Products</option>
          {products.map((product) => (
            <option key={product.id} value={product.id}>
              {product.name}
            </option>
          ))}
        </select>
      </div>

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
              <th>Accuracy</th>
            </tr>
          </thead>
          <tbody>
            {filteredForecasts.map((forecast) => (
              <tr key={forecast.id}>
                <td>{getProductName(forecast.product_id)}</td>
                <td>{new Date(forecast.forecast_date).toLocaleDateString()}</td>
                <td className="text-strong">{forecast.predicted_demand}</td>
                <td>{forecast.confidence_lower || '-'}</td>
                <td>{forecast.confidence_upper || '-'}</td>
                <td>{forecast.model_type || 'N/A'}</td>
                <td>
                  {forecast.accuracy_score ? `${forecast.accuracy_score.toFixed(2)}%` : 'N/A'}
                </td>
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
              : 'No forecasts generated yet. Record transactions first!'}
          </p>
        </div>
      )}

      <div className="card info-box">
        <h3>📊 How Forecasting Works</h3>
        <p>
          The system uses advanced time-series forecasting models to predict future demand:
        </p>
        <ul>
          <li>
            <strong>Prophet:</strong> Developed by Facebook, great for seasonal patterns
          </li>
          <li>
            <strong>ARIMA:</strong> Classical approach for trend-based forecasting
          </li>
          <li>
            <strong>Confidence Intervals:</strong> Shows the range of likely demand values
          </li>
          <li>
            <strong>Accuracy Score:</strong> MAPE (Mean Absolute Percentage Error) of the model
          </li>
        </ul>
      </div>
    </div>
  )
}
