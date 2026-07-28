import { useState, useEffect } from 'react'
import { transactionsAPI, productsAPI, exportsAPI } from '../services/api'
import '../css/pages.css'

/* ---- Icons ---- */
function IconPlus() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  )
}
function IconX() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}
function IconPencil() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 13, height: 13 }}>
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  )
}
function IconTrash() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 13, height: 13 }}>
      <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4h6v2" />
    </svg>
  )
}
function IconCheck() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 13, height: 13 }}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function IconDownload() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="7 10 12 15 17 10"/>
      <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  )
}

const EMPTY_FORM = {
  product_id:       '',
  transaction_type: 'sale',
  quantity:         '',
  unit_price:       '',
  total_price:      '',
  transaction_date: new Date().toISOString().split('T')[0],
  notes:            '',
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [products,     setProducts]     = useState([])
  const [loading,      setLoading]      = useState(false)
  const [error,        setError]        = useState(null)
  const [successMsg,   setSuccessMsg]   = useState(null)
  const [showForm,     setShowForm]     = useState(false)
  const [editingId,    setEditingId]    = useState(null)
  const [formData,     setFormData]     = useState(EMPTY_FORM)
  const [exporting,    setExporting]    = useState(false)

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [txns, prods] = await Promise.all([
        transactionsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setTransactions(txns.data)
      setProducts(prods.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  /* Open form pre-filled for editing */
  const startEdit = (txn) => {
    setEditingId(txn.id)
    setFormData({
      product_id:       txn.product_id,
      transaction_type: txn.transaction_type ?? 'sale',
      quantity:         txn.quantity,
      unit_price:       txn.unit_price,
      total_price:      txn.total_price,
      transaction_date: txn.transaction_date,
      notes:            txn.notes ?? '',
    })
    setShowForm(true)
    setError(null)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setFormData(EMPTY_FORM)
    setShowForm(false)
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    const updated = { ...formData, [name]: value }
    // Recalculate total whenever quantity or unit_price changes
    if (name === 'quantity' || name === 'unit_price') {
      const qty   = parseFloat(name === 'quantity'   ? value : updated.quantity)   || 0
      const price = parseFloat(name === 'unit_price' ? value : updated.unit_price) || 0
      updated.total_price = (qty * price).toFixed(2)
    }
    setFormData(updated)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        product_id:  parseInt(formData.product_id),
        quantity:    parseInt(formData.quantity),
        unit_price:  parseFloat(formData.unit_price),
        total_price: parseFloat(formData.total_price),
      }
      if (editingId) {
        await transactionsAPI.update(editingId, data)
        flash('Transaction updated successfully.')
      } else {
        await transactionsAPI.create(data)
        flash('Transaction recorded successfully.')
      }
      cancelEdit()
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this transaction?')) return
    try {
      await transactionsAPI.delete(id)
      flash('Transaction deleted.')
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const flash = (msg) => {
    setSuccessMsg(msg)
    setTimeout(() => setSuccessMsg(null), 3000)
  }

  const handleExport = async () => {
    try {
      setExporting(true)
      await exportsAPI.transactions()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setExporting(false)
    }
  }

  const getProductName = (id) => products.find((p) => p.id === id)?.name ?? 'Unknown'

  if (loading && transactions.length === 0) return <div className="loading">Loading transactions…</div>

  return (
    <div className="container">
      <div className="page-header">
        <h1>Transactions</h1>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn-secondary"
            onClick={handleExport}
            disabled={exporting}
            title="Export all transactions as CSV"
          >
            <IconDownload /> {exporting ? 'Exporting…' : 'Export CSV'}
          </button>
          {!showForm && (
            <button className="btn-primary" onClick={() => { setEditingId(null); setFormData(EMPTY_FORM); setShowForm(true) }}>
              <IconPlus /> Record Transaction
            </button>
          )}
        </div>
      </div>

      {error      && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

      {/* ── Add / Edit form ── */}
      {showForm && (
        <form onSubmit={handleSubmit} className="card">
          <h3>{editingId ? 'Edit Transaction' : 'New Transaction'}</h3>

          <div className="form-row">
            <div className="form-group">
              <label>Product *</label>
              <select name="product_id" value={formData.product_id} onChange={handleFormChange} required>
                <option value="">Select a product</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Transaction Type *</label>
              <select name="transaction_type" value={formData.transaction_type} onChange={handleFormChange} required>
                <option value="sale">Sale (outgoing)</option>
                <option value="purchase">Purchase (incoming)</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Quantity *</label>
              <input type="number" name="quantity" value={formData.quantity} onChange={handleFormChange} min="1" required />
            </div>
            <div className="form-group">
              <label>Unit Price (KES) *</label>
              <input type="number" name="unit_price" value={formData.unit_price} onChange={handleFormChange} step="0.01" min="0" required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Total Price (KES)</label>
              <input type="number" name="total_price" value={formData.total_price} step="0.01" readOnly />
            </div>
            <div className="form-group">
              <label>Date *</label>
              <input type="date" name="transaction_date" value={formData.transaction_date} onChange={handleFormChange} required />
            </div>
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea name="notes" value={formData.notes} onChange={handleFormChange} rows="2" />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button type="submit" className="btn-primary">
              <IconCheck /> {editingId ? 'Save Changes' : 'Record Transaction'}
            </button>
            <button type="button" className="btn-secondary" onClick={cancelEdit}>
              <IconX /> Cancel
            </button>
          </div>
        </form>
      )}

      {/* ── Table ── */}
      <div className="table-responsive">
        <table className="card">
          <thead>
            <tr>
              <th>Product</th>
              <th>Type</th>
              <th>Quantity</th>
              <th>Unit Price (KES)</th>
              <th>Total (KES)</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id} className={editingId === txn.id ? 'row-editing' : ''}>
                <td>{getProductName(txn.product_id)}</td>
                <td>
                  <span className={`badge ${txn.transaction_type === 'purchase' ? 'badge-info' : 'badge-success'}`}>
                    {txn.transaction_type === 'purchase' ? 'Purchase' : 'Sale'}
                  </span>
                </td>
                <td>{txn.quantity}</td>
                <td>KES {Number(txn.unit_price).toFixed(2)}</td>
                <td>KES {Number(txn.total_price).toFixed(2)}</td>
                <td>{new Date(txn.transaction_date + 'T00:00:00').toLocaleDateString()}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <button
                      className="btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                      onClick={() => startEdit(txn)}
                    >
                      <IconPencil /> Edit
                    </button>
                    <button
                      className="btn-danger"
                      style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                      onClick={() => handleDelete(txn.id)}
                    >
                      <IconTrash /> Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {transactions.length === 0 && !loading && (
        <div className="card text-center">
          <p className="text-muted">No transactions recorded yet.</p>
        </div>
      )}
    </div>
  )
}
