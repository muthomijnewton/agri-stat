import React from 'react'

function StatCard({ title, value, icon = '' }) {
  return (
    <div className="stat-card">
      <div style={{ fontSize: '24px', marginBottom: '10px' }}>{icon}</div>
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
    </div>
  )
}

export default StatCard
