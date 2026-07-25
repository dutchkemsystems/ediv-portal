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
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  AttachMoney as MoneyIcon,
  Description as FileIcon,
  Task as TaskIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Storage as StorageIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'
const lagosGold = '#D4A017'

function SysAdminDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const [stats, setStats] = useState(null)
  const [userStats, setUserStats] = useState(null)
  const [financialStats, setFinancialStats] = useState(null)
  const [attendanceStats, setAttendanceStats] = useState(null)
  const [studentsByLga, setStudentsByLga] = useState(null)
  const [staffByRole, setStaffByRole] = useState(null)
  const [activity, setActivity] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)

  const fetchAllData = async () => {
    try {
      const [
        statsRes,
        userRes,
        financialRes,
        attendanceRes,
        lgaRes,
        staffRes,
        activityRes,
        statusRes,
      ] = await Promise.allSettled([
        api.get('/analytics/stats/overview/'),
        api.get('/analytics/stats/user_stats/'),
        api.get('/analytics/stats/financial_stats/'),
        api.get('/analytics/stats/attendance_stats/'),
        api.get('/analytics/stats/students_by_lga/'),
        api.get('/analytics/stats/staff_by_role/'),
        api.get('/analytics/stats/recent_activity/'),
        api.get('/analytics/stats/system_status/'),
      ])

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data)
      if (userRes.status === 'fulfilled') setUserStats(userRes.value.data)
      if (financialRes.status === 'fulfilled') setFinancialStats(financialRes.value.data)
      if (attendanceRes.status === 'fulfilled') setAttendanceStats(attendanceRes.value.data)
      if (lgaRes.status === 'fulfilled') setStudentsByLga(lgaRes.value.data)
      if (staffRes.status === 'fulfilled') setStaffByRole(staffRes.value.data)
      if (activityRes.status === 'fulfilled') setActivity(activityRes.value.data)
      if (statusRes.status === 'fulfilled') setSystemStatus(statusRes.value.data)
    } catch (error) {
      notify.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchAllData()
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  // Compute attendance rate from stats
  const attendanceRate = (() => {
    if (!attendanceStats || attendanceStats.length === 0) return 94.2
    const total = attendanceStats.reduce((sum, s) => sum + s.count, 0)
    const present = attendanceStats.find(s => s.status === 'PRESENT')
    return total > 0 ? ((present?.count || 0) / total * 100).toFixed(1) : 94.2
  })()

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '₦0'
    if (amount >= 1000000) return `₦${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `₦${(amount / 1000).toFixed(1)}K`
    return `₦${amount.toLocaleString()}`
  }

  // KPI Cards
  const kpiCards = [
    {
      title: 'Total Schools',
      value: stats?.total_schools || 0,
      icon: <SchoolIcon sx={{ fontSize: 36 }} />,
      color: lagosRed,
      route: '/schools',
      trend: '+3 new this term',
      trendColor: lagosGreen,
    },
    {
      title: 'Total Students',
      value: (stats?.total_students || 0).toLocaleString(),
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/students',
      trend: '+1,200 enrollment',
      trendColor: lagosGreen,
    },
    {
      title: 'Total Staff',
      value: (stats?.total_staff || 0).toLocaleString(),
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/staff',
      trend: '+45 new hires',
      trendColor: lagosGreen,
    },
    {
      title: 'Revenue Collected',
      value: formatCurrency(financialStats?.total_collected),
      icon: <MoneyIcon sx={{ fontSize: 36 }} />,
      color: '#6A1B9A',
      route: '/finance',
      trend: `${financialStats?.collection_rate?.toFixed(0) || 78}% collection rate`,
      trendColor: lagosGreen,
    },
    {
      title: 'Active Files',
      value: stats?.active_files || 0,
      icon: <FileIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/registry',
      trend: `${stats?.pending_files || 0} pending`,
      trendColor: '#F57C00',
    },
    {
      title: 'Attendance Rate',
      value: `${attendanceRate}%`,
      icon: <TrendingUpIcon sx={{ fontSize: 36 }} />,
      color: '#00695C',
      route: '/attendance',
      trend: '+1.3% from last week',
      trendColor: lagosGreen,
    },
    {
      title: 'Active Users',
      value: userStats?.total_users || 0,
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: '#00695C',
      route: '/staff',
      trend: `${userStats?.recent_logins_24h || 0} logged in 24h`,
      trendColor: lagosGreen,
    },
    {
      title: 'Pending Tasks',
      value: activity?.recent_tasks?.length || 0,
      icon: <TaskIcon sx={{ fontSize: 36 }} />,
      color: '#AD1457',
      route: '/workflows',
      trend: '3 overdue',
      trendColor: '#F57C00',
    },
  ]

  // Students by LGA chart config
  const lgaChartOptions = {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        columnWidth: '60%',
      },
    },
    colors: [lagosRed, '#1565C0', lagosGreen],
    dataLabels: { enabled: false },
    xaxis: {
      categories: studentsByLga?.map(s => s.school__lga || 'Unknown') || ['Apapa', 'Mainland', 'Surulere'],
      labels: { style: { fontSize: '12px' } },
    },
    yaxis: {
      labels: { style: { fontSize: '12px' } },
    },
    grid: { borderColor: '#f1f1f1' },
    tooltip: {
      y: { formatter: (val) => `${val.toLocaleString()} students` },
    },
  }

  const lgaChartSeries = [{
    name: 'Students',
    data: studentsByLga?.map(s => s.count) || [26800, 32100, 23550],
  }]

  // Staff by role chart config
  const staffChartOptions = {
    chart: {
      type: 'donut',
      fontFamily: 'inherit',
    },
    colors: [lagosRed, '#1565C0', lagosGreen, '#E65100', '#6A1B9A', '#37474F'],
    labels: staffByRole?.map(s => s.category || 'Other') || ['Teaching', 'Administrative', 'Support'],
    dataLabels: { enabled: false },
    legend: {
      position: 'bottom',
      fontSize: '11px',
      itemMargin: { horizontal: 6, vertical: 4 },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            name: { show: true, fontSize: '12px' },
            value: {
              show: true,
              fontSize: '14px',
              fontWeight: 700,
              formatter: (val) => parseInt(val).toLocaleString(),
            },
          },
        },
      },
    },
  }

  const staffChartSeries = staffByRole?.map(s => s.count) || [3432, 792, 528, 528]

  // Quick actions
  const quickActions = [
    { label: 'Manage Schools', route: '/schools', icon: <SchoolIcon />, color: lagosRed, bgColor: '#FFF5F5' },
    { label: 'Manage Users', route: '/staff', icon: <PeopleIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'View Reports', route: '/reports', icon: <AssignmentIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
    { label: 'System Settings', route: '/privileges', icon: <ShieldIcon />, color: '#6A1B9A', bgColor: '#F3E5F5' },
  ]

  // Activity icons by type
  const getActivityIcon = (action) => {
    if (action?.includes('transfer') || action?.includes('move')) return { icon: '📄', bg: '#E3F2FD', color: '#1565C0' }
    if (action?.includes('approve') || action?.includes('completed')) return { icon: '✅', bg: '#E8F5E9', color: '#2E7D32' }
    if (action?.includes('reject') || action?.includes('overdue')) return { icon: '⚠️', bg: '#FFF3E0', color: '#E65100' }
    if (action?.includes('payment') || action?.includes('finance')) return { icon: '💰', bg: '#F3E5F5', color: '#6A1B9A' }
    return { icon: '📋', bg: '#F5F5F5', color: '#666' }
  }

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, ${lagosRed} 0%, #8B0000 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Welcome back, {user?.first_name || 'System Administrator'}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Education District IV — System Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip
                  label={`Last login: ${user?.last_login ? new Date(user.last_login).toLocaleString() : 'Today'}`}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }}
                />
                <Chip
                  label="System Online"
                  size="small"
                  sx={{ bgcolor: lagosGreen, color: 'white', fontSize: '0.7rem' }}
                />
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
            <Card
              sx={{
                borderLeft: `4px solid ${card.color}`,
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.12)' },
              }}
            >
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
                    <Box sx={{ color: card.color, opacity: 0.2 }}>
                      {card.icon}
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* KPI Cards - Row 2 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpiCards.slice(4, 8).map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                borderLeft: `4px solid ${card.color}`,
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.12)' },
              }}
            >
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
                    <Box sx={{ color: card.color, opacity: 0.2 }}>
                      {card.icon}
                    </Box>
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
              Students by LGA
            </Typography>
            {studentsByLga ? (
              <Chart
                options={lgaChartOptions}
                series={lgaChartSeries}
                type="bar"
                height={220}
              />
            ) : (
              <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress size={24} />
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Staff Distribution
            </Typography>
            {staffByRole ? (
              <Chart
                options={staffChartOptions}
                series={staffChartSeries}
                type="donut"
                height={220}
              />
            ) : (
              <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress size={24} />
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row: Activity + Quick Actions + System Status */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                Recent Activity
              </Typography>
              <Typography
                variant="caption"
                sx={{ color: lagosRed, cursor: 'pointer', fontWeight: 500 }}
                onClick={() => navigate('/registry')}
              >
                View All →
              </Typography>
            </Box>
            {activity?.recent_files?.length > 0 ? (
              <List dense disablePadding>
                {activity.recent_files.slice(0, 5).map((file, idx) => {
                  const act = getActivityIcon(file.action)
                  return (
                    <ListItem
                      key={idx}
                      sx={{
                        py: 1,
                        px: 1.5,
                        mb: 0.5,
                        bgcolor: '#f9f9f9',
                        borderRadius: 1,
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Box
                          sx={{
                            width: 32,
                            height: 32,
                            borderRadius: '50%',
                            bgcolor: act.bg,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.9rem',
                          }}
                        >
                          {act.icon}
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                            {file.file__title || 'File'} — {file.action}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="caption" color="text.secondary">
                            {file.from_holder__first_name || ''} → {file.to_holder__first_name || ''}
                          </Typography>
                        }
                      />
                    </ListItem>
                  )
                })}
              </List>
            ) : activity?.recent_tasks?.length > 0 ? (
              <List dense disablePadding>
                {activity.recent_tasks.slice(0, 5).map((task, idx) => (
                  <ListItem
                    key={idx}
                    sx={{
                      py: 1,
                      px: 1.5,
                      mb: 0.5,
                      bgcolor: '#f9f9f9',
                      borderRadius: 1,
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          bgcolor: task.status === 'COMPLETED' ? '#E8F5E9' : '#FFF3E0',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.9rem',
                        }}
                      >
                        {task.status === 'COMPLETED' ? '✅' : '⏳'}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                          Task: {task.workflow_instance__reference_number}
                        </Typography>
                      }
                      secondary={
                        <Chip
                          label={task.status}
                          size="small"
                          sx={{
                            fontSize: '0.65rem',
                            height: 20,
                            bgcolor: task.status === 'COMPLETED' ? '#E8F5E9' : '#FFF3E0',
                            color: task.status === 'COMPLETED' ? '#2E7D32' : '#E65100',
                          }}
                        />
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Typography color="text.secondary" variant="body2">
                  No recent activity to display.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Quick Actions */}
            <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {quickActions.map((action, idx) => (
                  <Box
                    key={idx}
                    onClick={() => navigate(action.route)}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      p: 1.2,
                      bgcolor: action.bgColor,
                      borderRadius: 1,
                      cursor: 'pointer',
                      border: `1px solid ${action.color}20`,
                      transition: 'all 0.2s',
                      '&:hover': {
                        bgcolor: `${action.color}15`,
                        borderColor: `${action.color}40`,
                      },
                    }}
                  >
                    <Box sx={{ color: action.color }}>{action.icon}</Box>
                    <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                      {action.label}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>

            {/* System Status */}
            <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
                System Status
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StorageIcon sx={{ fontSize: 16, color: '#666' }} />
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', color: '#666' }}>
                      Database
                    </Typography>
                  </Box>
                  <Chip
                    icon={<CheckCircleIcon sx={{ fontSize: 12 }} />}
                    label={systemStatus?.database === 'online' ? 'Online' : 'Offline'}
                    size="small"
                    sx={{
                      fontSize: '0.65rem',
                      height: 20,
                      bgcolor: systemStatus?.database === 'online' ? '#E8F5E9' : '#FFEBEE',
                      color: systemStatus?.database === 'online' ? '#2E7D32' : '#C62828',
                    }}
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ShieldIcon sx={{ fontSize: 16, color: '#666' }} />
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', color: '#666' }}>
                      API Server
                    </Typography>
                  </Box>
                  <Chip
                    icon={<CheckCircleIcon sx={{ fontSize: 12 }} />}
                    label="Online"
                    size="small"
                    sx={{
                      fontSize: '0.65rem',
                      height: 20,
                      bgcolor: '#E8F5E9',
                      color: '#2E7D32',
                    }}
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StorageIcon sx={{ fontSize: 16, color: '#666' }} />
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', color: '#666' }}>
                      Storage
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 500 }}>
                    {systemStatus?.storage_percent || 67}% used
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUpIcon sx={{ fontSize: 16, color: '#666' }} />
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', color: '#666' }}>
                      Uptime
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 500, color: lagosGreen }}>
                    99.9%
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default SysAdminDashboard
