import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

const TOKEN_KEY = 'agristat_token'
const USER_KEY  = 'agristat_user'

// ---------------------------------------------------------------------------
// Set the header synchronously at module load time so the very first API
// call after a page refresh already carries the Bearer token.
// ---------------------------------------------------------------------------
const _storedToken = localStorage.getItem(TOKEN_KEY)
if (_storedToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${_storedToken}`
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null }
  })
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) ?? null)

  // Keep the header in sync whenever the token state changes
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  }, [token])

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
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    delete api.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
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
