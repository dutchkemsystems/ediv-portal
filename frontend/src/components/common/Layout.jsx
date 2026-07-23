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
  Chip,
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
  AccountBalanceWallet as GrantsIcon,
  AdminPanelSettings as PrivilegesIcon,
  Domain as DepartmentIcon,
  Security as AuditIcon,
  Handshake as ParentTeacherIcon,
} from '@mui/icons-material'
import { logout } from '../../store/authSlice'

const drawerWidth = 260

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

const getMenuItems = (role) => {
  const allItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Schools', icon: <SchoolIcon />, path: '/schools' },
    { text: 'Staff', icon: <PeopleIcon />, path: '/staff' },
    { text: 'Students', icon: <PersonIcon />, path: '/students' },
    { text: 'Attendance', icon: <CalendarIcon />, path: '/attendance' },
    { text: 'Academics', icon: <LibraryIcon />, path: '/academics' },
    { text: 'Finance', icon: <FinanceIcon />, path: '/finance' },
    { text: 'Grants', icon: <GrantsIcon />, path: '/grants' },
    { text: 'Departments', icon: <DepartmentIcon />, path: '/departments' },
    { text: 'Audit & Compliance', icon: <AuditIcon />, path: '/audit' },
    { text: 'Parent-Teacher', icon: <ParentTeacherIcon />, path: '/parent-teacher' },
    { text: 'Privileges', icon: <PrivilegesIcon />, path: '/privileges' },
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
    HR: ['/dashboard', '/staff', '/hr', '/grants', '/reports', '/notifications'],
    FIN: ['/dashboard', '/finance', '/grants', '/reports', '/notifications'],
    AUDIT: ['/dashboard', '/audit', '/reports', '/notifications'],
    QA: ['/dashboard', '/reports', '/notifications', '/inspection'],
    CC: ['/dashboard', '/co-curricular', '/french', '/reports', '/notifications'],
    EMIS: ['/dashboard', '/reports', '/analytics', '/notifications'],
    PLAN: ['/dashboard', '/reports', '/analytics', '/notifications'],
    PROC: ['/dashboard', '/reports', '/notifications'],
    PA: ['/dashboard', '/communication', '/reports', '/notifications'],
    SA: ['/dashboard', '/schools', '/students', '/reports', '/notifications'],
    FRENCH: ['/dashboard', '/french', '/co-curricular', '/reports', '/notifications'],
    REG: ['/dashboard', '/registry', '/files', '/workflows', '/notifications'],
    REG_OFF: ['/dashboard', '/registry', '/files', '/workflows', '/notifications'],
    SA_OFF: ['/dashboard', '/schools', '/students', '/reports', '/notifications'],
    PRI: ['/dashboard', '/schools', '/students', '/staff', '/academics', '/attendance', '/timetable', '/reports', '/discipline', '/library', '/notifications'],
    VP: ['/dashboard', '/students', '/staff', '/academics', '/attendance', '/timetable', '/reports', '/discipline', '/notifications'],
    TCH: ['/dashboard', '/students', '/academics', '/attendance', '/timetable', '/e-learning', '/discipline', '/notifications'],
    STD: ['/dashboard', '/academics', '/attendance', '/library', '/e-learning', '/notifications'],
    PAR: ['/dashboard', '/students', '/finance', '/communication', '/parent-teacher', '/notifications'],
  }

  const allowedPaths = roleAccess[role] || ['/dashboard']
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
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, textAlign: 'center', bgcolor: lagosRed, color: 'white' }}>
        <Avatar sx={{ width: 56, height: 56, bgcolor: 'white', color: lagosRed, mx: 'auto', mb: 1, fontWeight: 700, fontSize: '1.1rem' }}>
          EDIV
        </Avatar>
        <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '0.95rem' }}>
          Education District IV
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.85 }}>
          Lagos State Ministry of Education
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ px: 2, py: 1.5, bgcolor: '#FFF5F5' }}>
        <Typography variant="subtitle2" noWrap sx={{ fontWeight: 600 }}>
          {user?.first_name} {user?.last_name}
        </Typography>
        <Chip
          label={user?.role}
          size="small"
          sx={{
            mt: 0.5,
            bgcolor: lagosRed,
            color: 'white',
            fontWeight: 500,
            fontSize: '0.7rem',
            height: 22,
          }}
        />
      </Box>
      <Divider />
      <List sx={{ py: 0.5, flex: 1, overflow: 'auto' }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => { navigate(item.path); setMobileOpen(false) }}
              sx={{
                py: 0.8,
                px: 2,
                '&:hover': { bgcolor: 'rgba(200, 16, 46, 0.08)' },
                '&.Mui-selected': { bgcolor: 'rgba(200, 16, 46, 0.12)' },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: lagosRed }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List sx={{ py: 0.5 }}>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout} sx={{ py: 0.8, px: 2, '&:hover': { bgcolor: 'rgba(211, 47, 47, 0.08)' } }}>
            <ListItemIcon sx={{ minWidth: 36, color: '#D32F2F' }}><LogoutIcon /></ListItemIcon>
            <ListItemText primary="Logout" primaryTypographyProps={{ variant: 'body2', color: '#D32F2F' }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ bgcolor: lagosRed }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2, display: { sm: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <SchoolIcon sx={{ mr: 1.5 }} />
          <Typography variant="h6" noWrap sx={{ flexGrow: 1, fontWeight: 600 }}>
            Education District IV Portal
          </Typography>
          <IconButton onClick={handleMenuOpen} sx={{ ml: 2 }}>
            <Badge color="error" variant="dot">
              <Avatar sx={{ bgcolor: 'white', color: lagosRed, width: 36, height: 36, fontWeight: 600 }}>
                {user?.first_name?.[0] || 'U'}
              </Avatar>
            </Badge>
          </IconButton>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
            <MenuItem disabled>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{user?.first_name} {user?.last_name}</Typography>
            </MenuItem>
            <MenuItem disabled>
              <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
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

      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, overflow: 'auto', bgcolor: '#F8F9FA' }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}

export default Layout
