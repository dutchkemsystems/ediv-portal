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
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  Work as WorkIcon,
  EventBusy as LeaveIcon,
  Refresh as RefreshIcon,
  Block as SuspendedIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function HRDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [hrData, setHrData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/hr_dashboard/')
      setHrData(res.data)
    } catch (error) {
      notify.error('Failed to load HR dashboard data')
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

  const kpiCards = [
    {
      title: 'Total Staff',
      value: hrData?.total_staff || 0,
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: lagosRed,
      route: '/staff',
      trend: `${hrData?.new_hires_30d || 0} new hires (30d)`,
      trendColor: lagosGreen,
    },
    {
      title: 'Pending Leaves',
      value: hrData?.pending_leaves || 0,
      icon: <LeaveIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/hr',
      trend: `${hrData?.approved_leaves || 0} approved`,
      trendColor: lagosGreen,
    },
    {
      title: 'New Hires (30d)',
      value: hrData?.new_hires_30d || 0,
      icon: <PersonAddIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/staff',
      trend: 'Last 30 days',
      trendColor: '#666',
    },
    {
      title: 'Suspended',
      value: hrData?.suspended || 0,
      icon: <SuspendedIcon sx={{ fontSize: 36 }} />,
      color: '#C62828',
      route: '/staff',
      trend: 'Active suspensions',
      trendColor: '#C62828',
    },
  ]

  const categoryChartOptions = {
    chart: { type: 'donut', fontFamily: 'inherit' },
    colors: [lagosRed, '#1565C0', lagosGreen, '#E65100', '#6A1B9A'],
    labels: hrData?.by_category?.map(c => c.category || 'Other') || [],
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

  const categoryChartSeries = hrData?.by_category?.map(c => c.count) || []

  const designationChartOptions = {
    chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    colors: [lagosRed],
    dataLabels: { enabled: false },
    xaxis: {
      categories: hrData?.by_designation?.map(d => d.designation?.replace('_', ' ') || '') || [],
      labels: { style: { fontSize: '10px' }, rotate: -45 },
    },
    yaxis: { labels: { style: { fontSize: '12px' } } },
    grid: { borderColor: '#f1f1f1' },
  }

  const designationChartSeries = [{
    name: 'Staff',
    data: hrData?.by_designation?.map(d => d.count) || [],
  }]

  const quickActions = [
    { label: 'Manage Staff', route: '/staff', icon: <PeopleIcon />, color: lagosRed, bgColor: '#FFF5F5' },
    { label: 'HR Module', route: '/hr', icon: <WorkIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'View Reports', route: '/reports', icon: <AssignmentIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
  ]

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                HR Dashboard
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'HR Manager'} — Staff Management Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`${hrData?.total_staff || 0} Staff Members`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                <Chip label={`${hrData?.pending_leaves || 0} Pending Leaves`} size="small" sx={{ bgcolor: '#E65100', color: 'white', fontSize: '0.7rem' }} />
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

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpiCards.map((card, index) => (
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
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Staff by Category
            </Typography>
            {categoryChartSeries.length > 0 ? (
              <Chart options={categoryChartOptions} series={categoryChartSeries} type="donut" height={250} />
            ) : (
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Staff by Designation
            </Typography>
            {designationChartSeries[0]?.data?.length > 0 ? (
              <Chart options={designationChartOptions} series={designationChartSeries} type="bar" height={250} />
            ) : (
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row: Recent Leaves + Quick Actions */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                Recent Leave Requests
              </Typography>
              <Typography variant="caption" sx={{ color: lagosRed, cursor: 'pointer', fontWeight: 500 }} onClick={() => navigate('/hr')}>
                View All →
              </Typography>
            </Box>
            {hrData?.recent_leaves?.length > 0 ? (
              <List dense disablePadding>
                {hrData.recent_leaves.map((leave, idx) => (
                  <ListItem key={idx} sx={{ py: 1, px: 1.5, mb: 0.5, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '50%',
                        bgcolor: leave.status === 'APPROVED' ? '#E8F5E9' : leave.status === 'REJECTED' ? '#FFEBEE' : '#FFF3E0',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem',
                      }}>
                        {leave.status === 'APPROVED' ? '✅' : leave.status === 'REJECTED' ? '❌' : '⏳'}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {leave.staff__first_name} {leave.staff__last_name} — {leave.leave_type?.replace('_', ' ')}
                      </Typography>}
                      secondary={<Chip label={leave.status} size="small" sx={{
                        fontSize: '0.65rem', height: 20,
                        bgcolor: leave.status === 'APPROVED' ? '#E8F5E9' : leave.status === 'REJECTED' ? '#FFEBEE' : '#FFF3E0',
                        color: leave.status === 'APPROVED' ? '#2E7D32' : leave.status === 'REJECTED' ? '#C62828' : '#E65100',
                      }} />}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Typography color="text.secondary" variant="body2">No recent leave requests.</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {quickActions.map((action, idx) => (
                <Box key={idx} onClick={() => navigate(action.route)} sx={{
                  display: 'flex', alignItems: 'center', gap: 1, p: 1.2,
                  bgcolor: action.bgColor, borderRadius: 1, cursor: 'pointer',
                  border: `1px solid ${action.color}20`, transition: 'all 0.2s',
                  '&:hover': { bgcolor: `${action.color}15`, borderColor: `${action.color}40` },
                }}>
                  <Box sx={{ color: action.color }}>{action.icon}</Box>
                  <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>{action.label}</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default HRDashboard
