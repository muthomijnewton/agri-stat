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
      const response = await productsAPI.list(0, 100)
      setProducts(response.data)
    } catch (err) {
      setError('Failed to load products')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddProduct = async (productData) => {
    try {
      await productsAPI.create(productData)
      setShowForm(false)
      fetchProducts()
    } catch (err) {
      setError('Failed to add product')
      console.error(err)
    }
  }

  const handleDeleteProduct = async (productId) => {
    try {
      await productsAPI.delete(productId)
      fetchProducts()
    } catch (err) {
      setError('Failed to delete product')
      console.error(err)
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
