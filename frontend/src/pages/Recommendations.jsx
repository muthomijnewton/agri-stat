import React, { useState, useEffect } from "react";
import { recommendationsAPI } from "../services/api";
import "../styles/Recommendations.css";

function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      console.log('💡 Fetching recommendations...');
      const response = await recommendationsAPI.list(0, 100);
      console.log('✅ Recommendations loaded:', response.data);
      setRecommendations(response.data);
      setError(null);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to load recommendations";
      console.error('❌ Error loading recommendations:', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      console.log('✅ Approving recommendation:', id);
      await recommendationsAPI.approve(id);
      console.log('✅ Recommendation approved successfully');
      setError(null);
      fetchRecommendations();
      alert('✅ Recommendation approved!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to approve recommendation";
      console.error('❌ Error approving', errorMsg);
      setError(errorMsg);
      alert('❌ Error: ' + errorMsg);
    }
  };

  const handleImplement = async (id) => {
    try {
      console.log('🚀 Implementing recommendation:', id);
      await recommendationsAPI.implement(id);
      console.log('✅ Recommendation implemented successfully');
      setError(null);
      fetchRecommendations();
      alert('✅ Recommendation implemented!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to implement recommendation";
      console.error('❌ Error implementing', errorMsg);
      setError(errorMsg);
      alert('❌ Error: ' + errorMsg);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this recommendation?')) {
      return;
    }
    try {
      console.log('🗑️ Deleting recommendation:', id);
      await recommendationsAPI.delete(id);
      console.log('✅ Recommendation deleted successfully');
      setError(null);
      fetchRecommendations();
      alert('✅ Recommendation deleted successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete recommendation';
      console.error('❌ Error deleting recommendation:', errorMsg);
      setError(errorMsg);
      alert('❌ Error: ' + errorMsg);
    }
  };

  if (loading) return <div className="loading">Loading recommendations...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="recommendations-page">
      <h1>Inventory Recommendations</h1>

      <div className="recommendations-grid">
        {recommendations.length === 0 ? (
          <p className="text-center">No recommendations found</p>
        ) : (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className={`recommendation-card status-${rec.status}`}
            >
              <div className="card-header">
                <h3>{rec.product?.name || "Unknown Product"}</h3>
                <span className={`status-badge ${rec.status}`}>
                  {rec.status}
                </span>
              </div>

              <div className="card-body">
                <div className="recommendation-item">
                  <label>Recommended Quantity:</label>
                  <span className="value">
                    {rec.recommended_quantity} units
                  </span>
                </div>

                <div className="recommendation-item">
                  <label>Current Quantity:</label>
                  <span className="value">
                    {rec.current_quantity || "-"} units
                  </span>
                </div>

                <div className="recommendation-item">
                  <label>Min / Max:</label>
                  <span className="value">
                    {rec.min_quantity || "-"} / {rec.max_quantity || "-"}
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
                {rec.status === "pending" && (
                  <>
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleApprove(rec.id)}
                    >
                      ✓ Approve
                    </button>
                    <button
                      className="btn btn-delete"
                      onClick={() => handleDelete(rec.id)}
                    >
                      Delete
                    </button>
                  </>
                )}
                {rec.status === "approved" && (
                  <>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleImplement(rec.id)}
                    >
                      ✓ Implement
                    </button>
                    <button
                      className="btn btn-delete"
                      onClick={() => handleDelete(rec.id)}
                    >
                      Delete
                    </button>
                  </>
                )}
                {rec.status === "implemented" && (
                  <>
                    <span className="status-text">Implemented</span>
                    <button
                      className="btn btn-delete"
                      onClick={() => handleDelete(rec.id)}
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Recommendations;
