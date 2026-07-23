import React, { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActionArea,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material'
import {
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  AttachMoney as MoneyIcon,
  Description as FileIcon,
  Task as TaskIcon,
  Visibility as VisionIcon,
  EmojiObjects as MissionIcon,
  DirectionsBus as TrafficIcon,
  LocalHospital as HealthIcon,
  MenuBook as EducationIcon,
  AccountBalance as EconomyIcon,
  Celebration as EntertainmentIcon,
  Shield as SecurityPolicyIcon,
} from '@mui/icons-material'
import api from '../api/client'
import { notify } from '../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'
const lagosGold = '#D4A017'

const themesData = [
  { letter: 'T', title: 'Traffic & Transport', icon: <TrafficIcon sx={{ fontSize: 20 }} />, color: '#1565C0' },
  { letter: 'H', title: 'Health & Environment', icon: <HealthIcon sx={{ fontSize: 20 }} />, color: '#2E7D32' },
  { letter: 'E', title: 'Education & Technology', icon: <EducationIcon sx={{ fontSize: 20 }} />, color: '#C8102E' },
  { letter: 'M', title: '21st Century Economy', icon: <EconomyIcon sx={{ fontSize: 20 }} />, color: '#6A1B9A' },
  { letter: 'S', title: 'Entertainment & Tourism', icon: <EntertainmentIcon sx={{ fontSize: 20 }} />, color: '#E65100' },
  { letter: '+', title: 'Security & Governance', icon: <SecurityPolicyIcon sx={{ fontSize: 20 }} />, color: '#37474F' },
]

function Dashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [statsRes, activityRes] = await Promise.all([
          api.get('/analytics/stats/overview/'),
          api.get('/analytics/stats/recent_activity/').catch(() => ({ data: {} })),
        ])
        setStats(statsRes.data)
        setActivity(activityRes.data)
      } catch (error) {
        notify.error('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  const statCards = [
    { title: 'Total Schools', value: stats?.total_schools || 0, icon: <SchoolIcon sx={{ fontSize: 48 }} />, color: lagosRed, route: '/schools' },
    { title: 'Total Students', value: stats?.total_students || 0, icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: '#1565C0', route: '/students' },
    { title: 'Total Staff', value: stats?.total_staff || 0, icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: lagosGreen, route: '/staff' },
    { title: 'Active Files', value: stats?.active_files || 0, icon: <AssignmentIcon sx={{ fontSize: 48 }} />, color: '#6A1B9A', route: '/registry' },
  ]

  const quickActions = {
    SYSADMIN: [
      { label: 'Manage Schools', route: '/schools', icon: <SchoolIcon /> },
      { label: 'Manage Users', route: '/staff', icon: <PeopleIcon /> },
      { label: 'View Reports', route: '/reports', icon: <AssignmentIcon /> },
    ],
    TG: [
      { label: 'School Overview', route: '/schools', icon: <SchoolIcon /> },
      { label: 'Staff Directory', route: '/staff', icon: <PeopleIcon /> },
      { label: 'Finance Overview', route: '/finance', icon: <MoneyIcon /> },
    ],
    HR: [
      { label: 'Staff Management', route: '/staff', icon: <PeopleIcon /> },
      { label: 'HR Module', route: '/hr', icon: <PeopleIcon /> },
      { label: 'View Reports', route: '/reports', icon: <AssignmentIcon /> },
    ],
    FIN: [
      { label: 'Finance Module', route: '/finance', icon: <MoneyIcon /> },
      { label: 'Fee Management', route: '/finance', icon: <MoneyIcon /> },
      { label: 'Budget Reports', route: '/reports', icon: <AssignmentIcon /> },
    ],
    PRI: [
      { label: 'School Dashboard', route: '/schools', icon: <SchoolIcon /> },
      { label: 'Student Records', route: '/students', icon: <PeopleIcon /> },
      { label: 'Attendance', route: '/attendance', icon: <AssignmentIcon /> },
    ],
    TCH: [
      { label: 'My Classes', route: '/academics', icon: <SchoolIcon /> },
      { label: 'Attendance', route: '/attendance', icon: <AssignmentIcon /> },
      { label: 'My Tasks', route: '/workflows', icon: <TaskIcon /> },
    ],
  }

  const actions = quickActions[user?.role] || quickActions.TG

  return (
    <Box>
      {/* Welcome Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: '#333' }}>
          Welcome, {user?.first_name || 'User'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Education District IV Portal Dashboard
        </Typography>
      </Box>

      {/* Vision & Mission Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderLeft: `4px solid ${lagosRed}`, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <CardContent sx={{ py: 2.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <VisionIcon sx={{ color: lagosRed, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: lagosRed, fontSize: '1rem' }}>
                  Our Vision
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#555', lineHeight: 1.6 }}>
                To be the leading education district in Lagos State, providing quality,
                inclusive, and technology-driven education that empowers every student
                to reach their full potential.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderLeft: `4px solid ${lagosGreen}`, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <CardContent sx={{ py: 2.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <MissionIcon sx={{ color: lagosGreen, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: lagosGreen, fontSize: '1rem' }}>
                  Our Mission
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#555', lineHeight: 1.6 }}>
                To deliver exceptional educational services through effective management
                of schools, dedicated staff, and innovative programs while maintaining
                high academic standards and ICT integration.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* T.H.E.M.E.S. Plus Banner */}
      <Card sx={{ mb: 3, bgcolor: '#1a1a2e', color: 'white', overflow: 'visible' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="overline" sx={{ color: lagosGold, letterSpacing: 2, fontWeight: 600 }}>
              T.H.E.M.E.S. Plus Agenda
            </Typography>
            <Chip
              label="Gov. Sanwo-Olu"
              size="small"
              sx={{ bgcolor: lagosGold, color: '#1a1a2e', fontWeight: 600, fontSize: '0.7rem' }}
            />
          </Box>
          <Grid container spacing={2}>
            {themesData.map((theme) => (
              <Grid item xs={6} sm={4} md={2} key={theme.letter}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    p: 1.5,
                    borderRadius: 1.5,
                    bgcolor: 'rgba(255,255,255,0.08)',
                    border: `1px solid ${theme.color}40`,
                    transition: 'all 0.2s',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.15)', borderColor: theme.color },
                  }}
                >
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '8px',
                      bgcolor: theme.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontSize: '1rem',
                      flexShrink: 0,
                    }}
                  >
                    {theme.letter}
                  </Box>
                  <Typography variant="caption" sx={{ lineHeight: 1.3, opacity: 0.9 }}>
                    {theme.title}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Stat Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardActionArea onClick={() => navigate(stat.route)}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h4" sx={{ color: stat.color, fontWeight: 700 }}>
                        {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        {stat.title}
                      </Typography>
                    </Box>
                    <Box sx={{ color: stat.color, opacity: 0.2 }}>
                      {stat.icon}
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Activity & Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Recent Activity
            </Typography>
            {activity?.recent_files?.length > 0 ? (
              <List dense>
                {activity.recent_files.map((file, idx) => (
                  <ListItem key={idx}>
                    <ListItemIcon><FileIcon /></ListItemIcon>
                    <ListItemText
                      primary={`${file.file__title || 'File'} — ${file.action}`}
                      secondary={`${file.from_holder__first_name || ''} → ${file.to_holder__first_name || ''}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : activity?.recent_tasks?.length > 0 ? (
              <List dense>
                {activity.recent_tasks.map((task, idx) => (
                  <ListItem key={idx}>
                    <ListItemIcon><TaskIcon /></ListItemIcon>
                    <ListItemText
                      primary={`Task: ${task.workflow_instance__reference_number}`}
                      secondary={
                        <Chip
                          label={task.status}
                          size="small"
                          color={task.status === 'COMPLETED' ? 'success' : task.status === 'PENDING' ? 'warning' : 'default'}
                        />
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">No recent activity to display.</Typography>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Quick Actions
            </Typography>
            <List dense>
              {actions.map((action, idx) => (
                <ListItem key={idx} button onClick={() => navigate(action.route)} sx={{ borderRadius: 1, mb: 0.5 }}>
                  <ListItemIcon sx={{ color: lagosRed }}>{action.icon}</ListItemIcon>
                  <ListItemText primary={action.label} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
