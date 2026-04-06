import React from 'react'

function ProductForm({ onSubmit }) {
  const [formData, setFormData] = React.useState({
    name: '',
    category: '',
    description: '',
    unit_price: '',
    unit: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
    setFormData({
      name: '',
      category: '',
      description: '',
      unit_price: '',
      unit: ''
    })
  }

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-group">
        <label>Product Name *</label>
        <input 
          type="text" 
          name="name" 
          value={formData.name}
          onChange={handleChange}
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
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Price</label>
          <input 
            type="number" 
            name="unit_price" 
            step="0.01"
            value={formData.unit_price}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Unit (kg, liters, pieces, etc.)</label>
        <input 
          type="text" 
          name="unit" 
          value={formData.unit}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea 
          name="description" 
          value={formData.description}
          onChange={handleChange}
          rows="4"
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">Add Product</button>
      </div>
    </form>
  )
}

export default ProductForm
