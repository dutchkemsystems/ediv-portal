import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
  Button,
  Chip,
  Tooltip,
  CircularProgress,
} from '@mui/material'
import {
  Notifications as NotificationsIcon,
  Mail as MailIcon,
  Assignment as FileIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import api from '../../api/client'

function NotificationBell() {
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const open = Boolean(anchorEl)

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      const response = await api.get('/communication/notifications/?is_read=false&limit=10')
      const data = response.data.results || response.data || []
      setNotifications(Array.isArray(data) ? data : [])
      setUnreadCount(Array.isArray(data) ? data.length : 0)
    } catch (error) {
      console.error('Error fetching notifications:', error)
      setNotifications([])
      setUnreadCount(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNotifications()
    // Poll every 30 seconds
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [fetchNotifications])

  const handleOpen = (event) => {
    setAnchorEl(event.currentTarget)
    fetchNotifications()
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.post(`/communication/notifications/${notificationId}/mark_read/`)
      setNotifications((prev) => prev.filter((n) => n.id !== notificationId))
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const handleMarkAllRead = async () => {
    try {
      const unreadIds = notifications.map((n) => n.id)
      await Promise.all(
        unreadIds.map((id) => api.post(`/communication/notifications/${id}/mark_read/`))
      )
      setNotifications([])
      setUnreadCount(0)
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  const handleViewAll = () => {
    handleClose()
    navigate('/notifications')
  }

  const getNotificationIcon = (title) => {
    if (!title) return <InfoIcon fontSize="small" />
    const lower = title.toLowerCase()
    if (lower.includes('mail')) return <MailIcon fontSize="small" />
    if (lower.includes('file')) return <FileIcon fontSize="small" />
    if (lower.includes('success') || lower.includes('completed'))
      return <SuccessIcon fontSize="small" color="success" />
    if (lower.includes('warning') || lower.includes('overdue'))
      return <WarningIcon fontSize="small" color="warning" />
    if (lower.includes('error') || lower.includes('failed'))
      return <ErrorIcon fontSize="small" color="error" />
    return <InfoIcon fontSize="small" color="info" />
  }

  const getNotificationColor = (title) => {
    if (!title) return 'default'
    const lower = title.toLowerCase()
    if (lower.includes('mail')) return 'primary'
    if (lower.includes('file')) return 'secondary'
    if (lower.includes('success') || lower.includes('completed')) return 'success'
    if (lower.includes('warning') || lower.includes('overdue')) return 'warning'
    if (lower.includes('error') || lower.includes('failed')) return 'error'
    return 'default'
  }

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton color="inherit" onClick={handleOpen} sx={{ ml: 1 }}>
          <Badge badgeContent={unreadCount} color="error" max={99}>
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 380,
            maxHeight: 480,
            mt: 1,
            '& .MuiMenuItem-root': { py: 1.5 },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ px: 2, py: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Notifications
          </Typography>
          {unreadCount > 0 && (
            <Button size="small" onClick={handleMarkAllRead} sx={{ textTransform: 'none' }}>
              Mark all read
            </Button>
          )}
        </Box>
        <Divider />

        {loading && notifications.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : notifications.length === 0 ? (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No new notifications
            </Typography>
          </Box>
        ) : (
          notifications.slice(0, 8).map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleMarkAsRead(notification.id)}
              sx={{
                alignItems: 'flex-start',
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36, mt: 0.5 }}>
                {getNotificationIcon(notification.title)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.3 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, flex: 1 }}>
                      {notification.title}
                    </Typography>
                    <Chip
                      label={notification.notification_type}
                      size="small"
                      color={getNotificationColor(notification.title)}
                      sx={{ height: 18, fontSize: '0.6rem' }}
                    />
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      {notification.message}
                    </Typography>
                    <Typography variant="caption" color="text.disabled">
                      {new Date(notification.created_at).toLocaleString()}
                    </Typography>
                  </>
                }
              />
            </MenuItem>
          ))
        )}

        {notifications.length > 0 && (
          <>
            <Divider />
            <MenuItem onClick={handleViewAll} sx={{ justifyContent: 'center' }}>
              <Typography variant="body2" color="primary" sx={{ fontWeight: 500 }}>
                View All Notifications
              </Typography>
            </MenuItem>
          </>
        )}
      </Menu>
    </>
  )
}

export default NotificationBell
