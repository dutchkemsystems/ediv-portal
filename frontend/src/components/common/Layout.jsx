import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  AccountBalance as FinanceIcon,
  Assessment as ReportsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  CalendarToday as CalendarIcon,
  Work as WorkIcon,
  SwapHoriz as WorkflowIcon,
  Mail as MailIcon,
  Notifications as NotificationsIcon,
  Schedule as TimetableIcon,
  DirectionsBus as TransportIcon,
  Inventory as AssetIcon,
  Gavel as DisciplineIcon,
  MenuBook as LibraryIcon,
  Computer as ELearningIcon,
  LocalHospital as WellnessIcon,
  Groups as AlumniIcon,
  Architecture as InfraIcon,
  Search as InspectionIcon,
  Translate as FrenchIcon,
  EmojiEvents as CoCurIcon,
  TrendingUp as AnalyticsIcon,
} from '@mui/icons-material'
import { logout } from '../../store/authSlice'

const drawerWidth = 260

const getMenuItems = (role) => {
  const allItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Schools', icon: <SchoolIcon />, path: '/schools' },
    { text: 'Staff', icon: <PeopleIcon />, path: '/staff' },
    { text: 'Students', icon: <PersonIcon />, path: '/students' },
    { text: 'Attendance', icon: <CalendarIcon />, path: '/attendance' },
    { text: 'Academics', icon: <LibraryIcon />, path: '/academics' },
    { text: 'Finance', icon: <FinanceIcon />, path: '/finance' },
    { text: 'HR & Recruitment', icon: <WorkIcon />, path: '/hr' },
    { text: 'E-Registry', icon: <AssignmentIcon />, path: '/registry' },
    { text: 'Files', icon: <AssignmentIcon />, path: '/files' },
    { text: 'Workflows', icon: <WorkflowIcon />, path: '/workflows' },
    { text: 'Communication', icon: <MailIcon />, path: '/communication' },
    { text: 'Notifications', icon: <NotificationsIcon />, path: '/notifications' },
    { text: 'Timetable', icon: <TimetableIcon />, path: '/timetable' },
    { text: 'Transport', icon: <TransportIcon />, path: '/transport' },
    { text: 'Assets', icon: <AssetIcon />, path: '/assets' },
    { text: 'Discipline', icon: <DisciplineIcon />, path: '/discipline' },
    { text: 'Library', icon: <LibraryIcon />, path: '/library' },
    { text: 'E-Learning', icon: <ELearningIcon />, path: '/e-learning' },
    { text: 'Wellness', icon: <WellnessIcon />, path: '/wellness' },
    { text: 'Alumni', icon: <AlumniIcon />, path: '/alumni' },
    { text: 'Infrastructure', icon: <InfraIcon />, path: '/infrastructure' },
    { text: 'Inspection', icon: <InspectionIcon />, path: '/inspection' },
    { text: 'French Unit', icon: <FrenchIcon />, path: '/french' },
    { text: 'Co-Curricular', icon: <CoCurIcon />, path: '/co-curricular' },
    { text: 'CPD', icon: <AnalyticsIcon />, path: '/cpd' },
    { text: 'Reports', icon: <ReportsIcon />, path: '/reports' },
  ]

  const roleAccess = {
    SYSADMIN: allItems.map(i => i.path),
    TG: allItems.map(i => i.path),
    PS: allItems.map(i => i.path),
    HR: ['/', '/staff', '/hr', '/reports', '/notifications'],
    FIN: ['/', '/finance', '/reports', '/notifications'],
    AUDIT: ['/', '/finance', '/reports', '/notifications'],
    QA: ['/', '/reports', '/notifications', '/inspection'],
    CC: ['/', '/co-curricular', '/reports', '/notifications'],
    EMIS: ['/', '/reports', '/analytics', '/notifications'],
    PLAN: ['/', '/reports', '/analytics', '/notifications'],
    REG: ['/', '/registry', '/files', '/workflows', '/notifications'],
    PRI: ['/', '/schools', '/students', '/staff', '/academics', '/attendance', '/timetable', '/reports', '/discipline', '/library', '/notifications'],
    VP: ['/', '/students', '/staff', '/academics', '/attendance', '/timetable', '/reports', '/discipline', '/notifications'],
    TCH: ['/', '/students', '/academics', '/attendance', '/timetable', '/e-learning', '/discipline', '/notifications'],
    STD: ['/', '/academics', '/attendance', '/library', '/e-learning', '/notifications'],
    PAR: ['/', '/students', '/finance', '/communication', '/notifications'],
  }

  const allowedPaths = roleAccess[role] || roleAccess.TG
  return allItems.filter(i => allowedPaths.includes(i.path))
}

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState(null)
  const { user } = useSelector((state) => state.auth)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const menuItems = getMenuItems(user?.role)

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen)
  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget)
  const handleMenuClose = () => setAnchorEl(null)
  const handleLogout = () => { dispatch(logout()); navigate('/login') }

  const drawer = (
    <Box>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Avatar sx={{ width: 50, height: 50, bgcolor: '#1a237e', mx: 'auto', mb: 1 }}>EDIV</Avatar>
        <Typography variant="h6" sx={{ color: '#1a237e', fontWeight: 'bold', fontSize: '1rem' }}>
          EDIV Portal
        </Typography>
        <Typography variant="body2" color="text.secondary" fontSize="0.75rem">
          Education District IV
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ px: 2, py: 1, bgcolor: '#f5f5f5' }}>
        <Typography variant="subtitle2" noWrap fontSize="0.8rem">
          {user?.first_name} {user?.last_name}
        </Typography>
        <Typography variant="caption" color="text.secondary">{user?.role}</Typography>
      </Box>
      <Divider />
      <List sx={{ py: 0.5 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => { navigate(item.path); setMobileOpen(false) }}
              sx={{ py: 0.75, px: 2 }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2' }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List sx={{ py: 0.5 }}>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout} sx={{ py: 0.75, px: 2 }}>
            <ListItemIcon sx={{ minWidth: 36 }}><LogoutIcon /></ListItemIcon>
            <ListItemText primary="Logout" primaryTypographyProps={{ variant: 'body2' }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ bgcolor: '#1a237e' }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2, display: { sm: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>Education District IV Portal</Typography>
          <IconButton onClick={handleMenuOpen} sx={{ ml: 2 }}>
            <Badge color="error" variant="dot">
              <Avatar sx={{ bgcolor: '#f57c00', width: 36, height: 36 }}>
                {user?.first_name?.[0] || 'U'}
              </Avatar>
            </Badge>
          </IconButton>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
            <MenuItem disabled>
              <Typography variant="body2">{user?.email}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{ display: { xs: 'none', sm: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, overflow: 'hidden' } }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, overflow: 'auto' }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}

export default Layout
