import React, { useState, useEffect } from "react";
import { forecastsAPI } from "../services/api";
import ForecastChart from "../components/ForecastChart";
import "../styles/Forecasts.css";

function Forecasts() {
  const [forecasts, setForecasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchForecasts();
  }, []);

  const fetchForecasts = async () => {
    try {
      setLoading(true);
      console.log('📈 Fetching forecasts...');
      const response = await forecastsAPI.list(0, 100);
      console.log('✅ Forecasts loaded:', response.data);
      setForecasts(response.data);
      setError(null);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to load forecasts";
      console.error('❌ Error loading forecasts:', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteForecast = async (forecastId) => {
    if (!window.confirm('Are you sure you want to delete this forecast?')) {
      return;
    }
    try {
      console.log('🗑️ Deleting forecast:', forecastId);
      await forecastsAPI.delete(forecastId);
      console.log('✅ Forecast deleted successfully');
      setError(null);
      fetchForecasts();
      alert('✅ Forecast deleted successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete forecast';
      console.error('❌ Error deleting forecast:', errorMsg);
      setError(errorMsg);
      alert('❌ Error: ' + errorMsg);
    }
  };

  if (loading) return <div className="loading">Loading forecasts...</div>;
  if (error) return <div className="error">{error}</div>;

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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {forecasts.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center">
                    No forecasts found
                  </td>
                </tr>
              ) : (
                forecasts.map((f) => (
                  <tr key={f.id}>
                    <td>{f.product?.name || "Unknown"}</td>
                    <td>{new Date(f.forecast_date).toLocaleDateString()}</td>
                    <td>{f.predicted_demand}</td>
                    <td>{f.confidence_lower || "-"}</td>
                    <td>{f.confidence_upper || "-"}</td>
                    <td>{f.model_type || "-"}</td>
                    <td>
                      {f.accuracy_score && typeof f.accuracy_score === 'number'
                        ? f.accuracy_score.toFixed(2) + "%"
                        : f.accuracy_score
                        ? parseFloat(f.accuracy_score).toFixed(2) + "%"
                        : "-"}
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeleteForecast(f.id)}
                        className="btn-delete"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Forecasts;
