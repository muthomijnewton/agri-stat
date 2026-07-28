import axios from 'axios'

// Vite exposes env vars via import.meta.env (VITE_ prefix only).
// Falls back to the local dev backend if the variable is not set.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---------------------------------------------------------------------------
// Products
// ---------------------------------------------------------------------------
export const productsAPI = {
  getAll:  (skip = 0, limit = 100) => api.get('/products', { params: { skip, limit } }),
  getById: (id)                     => api.get(`/products/${id}`),
  create:  (data)                   => api.post('/products', data),
  update:  (id, data)               => api.put(`/products/${id}`, data),
  delete:  (id)                     => api.delete(`/products/${id}`),
}

// ---------------------------------------------------------------------------
// Transactions
// ---------------------------------------------------------------------------
export const transactionsAPI = {
  getAll:  (skip = 0, limit = 100, filters = {}) =>
    api.get('/transactions', { params: { skip, limit, ...filters } }),
  create:  (data)       => api.post('/transactions', data),
  update:  (id, data)   => api.put(`/transactions/${id}`, data),
  delete:  (id)         => api.delete(`/transactions/${id}`),
}

// ---------------------------------------------------------------------------
// Forecasts
// ---------------------------------------------------------------------------
export const forecastsAPI = {
  getAll:           (skip = 0, limit = 100, filters = {}) =>
    api.get('/forecasts', { params: { skip, limit, ...filters } }),
  getById:          (id)              => api.get(`/forecasts/${id}`),
  create:           (data)            => api.post('/forecasts', data),
  update:           (id, data)        => api.put(`/forecasts/${id}`, data),
  delete:           (id)              => api.delete(`/forecasts/${id}`),
  generate:         (productId, model = 'auto') =>
    api.post(`/forecasts/generate/${productId}`, null, { params: { model } }),
  generateAll:      (model = 'auto') =>
    api.post('/forecasts/generate-all', null, { params: { model } }),
}

// ---------------------------------------------------------------------------
// Recommendations
// ---------------------------------------------------------------------------
export const recommendationsAPI = {
  getAll:     (skip = 0, limit = 100, filters = {}) =>
    api.get('/recommendations', { params: { skip, limit, ...filters } }),
  getById:    (id)       => api.get(`/recommendations/${id}`),
  create:     (data)     => api.post('/recommendations', data),
  approve:    (id)       => api.patch(`/recommendations/${id}/approve`),
  implement:  (id)       => api.patch(`/recommendations/${id}/implement`),
  delete:     (id)       => api.delete(`/recommendations/${id}`),
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------
export const notificationsAPI = {
  getAll:       ()   => api.get('/notifications/'),
  unreadCount:  ()   => api.get('/notifications/unread-count'),
  markRead:     (id) => api.patch(`/notifications/${id}/read`),
  markAllRead:  ()   => api.patch('/notifications/read-all'),
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export const authAPI = {
  login:         (username, password) => api.post('/auth/login', { username, password }),
  getProfile:    ()                   => api.get('/auth/me'),
  updateProfile: (data)               => api.patch('/auth/me', data),
}

// ---------------------------------------------------------------------------
// Stats / Analytics
// ---------------------------------------------------------------------------
export const statsAPI = {
  summary:                  ()                            => api.get('/stats/summary'),
  transactionsDaily:        (days = 30)                   => api.get(`/stats/transactions-daily?days=${days}`),
  revenueByProduct:         (days = 30)                   => api.get(`/stats/revenue-by-product?days=${days}`),
  transactionTypeSplit:     (days = 30)                   => api.get(`/stats/transaction-type-split?days=${days}`),
  forecastAccuracyTrend:    (limit = 20)                  => api.get(`/stats/forecast-accuracy-trend?limit=${limit}`),
  recommendationStatusBreakdown: ()                       => api.get('/stats/recommendation-status-breakdown'),
  topProductsByQuantity:    (days = 30, limit = 10)       => api.get(`/stats/top-products-by-quantity?days=${days}&limit=${limit}`),
}

// ---------------------------------------------------------------------------
// CSV Export
// ---------------------------------------------------------------------------

/**
 * Download a CSV from the given endpoint path and trigger a browser file-save.
 * Any query-string filters should be appended to `path` before calling.
 *
 * @param {string} path     - e.g. '/exports/transactions?product_id=3'
 * @param {string} filename - suggested filename, e.g. 'transactions.csv'
 */
export async function exportCSV(path, filename) {
  const response = await api.get(path, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8;' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const exportsAPI = {
  transactions:    (filters = {}) => {
    const params = new URLSearchParams(
      Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null && v !== ''))
    ).toString()
    const today = new Date().toISOString().slice(0, 10)
    return exportCSV(`/exports/transactions${params ? '?' + params : ''}`, `transactions_${today}.csv`)
  },
  forecasts:       (filters = {}) => {
    const params = new URLSearchParams(
      Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null && v !== ''))
    ).toString()
    const today = new Date().toISOString().slice(0, 10)
    return exportCSV(`/exports/forecasts${params ? '?' + params : ''}`, `forecasts_${today}.csv`)
  },
  recommendations: (filters = {}) => {
    const params = new URLSearchParams(
      Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null && v !== ''))
    ).toString()
    const today = new Date().toISOString().slice(0, 10)
    return exportCSV(`/exports/recommendations${params ? '?' + params : ''}`, `recommendations_${today}.csv`)
  },
}

// ---------------------------------------------------------------------------
// 401 interceptor — redirect to /login whenever a token is missing/expired
// ---------------------------------------------------------------------------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored credentials so the user lands on a clean login form
      localStorage.removeItem('agristat_token')
      localStorage.removeItem('agristat_user')
      delete api.defaults.headers.common['Authorization']
      // Only redirect if we're not already on the login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ---------------------------------------------------------------------------
// Default export (for direct use: api.get('/stats/summary'))
// ---------------------------------------------------------------------------
export default api
