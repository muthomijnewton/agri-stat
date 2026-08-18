import { Link } from 'react-router-dom'
import '../css/App.css'

/* ---- Inline SVG icons ---- */
function IconLeaf() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
    </svg>
  )
}

function IconTrendingUp() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
      <polyline points="16 7 22 7 22 13"/>
    </svg>
  )
}

function IconClipboard() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
    </svg>
  )
}

function IconBarChart2() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  )
}

function IconBox() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    </svg>
  )
}

const FEATURES = [
  {
    icon: <IconTrendingUp />,
    title: 'Demand Forecasting',
    desc: 'Prophet and ARIMA models predict future demand so you never run short or overstock.',
  },
  {
    icon: <IconClipboard />,
    title: 'Inventory Recommendations',
    desc: 'Automated reorder suggestions based on forecast output and current stock levels.',
  },
  {
    icon: <IconBarChart2 />,
    title: 'Analytics Dashboard',
    desc: 'KPI cards, revenue trends, and transaction breakdowns in one clear view.',
  },
  {
    icon: <IconBox />,
    title: 'Product Management',
    desc: 'Track agricultural products, pricing, and category data with ease.',
  },
]

export default function Landing() {
  return (
    <div className="landing-wrapper">

      {/* ── Top nav ── */}
      <header className="landing-header">
        <div className="landing-nav">
          <div className="landing-brand">
            <div className="landing-brand-icon">
              <IconLeaf />
            </div>
            <span className="landing-brand-name">AgriStat</span>
          </div>
          <div className="landing-nav-actions">
            <Link to="/login" className="btn-secondary landing-btn-outline">Log In</Link>
            <Link to="/register" className="btn-primary landing-btn-filled">Sign Up</Link>
          </div>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <div className="landing-hero-badge">Agricultural Supply Chain Intelligence</div>
          <h1 className="landing-hero-title">
            Forecast demand.<br />
            Optimise inventory.<br />
            <span className="landing-hero-accent">Grow with confidence.</span>
          </h1>
          <p className="landing-hero-sub">
            AgriStat is a data-driven platform built for farmers, cooperatives, and agri-businesses
            in East Africa. Turn your sales history into actionable forecasts and inventory plans.
          </p>
          <div className="landing-hero-cta">
            <Link to="/register" className="btn-primary landing-cta-primary">Get started free</Link>
            <Link to="/login" className="landing-cta-secondary">Already have an account? Log in →</Link>
          </div>
        </div>
        <div className="landing-hero-visual" aria-hidden="true">
          <div className="landing-hero-card">
            <div className="lhc-label">Forecast — Next 30 days</div>
            <div className="lhc-chart">
              {[40, 65, 50, 80, 70, 90, 75, 95, 85, 100, 88, 110].map((h, i) => (
                <div key={i} className="lhc-bar" style={{ height: `${h}%` }} />
              ))}
            </div>
            <div className="lhc-stats">
              <div className="lhc-stat">
                <span className="lhc-stat-value">+18%</span>
                <span className="lhc-stat-label">Predicted demand growth</span>
              </div>
              <div className="lhc-stat">
                <span className="lhc-stat-value">92%</span>
                <span className="lhc-stat-label">Forecast accuracy</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="landing-features">
        <div className="landing-section-header">
          <h2>Everything you need to run a smarter supply chain</h2>
          <p>Purpose-built for agricultural products — from maize and tomatoes to beans and potatoes.</p>
        </div>
        <div className="landing-features-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="landing-feature-card">
              <div className="landing-feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA banner ── */}
      <section className="landing-cta-banner">
        <h2>Ready to take control of your supply chain?</h2>
        <p>Create a free account and start forecasting in minutes.</p>
        <Link to="/register" className="btn-primary landing-cta-primary">Create your account</Link>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer">
        <p>
          &copy; 2026 AgriStat &mdash; Developed at the University of Eastern Africa, Baraton (INSY 492).
        </p>
      </footer>

    </div>
  )
}
