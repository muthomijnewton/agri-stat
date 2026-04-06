import React, { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function ForecastChart({ forecasts }) {
  const [data, setData] = useState([])

  useEffect(() => {
    if (forecasts && forecasts.length > 0) {
      const chartData = forecasts
        .sort((a, b) => new Date(a.forecast_date) - new Date(b.forecast_date))
        .slice(-30)
        .map(f => ({
          date: f.forecast_date,
          demand: f.predicted_demand,
          lower: f.confidence_lower || 0,
          upper: f.confidence_upper || 0
        }))
      setData(chartData)
    }
  }, [forecasts])

  if (data.length === 0) {
    return <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No forecast data</div>
  }

  return (
    <div className="chart-container">
      <h2>Forecast Visualization</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
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
    </div>
  )
}

export default ForecastChart
