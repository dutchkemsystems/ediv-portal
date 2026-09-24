import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Avatar,
  Collapse,
} from '@mui/material'
import {
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
  MenuBook as LibraryIcon,
  Sports as SportsIcon,
  Science as ScienceIcon,
  LocalHospital as WellnessIcon,
  TrendingUp as AnalyticsIcon,
  Work as WorkIcon,
  SwapHoriz as WorkflowIcon,
  Mail as MailIcon,
  Notifications as NotificationsIcon,
  Schedule as TimetableIcon,
  DirectionsBus as TransportIcon,
  Inventory as AssetIcon,
  Gavel as DisciplineIcon,
  Computer as ELearningIcon,
  Groups as AlumniIcon,
  Architecture as InfraIcon,
  Search as InspectionIcon,
  Translate as FrenchIcon,
  EmojiEvents as CoCurIcon,
  School as CPDIcon,
  ExpandLess,
  ExpandMore,
  Payment as PaymentIcon,
} from '@mui/icons-material'
import { logout } from '../../store/authSlice'

const DRAWER_WIDTH = 260

const getMenuItems = (role) => {
  const items = [
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
    { text: 'CPD', icon: <CPDIcon />, path: '/cpd' },
    { text: 'Reports', icon: <ReportsIcon />, path: '/reports' },
  ]

  const roleAccess = {
    SYSADMIN: items.map(i => i.path),
    TG: items.map(i => i.path),
    PS: items.map(i => i.path),
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
  return items.filter(i => allowedPaths.includes(i.path))
}

function Sidebar() {
  const { user } = useSelector((state) => state.auth)
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = getMenuItems(user?.role)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Avatar sx={{ width: 60, height: 60, bgcolor: '#1a237e', mx: 'auto', mb: 1 }}>EDIV</Avatar>
        <Typography variant="h6" sx={{ color: '#1a237e', fontWeight: 'bold' }}>Education District IV</Typography>
        <Typography variant="body2" color="text.secondary">Portal</Typography>
      </Box>
      <Divider />
      <Box sx={{ p: 2, bgcolor: '#f5f5f5' }}>
        <Typography variant="subtitle2" noWrap>{user?.first_name} {user?.last_name}</Typography>
        <Typography variant="caption" color="text.secondary">{user?.role}</Typography>
      </Box>
      <Divider />
      <List sx={{ flexGrow: 1, overflow: 'auto' }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                py: 0.5,
                '&.Mui-selected': { bgcolor: '#e8eaf6', '&:hover': { bgcolor: '#c5cae9' }, borderRight: '3px solid #1a237e' },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2' }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon sx={{ minWidth: 36 }}><LogoutIcon /></ListItemIcon>
            <ListItemText primary="Logout" primaryTypographyProps={{ variant: 'body2' }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )
}

export default Sidebar
