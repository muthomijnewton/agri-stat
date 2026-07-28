import { useState, useEffect, useRef, useCallback } from 'react'
import { notificationsAPI } from '../services/api'

/* ---- type → colour map ---- */
const TYPE_COLOR = {
  info:    '#2563eb',
  success: '#16a34a',
  warning: '#d97706',
  danger:  '#dc2626',
}

const TYPE_BG = {
  info:    '#eff6ff',
  success: '#f0fdf4',
  warning: '#fffbeb',
  danger:  '#fef2f2',
}

/* ---- relative time formatter ---- */
function relativeTime(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins  = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days  = Math.floor(diff / 86400000)
  if (mins  < 1)  return 'just now'
  if (mins  < 60) return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

/* ---- SVG icons ---- */
function IconBell({ hasUnread }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={hasUnread ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ width: 18, height: 18 }}
    >
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  )
}

function IconCheckAll() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ width: 13, height: 13 }}>
      <polyline points="20 6 9 17 4 12" />
      <polyline points="16 6 9 13 4 8" style={{ opacity: 0.5 }} />
    </svg>
  )
}

/* ================================================================
   NotificationBell
   ================================================================ */
export default function NotificationBell() {
  const [open,          setOpen]          = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unread,        setUnread]        = useState(0)
  const [loading,       setLoading]       = useState(false)
  const [markingAll,    setMarkingAll]    = useState(false)

  const dropdownRef = useRef(null)
  const pollRef     = useRef(null)

  /* ---- fetch unread count (lightweight, runs every 30 s) ---- */
  const fetchCount = useCallback(async () => {
    try {
      const res = await notificationsAPI.unreadCount()
      setUnread(res.data.count)
    } catch {
      /* silently ignore — auth may not be ready yet */
    }
  }, [])

  /* ---- fetch full list when dropdown opens ---- */
  const fetchAll = useCallback(async () => {
    try {
      setLoading(true)
      const res = await notificationsAPI.getAll()
      setNotifications(res.data)
      setUnread(res.data.filter(n => !n.read).length)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }, [])

  /* ---- poll for count every 30 s ---- */
  useEffect(() => {
    fetchCount()
    pollRef.current = setInterval(fetchCount, 30000)
    return () => clearInterval(pollRef.current)
  }, [fetchCount])

  /* ---- fetch full list whenever dropdown opens ---- */
  useEffect(() => {
    if (open) fetchAll()
  }, [open, fetchAll])

  /* ---- close on outside click ---- */
  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  /* ---- mark single notification as read ---- */
  const handleMarkRead = async (id) => {
    try {
      await notificationsAPI.markRead(id)
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      )
      setUnread(prev => Math.max(0, prev - 1))
    } catch { /* ignore */ }
  }

  /* ---- mark all as read ---- */
  const handleMarkAllRead = async () => {
    try {
      setMarkingAll(true)
      await notificationsAPI.markAllRead()
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
      setUnread(0)
    } catch { /* ignore */ }
    finally { setMarkingAll(false) }
  }

  return (
    <div className="notif-bell-wrapper" ref={dropdownRef}>
      {/* ---- Bell button ---- */}
      <button
        className="notif-bell-btn"
        onClick={() => setOpen(o => !o)}
        aria-label={`Notifications${unread > 0 ? ` — ${unread} unread` : ''}`}
        aria-expanded={open}
        aria-haspopup="true"
      >
        <IconBell hasUnread={unread > 0} />
        {unread > 0 && (
          <span className="notif-badge" aria-hidden="true">
            {unread > 99 ? '99+' : unread}
          </span>
        )}
      </button>

      {/* ---- Dropdown ---- */}
      {open && (
        <div className="notif-dropdown" role="dialog" aria-label="Notifications">
          {/* header */}
          <div className="notif-dropdown-header">
            <span className="notif-dropdown-title">
              Notifications
              {unread > 0 && (
                <span className="notif-header-badge">{unread} unread</span>
              )}
            </span>
            {unread > 0 && (
              <button
                className="notif-mark-all-btn"
                onClick={handleMarkAllRead}
                disabled={markingAll}
                title="Mark all as read"
              >
                <IconCheckAll />
                {markingAll ? 'Marking…' : 'Mark all read'}
              </button>
            )}
          </div>

          {/* body */}
          <div className="notif-dropdown-body">
            {loading ? (
              <div className="notif-empty">Loading…</div>
            ) : notifications.length === 0 ? (
              <div className="notif-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
                  aria-hidden="true" style={{ width: 32, height: 32, color: '#d1d5db', marginBottom: '0.5rem' }}>
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
                <p>No notifications yet</p>
              </div>
            ) : (
              <ul className="notif-list" role="list">
                {notifications.slice(0, 20).map(n => (
                  <li
                    key={n.id}
                    className={`notif-item${n.read ? ' notif-item--read' : ''}`}
                    style={{
                      borderLeft: `3px solid ${TYPE_COLOR[n.type] ?? '#6b7280'}`,
                      backgroundColor: n.read ? 'transparent' : (TYPE_BG[n.type] ?? '#f9fafb'),
                    }}
                  >
                    <div className="notif-item-body">
                      <p className="notif-item-title">{n.title}</p>
                      <p className="notif-item-msg">{n.message}</p>
                      <span className="notif-item-time">
                        {relativeTime(n.created_at)}
                      </span>
                    </div>
                    {!n.read && (
                      <button
                        className="notif-read-btn"
                        onClick={() => handleMarkRead(n.id)}
                        title="Mark as read"
                        aria-label="Mark as read"
                      >
                        ✓
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
