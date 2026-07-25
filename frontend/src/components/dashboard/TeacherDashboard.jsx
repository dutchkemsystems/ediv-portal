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
} from '@mui/material'
import {
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  CalendarToday as CalendarIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  CheckCircle as CheckIcon,
  Cancel as AbsentIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function TeacherDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [teacherData, setTeacherData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/teacher_dashboard/')
      setTeacherData(res.data)
    } catch (error) {
      notify.error('Failed to load dashboard data')
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
      title: 'My Students',
      value: (teacherData?.total_students || 0).toLocaleString(),
      icon: <PersonIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/students',
      trend: 'Active students',
      trendColor: '#666',
    },
    {
      title: 'Present Today',
      value: teacherData?.present_today || 0,
      icon: <CheckIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/attendance',
      trend: `${teacherData?.attendance_rate || 0}% attendance`,
      trendColor: lagosGreen,
    },
    {
      title: 'Absent Today',
      value: teacherData?.absent_today || 0,
      icon: <AbsentIcon sx={{ fontSize: 36 }} />,
      color: '#C62828',
      route: '/attendance',
      trend: 'Require follow-up',
      trendColor: '#C62828',
    },
    {
      title: 'Staff Present',
      value: `${teacherData?.staff_present_today || 0}/${teacherData?.total_school_staff || 0}`,
      icon: <PeopleIcon sx={{ fontSize: 36 }} />,
      color: '#00695C',
      route: '/staff',
      trend: 'Today',
      trendColor: '#666',
    },
  ]

  const attendanceTrendOptions = {
    chart: { type: 'area', toolbar: { show: false }, fontFamily: 'inherit' },
    colors: [lagosGreen, '#C62828'],
    dataLabels: { enabled: false },
    xaxis: {
      categories: teacherData?.attendance_trend?.map(t => {
        const d = new Date(t.date)
        return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
      }) || [],
      labels: { style: { fontSize: '10px' } },
    },
    yaxis: { labels: { style: { fontSize: '12px' } } },
    grid: { borderColor: '#f1f1f1' },
    stroke: { curve: 'smooth', width: 2 },
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.1 } },
  }

  const attendanceTrendSeries = [
    {
      name: 'Present',
      data: teacherData?.attendance_trend?.map(t => t.present) || [],
    },
    {
      name: 'Absent',
      data: teacherData?.attendance_trend?.map(t => t.absent) || [],
    },
  ]

  const quickActions = [
    { label: 'Take Attendance', route: '/attendance', icon: <CalendarIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
    { label: 'Academics', route: '/academics', icon: <SchoolIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'E-Learning', route: '/e-learning', icon: <TrendingUpIcon />, color: '#6A1B9A', bgColor: '#F3E5F5' },
    { label: 'Timetable', route: '/timetable', icon: <CalendarIcon />, color: '#E65100', bgColor: '#FFF3E0' },
  ]

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>Teacher Dashboard</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'Teacher'} — Today's Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`${teacherData?.total_students || 0} Students`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                <Chip label={`${teacherData?.attendance_rate || 0}% Attendance`} size="small" sx={{ bgcolor: lagosGreen, color: 'white', fontSize: '0.7rem' }} />
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

      {/* Attendance Trend */}
      <Paper sx={{ p: 2.5, mb: 3, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
          Attendance Trend (7 Days)
        </Typography>
        {attendanceTrendSeries[0]?.data?.length > 0 ? (
          <Chart options={attendanceTrendOptions} series={attendanceTrendSeries} type="area" height={250} />
        ) : (
          <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">No attendance data available</Typography>
          </Box>
        )}
      </Paper>

      {/* Quick Actions */}
      <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={1.5}>
          {quickActions.map((action, idx) => (
            <Grid item xs={6} sm={3} key={idx}>
              <Box onClick={() => navigate(action.route)} sx={{
                display: 'flex', alignItems: 'center', gap: 1, p: 1.5,
                bgcolor: action.bgColor, borderRadius: 1, cursor: 'pointer',
                border: `1px solid ${action.color}20`, transition: 'all 0.2s',
                '&:hover': { bgcolor: `${action.color}15`, borderColor: `${action.color}40`, transform: 'translateY(-2px)' },
              }}>
                <Box sx={{ color: action.color }}>{action.icon}</Box>
                <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem' }}>{action.label}</Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  )
}

export default TeacherDashboard
