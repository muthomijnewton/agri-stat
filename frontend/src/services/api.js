import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

console.log('🌐 API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 5000
})

// Add response interceptor for better error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('❌ API request timeout - backend may not be running')
    } else if (error.message === 'Network Error') {
      console.error('❌ Network error - check if backend is accessible')
    } else if (error.response?.status === 404) {
      console.error('❌ Endpoint not found:', error.response.config.url)
    } else if (error.response?.status === 500) {
      console.error('❌ Server error:', error.response.data)
    } else {
      console.error('❌ API Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Products API
export const productsAPI = {
  list: (skip = 0, limit = 100) => 
    api.get('/products/', { params: { skip, limit } }),
  get: (id) => 
    api.get(`/products/${id}`),
  create: (data) => 
    api.post('/products/', data),
  update: (id, data) => 
    api.put(`/products/${id}`, data),
  delete: (id) => 
    api.delete(`/products/${id}`)
}

// Transactions API
export const transactionsAPI = {
  list: (skip = 0, limit = 100, filters = {}) => 
    api.get('/transactions/', { params: { skip, limit, ...filters } }),
  get: (id) => 
    api.get(`/transactions/${id}`),
  create: (data) => 
    api.post('/transactions/', data),
  update: (id, data) => 
    api.put(`/transactions/${id}`, data),
  delete: (id) => 
    api.delete(`/transactions/${id}`)
}

// Forecasts API
export const forecastsAPI = {
  list: (skip = 0, limit = 100, filters = {}) => 
    api.get('/forecasts/', { params: { skip, limit, ...filters } }),
  get: (id) => 
    api.get(`/forecasts/${id}`),
  getByProduct: (productId, days = 30) => 
    api.get(`/forecasts/product/${productId}`, { params: { days } }),
  create: (data) => 
    api.post('/forecasts/', data),
  update: (id, data) => 
    api.put(`/forecasts/${id}`, data),
  delete: (id) => 
    api.delete(`/forecasts/${id}`)
}

// Recommendations API
export const recommendationsAPI = {
  list: (skip = 0, limit = 100, filters = {}) => 
    api.get('/recommendations/', { params: { skip, limit, ...filters } }),
  get: (id) => 
    api.get(`/recommendations/${id}`),
  getByProduct: (productId) => 
    api.get(`/recommendations/product/${productId}`),
  create: (data) => 
    api.post('/recommendations/', data),
  update: (id, data) => 
    api.put(`/recommendations/${id}`, data),
  approve: (id) => 
    api.patch(`/recommendations/${id}/approve`),
  implement: (id) => 
    api.patch(`/recommendations/${id}/implement`),
  delete: (id) => 
    api.delete(`/recommendations/${id}`)
}

export default api
