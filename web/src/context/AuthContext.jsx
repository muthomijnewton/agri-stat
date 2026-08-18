import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

const TOKEN_KEY = 'agristat_token'
const USER_KEY  = 'agristat_user'

// ---------------------------------------------------------------------------
// Set the Authorization header synchronously at module load time so the very
// first API call after a page refresh already carries the Bearer token.
// ---------------------------------------------------------------------------
const _storedToken = localStorage.getItem(TOKEN_KEY)
if (_storedToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${_storedToken}`
}

// ---------------------------------------------------------------------------
// JWT expiry helper — decodes the payload without a library dependency.
// Returns true if the token has expired (or is unparseable).
// ---------------------------------------------------------------------------
function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    if (!payload.exp) return false          // no exp claim → treat as valid
    return Date.now() / 1000 >= payload.exp // compare Unix timestamps
  } catch {
    return true                             // malformed token → treat as expired
  }
}

export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null }
  })
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) ?? null)

  // ── Keep Authorization header in sync with token state ──────────────────
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  }, [token])

  // ── On boot: validate the stored token against the server ────────────────
  // 1. If the JWT itself has expired client-side → clear immediately (no network call)
  // 2. Otherwise call GET /auth/me to confirm the session is still valid and
  //    refresh the user object in case profile data changed on another device.
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    if (!storedToken) return

    if (isTokenExpired(storedToken)) {
      _clearAuth()
      return
    }

    api.get('/auth/me')
      .then(({ data }) => {
        // Merge fresh server data into localStorage + state
        localStorage.setItem(USER_KEY, JSON.stringify(data))
        setUser(data)
      })
      .catch(() => {
        // 401 / network error — force logout so the UI stays consistent
        _clearAuth()
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function _clearAuth() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    delete api.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
  }

  function login(userData) {
    const { access_token, ...rest } = userData
    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(rest))
    // Set immediately — don't wait for the useEffect re-render cycle
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setToken(access_token)
    setUser(rest)
  }

  function logout() {
    _clearAuth()
  }

  /** Sync updated profile fields back into localStorage + state after PATCH /me */
  function updateUser(updatedFields) {
    const merged = { ...user, ...updatedFields }
    localStorage.setItem(USER_KEY, JSON.stringify(merged))
    setUser(merged)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, updateUser, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
