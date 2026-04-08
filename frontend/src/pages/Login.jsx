import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";
import "../styles/Login.css";

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);
      const data = response.data;

      // Save user to localStorage
      localStorage.setItem("user", JSON.stringify(data));
      localStorage.setItem("isAuthenticated", "true");

      // Notify parent component
      if (onLogin) {
        onLogin();
      }

      // Navigate to dashboard
      navigate("/");
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        "Login failed. Please try again.";
      setError(errorMsg);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🌾 Agric Stat Dashboard</h1>
          <p>Agricultural Statistics Dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="login-info">
          <p className="hint">Demo Credentials:</p>
          <p className="credentials">
            Username: <strong>somi</strong>
          </p>
          <p className="credentials">
            Password: <strong>1234</strong>
          </p>
        </div>
      </div>
    </div>
  );
}
