import React, { useEffect, useState } from 'react'
import { transactionsAPI } from '../services/api'

function RecentTransactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRecentTransactions()
  }, [])

  const fetchRecentTransactions = async () => {
    try {
      const response = await transactionsAPI.list(0, 10)
      setTransactions(response.data)
    } catch (err) {
      console.error('Error fetching transactions:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="card loading">Loading...</div>
  if (transactions.length === 0) return <div className="card">No transactions yet</div>

  return (
    <div className="chart-container">
      <h2>Recent Transactions</h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #dee2e6' }}>
              <th style={{ textAlign: 'left', padding: '10px' }}>Product</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Qty</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(t => (
              <tr key={t.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                <td style={{ padding: '10px' }}>{t.product?.name || 'Unknown'}</td>
                <td style={{ padding: '10px' }}>{t.quantity}</td>
                <td style={{ padding: '10px' }}>{new Date(t.transaction_date).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default RecentTransactions
