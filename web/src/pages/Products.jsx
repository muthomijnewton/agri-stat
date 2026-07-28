import { useState, useEffect } from 'react'
import { productsAPI } from '../services/api'
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

const EMPTY_FORM = { name: '', category: '', description: '', unit_price: '', unit: '' }

export default function Products() {
  const [products,   setProducts]   = useState([])
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [showForm,   setShowForm]   = useState(false)
  const [editingId,  setEditingId]  = useState(null)   // null = adding new
  const [formData,   setFormData]   = useState(EMPTY_FORM)

  useEffect(() => { fetchProducts() }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await productsAPI.getAll(0, 100)
      setProducts(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  /* Open the form pre-filled for editing */
  const startEdit = (product) => {
    setEditingId(product.id)
    setFormData({
      name:        product.name        ?? '',
      category:    product.category    ?? '',
      description: product.description ?? '',
      unit_price:  product.unit_price  ?? '',
      unit:        product.unit        ?? '',
    })
    setShowForm(true)
    setError(null)
  }

  /* Reset to "add new" state */
  const cancelEdit = () => {
    setEditingId(null)
    setFormData(EMPTY_FORM)
    setShowForm(false)
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        unit_price: formData.unit_price ? parseFloat(formData.unit_price) : null,
      }
      if (editingId) {
        await productsAPI.update(editingId, data)
        flash('Product updated successfully.')
      } else {
        await productsAPI.create(data)
        flash('Product added successfully.')
      }
      cancelEdit()
      fetchProducts()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this product?')) return
    try {
      await productsAPI.delete(id)
      flash('Product deleted.')
      fetchProducts()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const flash = (msg) => {
    setSuccessMsg(msg)
    setTimeout(() => setSuccessMsg(null), 3000)
  }

  if (loading && products.length === 0) return <div className="loading">Loading products…</div>

  return (
    <div className="container">
      <div className="page-header">
        <h1>Products</h1>
        {!showForm && (
          <button className="btn-primary" onClick={() => { setEditingId(null); setFormData(EMPTY_FORM); setShowForm(true) }}>
            <IconPlus /> Add Product
          </button>
        )}
      </div>

      {error      && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

      {/* ── Add / Edit form ── */}
      {showForm && (
        <form onSubmit={handleSubmit} className="card">
          <h3>{editingId ? 'Edit Product' : 'Add New Product'}</h3>

          <div className="form-group">
            <label>Product Name *</label>
            <input type="text" name="name" value={formData.name} onChange={handleFormChange} required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category</label>
              <input type="text" name="category" value={formData.category} onChange={handleFormChange} placeholder="e.g., Vegetables, Grains" />
            </div>
            <div className="form-group">
              <label>Unit</label>
              <input type="text" name="unit" value={formData.unit} onChange={handleFormChange} placeholder="e.g., kg, pieces, litres" />
            </div>
          </div>

          <div className="form-group">
            <label>Unit Price (KES)</label>
            <input type="number" name="unit_price" value={formData.unit_price} onChange={handleFormChange} step="0.01" placeholder="0.00" />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={formData.description} onChange={handleFormChange} rows="3" />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button type="submit" className="btn-primary">
              <IconCheck /> {editingId ? 'Save Changes' : 'Add Product'}
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
              <th>Name</th>
              <th>Category</th>
              <th>Unit Price (KES)</th>
              <th>Unit</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id} className={editingId === product.id ? 'row-editing' : ''}>
                <td>{product.name}</td>
                <td>{product.category || '—'}</td>
                <td>KES {Number(product.unit_price || 0).toFixed(2)}</td>
                <td>{product.unit || '—'}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <button
                      className="btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                      onClick={() => startEdit(product)}
                    >
                      <IconPencil /> Edit
                    </button>
                    <button
                      className="btn-danger"
                      style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                      onClick={() => handleDelete(product.id)}
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

      {products.length === 0 && !loading && (
        <div className="card text-center">
          <p className="text-muted">No products found. Add one to get started.</p>
        </div>
      )}
    </div>
  )
}
