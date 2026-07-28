import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Wrap any route element with <RequireAuth> to force authentication.
 * Unauthenticated users are redirected to /login with the original
 * path stored so they can be sent back after signing in.
 */
export default function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
