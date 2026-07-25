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
  Description as FileIcon,
  SwapHoriz as WorkflowIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function RegistryDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [registryData, setRegistryData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/registry_dashboard/')
      setRegistryData(res.data)
    } catch (error) {
      notify.error('Failed to load registry dashboard data')
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
      title: 'Total Files',
      value: registryData?.total_files || 0,
      icon: <FileIcon sx={{ fontSize: 36 }} />,
      color: lagosRed,
      route: '/registry',
      trend: `${registryData?.active_files || 0} active`,
      trendColor: lagosGreen,
    },
    {
      title: 'Active Files',
      value: registryData?.active_files || 0,
      icon: <CheckIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/registry',
      trend: 'Currently in use',
      trendColor: '#666',
    },
    {
      title: 'Pending Files',
      value: registryData?.pending_files || 0,
      icon: <WarningIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/registry',
      trend: 'Awaiting action',
      trendColor: '#E65100',
    },
    {
      title: 'Active Workflows',
      value: registryData?.active_workflows || 0,
      icon: <WorkflowIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/workflows',
      trend: `${registryData?.overdue_tasks || 0} overdue`,
      trendColor: registryData?.overdue_tasks > 0 ? '#C62828' : lagosGreen,
    },
  ]

  const fileStatusChartOptions = {
    chart: { type: 'donut', fontFamily: 'inherit' },
    colors: [lagosGreen, '#E65100', '#1565C0', '#757575'],
    labels: registryData?.files_by_status?.map(s => s.status || 'Other') || [],
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

  const fileStatusChartSeries = registryData?.files_by_status?.map(s => s.count) || []

  const quickActions = [
    { label: 'Registry', route: '/registry', icon: <FileIcon />, color: lagosRed, bgColor: '#FFF5F5' },
    { label: 'Files', route: '/files', icon: <AssignmentIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'Workflows', route: '/workflows', icon: <WorkflowIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
  ]

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, #E65100 0%, #BF360C 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>Registry Dashboard</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'Registry Officer'} — File & Workflow Management
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`${registryData?.total_files || 0} Total Files`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                <Chip label={`${registryData?.pending_files || 0} Pending`} size="small" sx={{ bgcolor: '#E65100', color: 'white', fontSize: '0.7rem' }} />
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

      {/* Charts + Activity Row */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Files by Status
            </Typography>
            {fileStatusChartSeries.length > 0 ? (
              <Chart options={fileStatusChartOptions} series={fileStatusChartSeries} type="donut" height={250} />
            ) : (
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                Recent File Movements
              </Typography>
              <Typography variant="caption" sx={{ color: lagosRed, cursor: 'pointer', fontWeight: 500 }} onClick={() => navigate('/registry')}>
                View All →
              </Typography>
            </Box>
            {registryData?.recent_movements?.length > 0 ? (
              <List dense disablePadding>
                {registryData.recent_movements.slice(0, 5).map((movement, idx) => (
                  <ListItem key={idx} sx={{ py: 1, px: 1.5, mb: 0.5, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Box sx={{
                        width: 32, height: 32, borderRadius: '50%',
                        bgcolor: '#E3F2FD', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem',
                      }}>📄</Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>
                        {movement.file__title || movement.file__file_number || 'File'} — {movement.action}
                      </Typography>}
                      secondary={<Typography variant="caption" color="text.secondary">
                        {movement.from_holder__first_name || ''} → {movement.to_holder__first_name || ''}
                      </Typography>}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Typography color="text.secondary" variant="body2">No recent file movements.</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 2.5, mt: 2, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>Quick Actions</Typography>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
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
    </Box>
  )
}

export default RegistryDashboard
