import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import '../css/App.css'

function IconLeaf() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
    </svg>
  )
}

export default function Register() {
  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const { login } = useAuth()
  const navigate  = useNavigate()

  const set = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Client-side validation
    if (!form.username.trim()) return setError('Username is required.')
    if (form.username.trim().length < 3) return setError('Username must be at least 3 characters.')
    if (!form.email.trim()) return setError('Email is required.')
    if (!form.password) return setError('Password is required.')
    if (form.password.length < 6) return setError('Password must be at least 6 characters.')
    if (form.password !== form.confirm_password) return setError('Passwords do not match.')

    try {
      setLoading(true)
      setError(null)
      const { data } = await authAPI.register(
        form.username.trim(),
        form.email.trim(),
        form.password,
        form.full_name.trim() || null,
      )
      // Auto-login: store token and redirect to dashboard
      login(data)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(' '))
      } else {
        setError(detail ?? 'Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card card">

        <div className="login-header">
          <div className="login-logo">
            <IconLeaf />
          </div>
          <h1>Create account</h1>
          <p>Join AgriStat and start forecasting</p>
        </div>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>

          <div className="form-group">
            <label htmlFor="full_name">Full Name <span className="text-muted">(optional)</span></label>
            <input
              id="full_name"
              type="text"
              value={form.full_name}
              onChange={set('full_name')}
              placeholder="e.g. Jane Wanjiku"
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-username">Username <span className="register-required">*</span></label>
            <input
              id="reg-username"
              type="text"
              value={form.username}
              onChange={set('username')}
              placeholder="e.g. janewanjiku"
              autoComplete="username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-email">Email address <span className="register-required">*</span></label>
            <input
              id="reg-email"
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-password">Password <span className="register-required">*</span></label>
            <input
              id="reg-password"
              type="password"
              value={form.password}
              onChange={set('password')}
              placeholder="At least 6 characters"
              autoComplete="new-password"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-confirm">Confirm Password <span className="register-required">*</span></label>
            <input
              id="reg-confirm"
              type="password"
              value={form.confirm_password}
              onChange={set('confirm_password')}
              placeholder="Repeat your password"
              autoComplete="new-password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary btn-full"
            disabled={loading}
          >
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="register-login-link">
          Already have an account?{' '}
          <Link to="/login">Log in</Link>
        </p>

      </div>
    </div>
  )
}
