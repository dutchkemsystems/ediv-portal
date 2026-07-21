import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Box,
  Divider,
  ListItemIcon,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Settings,
  ExitToApp,
} from '@mui/icons-material'
import { logout } from '../../store/authSlice'

function Header({ onMenuClick }) {
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifAnchorEl, setNotifAnchorEl] = useState(null)
  const { user } = useSelector((state) => state.auth)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleNotifOpen = (event) => {
    setNotifAnchorEl(event.currentTarget)
  }

  const handleNotifClose = () => {
    setNotifAnchorEl(null)
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
    handleMenuClose()
  }

  const handleProfile = () => {
    navigate('/profile')
    handleMenuClose()
  }

  const handleSettings = () => {
    navigate('/settings')
    handleMenuClose()
  }

  return (
    <AppBar
      position="fixed"
      sx={{
        bgcolor: '#1a237e',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap sx={{ flexGrow: 0, mr: 4 }}>
          Education District IV
        </Typography>

        <Box sx={{ flexGrow: 1 }} />

        {/* Notifications */}
        <IconButton
          color="inherit"
          onClick={handleNotifOpen}
          sx={{ mr: 1 }}
        >
          <Badge badgeContent={3} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <Menu
          anchorEl={notifAnchorEl}
          open={Boolean(notifAnchorEl)}
          onClose={handleNotifClose}
          PaperProps={{
            sx: { width: 320, maxHeight: 400 },
          }}
        >
          <MenuItem disabled>
            <Typography variant="subtitle2">Notifications</Typography>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleNotifClose}>
            <Typography variant="body2">No new notifications</Typography>
          </MenuItem>
        </Menu>

        {/* User Menu */}
        <IconButton onClick={handleMenuOpen} sx={{ ml: 1 }}>
          <Avatar
            sx={{
              bgcolor: '#f57c00',
              width: 40,
              height: 40,
            }}
          >
            {user?.first_name?.[0] || 'U'}
          </Avatar>
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem disabled>
            <Box>
              <Typography variant="subtitle2">
                {user?.first_name} {user?.last_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleProfile}>
            <ListItemIcon>
              <AccountCircle fontSize="small" />
            </ListItemIcon>
            Profile
          </MenuItem>
          <MenuItem onClick={handleSettings}>
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            Settings
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <ExitToApp fontSize="small" />
            </ListItemIcon>
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  )
}

export default Header
