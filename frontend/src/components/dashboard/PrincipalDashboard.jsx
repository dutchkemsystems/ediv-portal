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
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material'
import {
  People as PeopleIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  CalendarToday as CalendarIcon,
  Assignment as AssignmentIcon,
  Gavel as DisciplineIcon,
  AttachMoney as MoneyIcon,
  Task as TaskIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Schedule as TimetableIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function PrincipalDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [schoolData, setSchoolData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/principal_dashboard/')
      setSchoolData(res.data)
    } catch (error) {
      notify.error('Failed to load school dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleRefresh = () => { setRefreshing(true); fetchData() }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  const formatCurrency = (amount) => {
    if (!amount) return '₦0'
    if (amount >= 1000000) return `₦${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `₦${(amount / 1000).toFixed(1)}K`
    return `₦${Number(amount).toLocaleString()}`
  }

  const kpiCards = [
    {
      title: 'Total Students',
      value: (schoolData?.total_students || 0).toLocaleString(),
      icon: <PersonIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/students',
      trend: `${schoolData?.male_students || 0} male, ${schoolData?.female_students || 0} female`,
      trendColor: '#666',
    },
    {
      title: 'Total Staff',
      value: (schoolData?.total_staff || 0).toLocaleString(),
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/staff',
      trend: 'Active staff members',
      trendColor: '#666',
    },
    {
      title: 'Attendance Rate',
      value: `${schoolData?.attendance_rate || 0}%`,
      icon: <CalendarIcon sx={{ fontSize: 36 }} />,
      color: '#00695C',
      route: '/attendance',
      trend: 'Today',
      trendColor: lagosGreen,
    },
    {
      title: 'Fees Collected',
      value: formatCurrency(schoolData?.total_fees_collected),
      icon: <MoneyIcon sx={{ fontSize: 36 }} />,
      color: '#6A1B9A',
      route: '/finance',
      trend: `${formatCurrency(schoolData?.total_fees_due)} outstanding`,
      trendColor: '#E65100',
    },
    {
      title: 'Discipline',
      value: schoolData?.total_incidents || 0,
      icon: <DisciplineIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/discipline',
      trend: `${schoolData?.pending_incidents || 0} pending`,
      trendColor: schoolData?.pending_incidents > 0 ? '#C62828' : lagosGreen,
    },
    {
      title: 'Pending Tasks',
      value: schoolData?.pending_tasks?.length || 0,
      icon: <TaskIcon sx={{ fontSize: 36 }} />,
      color: '#AD1457',
      route: '/workflows',
      trend: 'Workflow tasks',
      trendColor: '#666',
    },
  ]

  // Attendance Trend Chart
  const attendanceTrendOptions = {
    chart: { type: 'line', toolbar: { show: false }, fontFamily: 'inherit' },
    colors: [lagosGreen, '#C62828'],
    dataLabels: { enabled: false },
    xaxis: {
      categories: schoolData?.attendance_trend?.map(t => {
        const d = new Date(t.date)
        return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
      }) || [],
      labels: { style: { fontSize: '10px' } },
    },
    yaxis: { labels: { style: { fontSize: '12px' } } },
    grid: { borderColor: '#f1f1f1' },
    stroke: { curve: 'smooth', width: 2 },
    markers: { size: 4 },
  }

  const attendanceTrendSeries = [
    { name: 'Present', data: schoolData?.attendance_trend?.map(t => t.present) || [] },
    { name: 'Absent', data: schoolData?.attendance_trend?.map(t => t.absent || (t.total - t.present)) || [] },
  ]

  // Gender Distribution Chart
  const genderPieOptions = {
    chart: { type: 'donut', fontFamily: 'inherit' },
    colors: ['#1565C0', '#E91E63'],
    labels: ['Male', 'Female'],
    dataLabels: { enabled: false },
    legend: { position: 'bottom', fontSize: '11px' },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            value: { show: true, fontSize: '14px', fontWeight: 700, formatter: (val) => parseInt(val).toLocaleString() },
          },
        },
      },
    },
  }

  const genderPieSeries = [schoolData?.male_students || 0, schoolData?.female_students || 0]

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'error'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'info'
      case 'LOW': return 'success'
      default: return 'default'
    }
  }

  const quickActions = [
    { label: 'Students', route: '/students', icon: <PersonIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'Staff', route: '/staff', icon: <PeopleIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
    { label: 'Attendance', route: '/attendance', icon: <CalendarIcon />, color: '#00695C', bgColor: '#E0F2F1' },
    { label: 'Academics', route: '/academics', icon: <AssignmentIcon />, color: '#6A1B9A', bgColor: '#F3E5F5' },
    { label: 'Discipline', route: '/discipline', icon: <DisciplineIcon />, color: '#E65100', bgColor: '#FFF3E0' },
    { label: 'Finance', route: '/finance', icon: <MoneyIcon />, color: '#6A1B9A', bgColor: '#F3E5F5' },
    { label: 'Timetable', route: '/timetable', icon: <TimetableIcon />, color: '#00695C', bgColor: '#E0F2F1' },
    { label: 'Reports', route: '/reports', icon: <AssignmentIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
  ]

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, ${lagosRed} 0%, #8B0000 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {schoolData?.school_name || 'School'} Dashboard
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'Principal'} — School Operations Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`${schoolData?.total_students || 0} Students`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                <Chip label={`${schoolData?.total_staff || 0} Staff`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                {schoolData?.pending_incidents > 0 && (
                  <Chip label={`${schoolData.pending_incidents} Pending Issues`} size="small" sx={{ bgcolor: '#E65100', color: 'white', fontSize: '0.7rem' }} />
                )}
              </Box>
            </Box>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} sx={{ color: 'white' }} disabled={refreshing}>
                <RefreshIcon sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
              </IconButton>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      {/* KPI Cards - Row 1 */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {kpiCards.slice(0, 4).map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{
              borderLeft: `4px solid ${card.color}`,
              boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.12)' },
            }}>
              <CardActionArea onClick={() => navigate(card.route)}>
                <CardContent sx={{ py: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h4" sx={{ color: card.color, fontWeight: 700, fontSize: '1.6rem' }}>
                        {card.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {card.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: card.trendColor, fontSize: '0.7rem' }}>
                        {card.trend}
                      </Typography>
                    </Box>
                    <Box sx={{ color: card.color, opacity: 0.2 }}>{card.icon}</Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* KPI Cards - Row 2 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpiCards.slice(4, 6).map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{
              borderLeft: `4px solid ${card.color}`,
              boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.12)' },
            }}>
              <CardActionArea onClick={() => navigate(card.route)}>
                <CardContent sx={{ py: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h4" sx={{ color: card.color, fontWeight: 700, fontSize: '1.6rem' }}>
                        {card.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {card.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: card.trendColor, fontSize: '0.7rem' }}>
                        {card.trend}
                      </Typography>
                    </Box>
                    <Box sx={{ color: card.color, opacity: 0.2 }}>{card.icon}</Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Attendance Trend (7 Days)
            </Typography>
            {attendanceTrendSeries[0]?.data?.length > 0 ? (
              <Chart options={attendanceTrendOptions} series={attendanceTrendSeries} type="line" height={220} />
            ) : (
              <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No attendance data</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Student Gender Distribution
            </Typography>
            {(genderPieSeries[0] + genderPieSeries[1]) > 0 ? (
              <Chart options={genderPieOptions} series={genderPieSeries} type="donut" height={220} />
            ) : (
              <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row: Recent Incidents + Pending Tasks + Quick Actions */}
      <Grid container spacing={2}>
        {/* Recent Discipline Incidents */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                Recent Incidents
              </Typography>
              <Typography variant="caption" sx={{ color: lagosRed, cursor: 'pointer', fontWeight: 500 }} onClick={() => navigate('/discipline')}>
                View All →
              </Typography>
            </Box>
            {schoolData?.recent_incidents?.length > 0 ? (
              <List dense disablePadding>
                {schoolData.recent_incidents.map((incident, idx) => (
                  <ListItem key={idx} sx={{ py: 0.8, px: 1, mb: 0.5, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <WarningIcon sx={{ fontSize: 16, color: getSeverityColor(incident.severity) === 'error' ? '#C62828' : getSeverityColor(incident.severity) === 'warning' ? '#E65100' : '#666' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {incident.student__first_name} {incident.student__last_name}
                      </Typography>}
                      secondary={<Box sx={{ display: 'flex', gap: 0.5, mt: 0.3 }}>
                        <Chip label={incident.incident_type} size="small" sx={{ fontSize: '0.6rem', height: 18 }} />
                        <Chip label={incident.severity} size="small" color={getSeverityColor(incident.severity)} sx={{ fontSize: '0.6rem', height: 18 }} />
                      </Box>}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 3, textAlign: 'center' }}>
                <Typography color="text.secondary" variant="body2">No recent incidents</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Pending Tasks */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)', height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                Pending Tasks
              </Typography>
              <Typography variant="caption" sx={{ color: lagosRed, cursor: 'pointer', fontWeight: 500 }} onClick={() => navigate('/workflows')}>
                View All →
              </Typography>
            </Box>
            {schoolData?.pending_tasks?.length > 0 ? (
              <List dense disablePadding>
                {schoolData.pending_tasks.map((task, idx) => (
                  <ListItem key={idx} sx={{ py: 0.8, px: 1, mb: 0.5, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <TaskIcon sx={{ fontSize: 16, color: task.status === 'IN_PROGRESS' ? '#E65100' : '#1565C0' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {task.workflow_instance__reference_number || 'Task'}
                      </Typography>}
                      secondary={<Box sx={{ display: 'flex', gap: 0.5, mt: 0.3 }}>
                        <Chip label={task.status} size="small" sx={{ fontSize: '0.6rem', height: 18, bgcolor: task.status === 'IN_PROGRESS' ? '#FFF3E0' : '#E3F2FD', color: task.status === 'IN_PROGRESS' ? '#E65100' : '#1565C0' }} />
                        {task.due_date && <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>Due: {task.due_date}</Typography>}
                      </Box>}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 3, textAlign: 'center' }}>
                <CheckIcon sx={{ color: lagosGreen, fontSize: 32, mb: 1 }} />
                <Typography color="text.secondary" variant="body2">All caught up!</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions + Recent Activity */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Quick Actions */}
            <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
                Quick Actions
              </Typography>
              <Grid container spacing={1}>
                {quickActions.map((action, idx) => (
                  <Grid item xs={6} key={idx}>
                    <Box onClick={() => navigate(action.route)} sx={{
                      display: 'flex', alignItems: 'center', gap: 0.8, p: 1,
                      bgcolor: action.bgColor, borderRadius: 1, cursor: 'pointer',
                      border: `1px solid ${action.color}20`, transition: 'all 0.2s',
                      '&:hover': { bgcolor: `${action.color}15`, borderColor: `${action.color}40`, transform: 'translateY(-1px)' },
                    }}>
                      <Box sx={{ color: action.color, fontSize: 18 }}>{action.icon}</Box>
                      <Typography variant="caption" sx={{ fontWeight: 500, fontSize: '0.75rem' }}>{action.label}</Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Paper>

            {/* Recent Staff Activity */}
            <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
                Recent Staff Activity
              </Typography>
              {schoolData?.recent_activity?.length > 0 ? (
                <List dense disablePadding>
                  {schoolData.recent_activity.map((activity, idx) => (
                    <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={<Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                          {activity.user__first_name} {activity.user__last_name}
                        </Typography>}
                        secondary={<Typography variant="caption" color="text.secondary">
                          {activity.designation?.replace('_', ' ')} • {activity.updated_at ? new Date(activity.updated_at).toLocaleDateString() : ''}
                        </Typography>}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary" variant="body2" sx={{ py: 2, textAlign: 'center' }}>No recent activity</Typography>
              )}
            </Paper>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default PrincipalDashboard
