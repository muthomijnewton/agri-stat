import React, { useState, useEffect } from 'react'
import { productsAPI } from '../services/api'
import ProductForm from '../components/ProductForm'
import ProductList from '../components/ProductList'
import '../styles/Products.css'

function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      console.log('📦 Fetching products...')
      const response = await productsAPI.list(0, 100)
      console.log('✅ Products loaded:', response.data)
      setProducts(response.data)
      setError(null)
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load products'
      console.error('❌ Error loading products:', errorMsg)
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleAddProduct = async (productData) => {
    try {
      console.log('➕ Creating product:', productData)
      await productsAPI.create(productData)
      console.log('✅ Product created successfully')
      setShowForm(false)
      setError(null)
      fetchProducts()
      alert('✅ Product added successfully!')
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to add product'
      console.error('❌ Error creating product:', errorMsg)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
    }
  }

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return
    }
    try {
      console.log('🗑️ Deleting product:', productId)
      await productsAPI.delete(productId)
      console.log('✅ Product deleted successfully')
      setError(null)
      fetchProducts()
      alert('✅ Product deleted successfully!')
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete product'
      console.error('❌ Error deleting product:', errorMsg)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
    }
  }

  if (loading) return <div className="loading">Loading products...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="products-page">
      <div className="page-header">
        <h1>Products</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Add Product'}
        </button>
      </div>

      {showForm && (
        <ProductForm onSubmit={handleAddProduct} />
      )}

      <ProductList 
        products={products}
        onDelete={handleDeleteProduct}
      />
    </div>
  )
}

export default Products
