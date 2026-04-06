import { useState, useEffect } from 'react'
import { productsAPI } from '../services/api'
import '../css/pages.css'

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    description: '',
    unit_price: '',
    unit: '',
  })

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const response = await productsAPI.getAll(0, 100)
      setProducts(response.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        unit_price: formData.unit_price ? parseFloat(formData.unit_price) : null,
      }
      await productsAPI.create(data)
      setFormData({ name: '', category: '', description: '', unit_price: '', unit: '' })
      setShowForm(false)
      fetchProducts()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productsAPI.delete(id)
        fetchProducts()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  if (loading && products.length === 0) return <div className="loading">Loading products...</div>

  return (
    <div className="container">
      <h1>Products</h1>

      {error && <div className="error">{error}</div>}

      <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? '✕ Close' : '+ Add Product'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="card">
          <h3>Add New Product</h3>
          <div className="form-group">
            <label>Product Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category</label>
              <input
                type="text"
                name="category"
                value={formData.category}
                onChange={handleFormChange}
                placeholder="e.g., Vegetables, Fruits"
              />
            </div>
            <div className="form-group">
              <label>Unit</label>
              <input
                type="text"
                name="unit"
                value={formData.unit}
                onChange={handleFormChange}
                placeholder="e.g., kg, pieces, liters"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Unit Price</label>
            <input
              type="number"
              name="unit_price"
              value={formData.unit_price}
              onChange={handleFormChange}
              step="0.01"
              placeholder="0.00"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleFormChange}
              rows="3"
            />
          </div>

          <button type="submit" className="btn-primary">Save Product</button>
        </form>
      )}

      <div className="table-responsive">
        <table className="card">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Unit Price</th>
              <th>Unit</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.category || '-'}</td>
                <td>${product.unit_price || '0.00'}</td>
                <td>{product.unit || '-'}</td>
                <td>
                  <button
                    onClick={() => handleDelete(product.id)}
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

      {products.length === 0 && !loading && (
        <div className="card text-center">
          <p className="text-muted">No products found. Add one to get started!</p>
        </div>
      )}
    </div>
  )
}
