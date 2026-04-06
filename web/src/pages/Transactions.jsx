import { useState, useEffect } from 'react'
import { transactionsAPI, productsAPI } from '../services/api'
import '../css/pages.css'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: '',
    unit_price: '',
    total_price: '',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [txns, prods] = await Promise.all([
        transactionsAPI.getAll(0, 100),
        productsAPI.getAll(0, 100),
      ])
      setTransactions(txns.data)
      setProducts(prods.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    const newData = { ...formData, [name]: value }

    // Auto-calculate total_price
    if (name === 'quantity' || name === 'unit_price') {
      const quantity = parseFloat(newData.quantity) || 0
      const unitPrice = parseFloat(newData.unit_price) || 0
      newData.total_price = (quantity * unitPrice).toFixed(2)
    }

    setFormData(newData)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        product_id: parseInt(formData.product_id),
        quantity: parseInt(formData.quantity),
        unit_price: parseFloat(formData.unit_price),
        total_price: parseFloat(formData.total_price),
      }
      await transactionsAPI.create(data)
      setFormData({
        product_id: '',
        quantity: '',
        unit_price: '',
        total_price: '',
        transaction_date: new Date().toISOString().split('T')[0],
        notes: '',
      })
      setShowForm(false)
      fetchData()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this transaction?')) {
      try {
        await transactionsAPI.delete(id)
        fetchData()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId)
    return product ? product.name : 'Unknown'
  }

  if (loading && transactions.length === 0)
    return <div className="loading">Loading transactions...</div>

  return (
    <div className="container">
      <h1>Transactions</h1>

      {error && <div className="error">{error}</div>}

      <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? '✕ Close' : '+ Record Transaction'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="card">
          <h3>New Transaction</h3>
          <div className="form-group">
            <label>Product *</label>
            <select
              name="product_id"
              value={formData.product_id}
              onChange={handleFormChange}
              required
            >
              <option value="">Select a product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Quantity *</label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Unit Price *</label>
              <input
                type="number"
                name="unit_price"
                value={formData.unit_price}
                onChange={handleFormChange}
                step="0.01"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Total Price</label>
              <input
                type="number"
                name="total_price"
                value={formData.total_price}
                onChange={handleFormChange}
                step="0.01"
                readOnly
              />
            </div>
            <div className="form-group">
              <label>Date *</label>
              <input
                type="date"
                name="transaction_date"
                value={formData.transaction_date}
                onChange={handleFormChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleFormChange}
              rows="2"
            />
          </div>

          <button type="submit" className="btn-primary">
            Record Transaction
          </button>
        </form>
      )}

      <div className="table-responsive">
        <table className="card">
          <thead>
            <tr>
              <th>Product</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id}>
                <td>{getProductName(txn.product_id)}</td>
                <td>{txn.quantity}</td>
                <td>${txn.unit_price}</td>
                <td>${txn.total_price}</td>
                <td>{new Date(txn.transaction_date).toLocaleDateString()}</td>
                <td>
                  <button
                    onClick={() => handleDelete(txn.id)}
                    className="btn-danger"
                    style={{ padding: '5px 10px', fontSize: '0.85rem' }}
                  >
                    Delete
                  </button>
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
