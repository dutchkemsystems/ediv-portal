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
  Divider,
} from '@mui/material'
import {
  Person as PersonIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
  Chat as ChatIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
} from '@mui/icons-material'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function ParentDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [parentData, setParentData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/parent_dashboard/')
      setParentData(res.data)
    } catch (error) {
      notify.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleRefresh = () => { setRefreshing(true); fetchData() }

  const formatCurrency = (amount) => {
    if (!amount) return '₦0'
    return `₦${Number(amount).toLocaleString()}`
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  const children = parentData?.children || []
  const totalBalance = children.reduce((sum, c) => sum + (c.balance || 0), 0)

  const kpiCards = [
    {
      title: 'My Children',
      value: parentData?.total_children || 0,
      icon: <PersonIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/students',
      trend: 'Enrolled students',
      trendColor: '#666',
    },
    {
      title: 'Total Due',
      value: formatCurrency(children.reduce((sum, c) => sum + (c.total_due || 0), 0)),
      icon: <ReceiptIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/finance',
      trend: 'Across all children',
      trendColor: '#E65100',
    },
    {
      title: 'Total Paid',
      value: formatCurrency(children.reduce((sum, c) => sum + (c.total_paid || 0), 0)),
      icon: <MoneyIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/finance',
      trend: 'Confirmed payments',
      trendColor: lagosGreen,
    },
    {
      title: 'Balance',
      value: formatCurrency(totalBalance),
      icon: <MoneyIcon sx={{ fontSize: 36 }} />,
      color: totalBalance > 0 ? '#C62828' : lagosGreen,
      route: '/finance',
      trend: totalBalance > 0 ? 'Outstanding balance' : 'Fully paid',
      trendColor: totalBalance > 0 ? '#C62828' : lagosGreen,
    },
  ]

  const quickActions = [
    { label: 'Fee Payment', route: '/finance', icon: <MoneyIcon />, color: lagosGreen, bgColor: '#E8F5E9' },
    { label: 'Communication', route: '/communication', icon: <ChatIcon />, color: '#1565C0', bgColor: '#E3F2FD' },
    { label: 'Parent-Teacher', route: '/parent-teacher', icon: <SchoolIcon />, color: '#6A1B9A', bgColor: '#F3E5F5' },
  ]

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, #6A1B9A 0%, #4A148C 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>Parent Dashboard</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'Parent'} — Your Children's Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`${parentData?.total_children || 0} Children`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                {totalBalance > 0 && (
                  <Chip label={`Balance: ${formatCurrency(totalBalance)}`} size="small" sx={{ bgcolor: '#E65100', color: 'white', fontSize: '0.7rem' }} />
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
                      <Typography variant="h4" sx={{ color: card.color, fontWeight: 700, fontSize: '1.4rem' }}>
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

      {/* Children Cards */}
      {children.length > 0 && (
        <Paper sx={{ p: 2.5, mb: 3, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 2 }}>
            My Children
          </Typography>
          <Grid container spacing={2}>
            {children.map((child) => (
              <Grid item xs={12} sm={6} md={4} key={child.id}>
                <Card sx={{ height: '100%', '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.12)' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                      <Box sx={{
                        width: 44, height: 44, borderRadius: '50%',
                        bgcolor: '#E3F2FD', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: '#1565C0', fontWeight: 700, fontSize: '1rem',
                      }}>
                        {child.name?.split(' ').map(n => n[0]).join('').slice(0, 2)}
                      </Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>{child.name}</Typography>
                        <Typography variant="caption" color="text.secondary">{child.admission_number}</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1.5 }}>
                      <Chip label={child.school} size="small" color="primary" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                      <Chip label={child.class_name} size="small" sx={{ bgcolor: '#E8F5E9', fontSize: '0.7rem' }} />
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">Total Due</Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>{formatCurrency(child.total_due)}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">Paid</Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600, color: lagosGreen }}>{formatCurrency(child.total_paid)}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">Balance</Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600, color: child.balance > 0 ? '#C62828' : lagosGreen }}>
                        {formatCurrency(child.balance)}
                      </Typography>
                    </Box>
                    {child.recent_payments?.length > 0 && (
                      <Box sx={{ mt: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>Recent Payments</Typography>
                        {child.recent_payments.slice(0, 2).map((p, idx) => (
                          <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#666' }}>
                            <span>{p.payment_method?.replace('_', ' ')}</span>
                            <span>{formatCurrency(p.amount)}</span>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Quick Actions */}
      <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1.5 }}>
          Quick Actions
        </Typography>
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

export default ParentDashboard
