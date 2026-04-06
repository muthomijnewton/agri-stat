import axios from 'axios'

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Products API
export const productsAPI = {
  getAll: (skip = 0, limit = 100) => api.get('/products', { params: { skip, limit } }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
}

// Transactions API
export const transactionsAPI = {
  getAll: (skip = 0, limit = 100, filters = {}) => 
    api.get('/transactions', { params: { skip, limit, ...filters } }),
  getById: (id) => api.get(`/transactions/${id}`),
  create: (data) => api.post('/transactions', data),
  update: (id, data) => api.put(`/transactions/${id}`, data),
  delete: (id) => api.delete(`/transactions/${id}`),
}

// Forecasts API
export const forecastsAPI = {
  getAll: (skip = 0, limit = 100, filters = {}) => 
    api.get('/forecasts', { params: { skip, limit, ...filters } }),
  getById: (id) => api.get(`/forecasts/${id}`),
  getByProduct: (productId, days = 30) => 
    api.get(`/forecasts/product/${productId}`, { params: { days } }),
  create: (data) => api.post('/forecasts', data),
  update: (id, data) => api.put(`/forecasts/${id}`, data),
  delete: (id) => api.delete(`/forecasts/${id}`),
}

// Recommendations API
export const recommendationsAPI = {
  getAll: (skip = 0, limit = 100, filters = {}) => 
    api.get('/recommendations', { params: { skip, limit, ...filters } }),
  getById: (id) => api.get(`/recommendations/${id}`),
  getByProduct: (productId) => api.get(`/recommendations/product/${productId}`),
  create: (data) => api.post('/recommendations', data),
  update: (id, data) => api.put(`/recommendations/${id}`, data),
  approve: (id) => api.patch(`/recommendations/${id}/approve`),
  implement: (id) => api.patch(`/recommendations/${id}/implement`),
  delete: (id) => api.delete(`/recommendations/${id}`),
}

export default api
