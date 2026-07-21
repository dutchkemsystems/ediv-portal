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
} from '@mui/material'
import {
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  AttachMoney as MoneyIcon,
  Description as FileIcon,
  Task as TaskIcon,
} from '@mui/icons-material'
import api from '../api/client'

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
        console.error('Error fetching dashboard:', error)
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
    { title: 'Total Schools', value: stats?.total_schools || 0, icon: <SchoolIcon sx={{ fontSize: 48 }} />, color: '#1a237e', route: '/schools' },
    { title: 'Total Students', value: stats?.total_students || 0, icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: '#f57c00', route: '/students' },
    { title: 'Total Staff', value: stats?.total_staff || 0, icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: '#388e3c', route: '/staff' },
    { title: 'Active Files', value: stats?.active_files || 0, icon: <AssignmentIcon sx={{ fontSize: 48 }} />, color: '#d32f2f', route: '/registry' },
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
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.first_name || 'User'}
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Education District IV Portal Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardActionArea onClick={() => navigate(stat.route)}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h4" sx={{ color: stat.color }}>
                        {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stat.title}
                      </Typography>
                    </Box>
                    <Box sx={{ color: stat.color, opacity: 0.3 }}>
                      {stat.icon}
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
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
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <List dense>
              {actions.map((action, idx) => (
                <ListItem key={idx} button onClick={() => navigate(action.route)}>
                  <ListItemIcon>{action.icon}</ListItemIcon>
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
