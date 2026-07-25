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
  LinearProgress,
} from '@mui/material'
import {
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
} from '@mui/icons-material'
import Chart from 'react-apexcharts'
import api from '../../api/client'
import { notify } from '../../utils/notifications'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'

function FinanceDashboard() {
  const { user } = useSelector((state) => state.auth)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [financeData, setFinanceData] = useState(null)

  const fetchData = async () => {
    try {
      const res = await api.get('/analytics/stats/finance_dashboard/')
      setFinanceData(res.data)
    } catch (error) {
      notify.error('Failed to load finance dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleRefresh = () => { setRefreshing(true); fetchData() }

  const formatCurrency = (amount) => {
    if (!amount) return '₦0'
    if (amount >= 1000000) return `₦${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `₦${(amount / 1000).toFixed(1)}K`
    return `₦${Number(amount).toLocaleString()}`
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  const kpiCards = [
    {
      title: 'Total Collected',
      value: formatCurrency(financeData?.total_collected),
      icon: <MoneyIcon sx={{ fontSize: 36 }} />,
      color: lagosGreen,
      route: '/finance',
      trend: `${financeData?.collection_rate || 0}% collection rate`,
      trendColor: lagosGreen,
    },
    {
      title: 'Outstanding',
      value: formatCurrency(financeData?.total_due),
      icon: <ReceiptIcon sx={{ fontSize: 36 }} />,
      color: '#E65100',
      route: '/finance',
      trend: 'Pending collection',
      trendColor: '#E65100',
    },
    {
      title: 'Payments Today',
      value: formatCurrency(financeData?.payments_today),
      icon: <PaymentIcon sx={{ fontSize: 36 }} />,
      color: '#1565C0',
      route: '/finance',
      trend: `${financeData?.pending_payments || 0} unconfirmed`,
      trendColor: '#F57C00',
    },
    {
      title: 'Collection Rate',
      value: `${financeData?.collection_rate || 0}%`,
      icon: <TrendingUpIcon sx={{ fontSize: 36 }} />,
      color: '#00695C',
      route: '/finance',
      trend: 'Overall performance',
      trendColor: lagosGreen,
    },
  ]

  const collectionBySchoolChartOptions = {
    chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%', horizontal: true } },
    colors: [lagosGreen],
    dataLabels: { enabled: false },
    xaxis: {
      categories: financeData?.collection_by_school?.map(s => s.student_fee__fee_structure__school__name || 'Unknown') || [],
      labels: { style: { fontSize: '11px' } },
    },
    yaxis: { labels: { style: { fontSize: '11px' } } },
    grid: { borderColor: '#f1f1f1' },
    tooltip: { y: { formatter: (val) => formatCurrency(val) } },
  }

  const collectionBySchoolSeries = [{
    name: 'Collected',
    data: financeData?.collection_by_school?.map(s => s.total) || [],
  }]

  const collectionByMethodChartOptions = {
    chart: { type: 'donut', fontFamily: 'inherit' },
    colors: [lagosRed, '#1565C0', lagosGreen, '#E65100', '#6A1B9A'],
    labels: financeData?.collection_by_method?.map(m => m.payment_method?.replace('_', ' ') || 'Other') || [],
    dataLabels: { enabled: false },
    legend: { position: 'bottom', fontSize: '11px' },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            value: { show: true, fontSize: '14px', fontWeight: 700, formatter: (val) => formatCurrency(parseInt(val)) },
          },
        },
      },
    },
  }

  const collectionByMethodSeries = financeData?.collection_by_method?.map(m => m.total) || []

  return (
    <Box>
      {/* Welcome Banner */}
      <Card sx={{ mb: 3, background: `linear-gradient(135deg, #00843D 0%, #005A2B 100%)`, color: 'white' }}>
        <CardContent sx={{ py: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>Finance Dashboard</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                Welcome, {user?.first_name || 'Finance Manager'} — Financial Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                <Chip label={`Collection: ${financeData?.collection_rate || 0}%`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }} />
                <Chip label={`${financeData?.pending_payments || 0} pending`} size="small" sx={{ bgcolor: '#E65100', color: 'white', fontSize: '0.7rem' }} />
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

      {/* Collection Rate Bar */}
      <Paper sx={{ p: 2.5, mb: 3, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Collection Progress</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600, color: lagosGreen }}>{financeData?.collection_rate || 0}%</Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={financeData?.collection_rate || 0}
          sx={{ height: 10, borderRadius: 5, bgcolor: '#f0f0f0', '& .MuiLinearProgress-bar': { borderRadius: 5, bgcolor: lagosGreen } }}
        />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="caption" color="text.secondary">Collected: {formatCurrency(financeData?.total_collected)}</Typography>
          <Typography variant="caption" color="text.secondary">Outstanding: {formatCurrency(financeData?.total_due)}</Typography>
        </Box>
      </Paper>

      {/* Charts Row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Collection by School
            </Typography>
            {collectionBySchoolSeries[0]?.data?.length > 0 ? (
              <Chart options={collectionBySchoolChartOptions} series={collectionBySchoolSeries} type="bar" height={250} />
            ) : (
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2.5, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 1 }}>
              Collection by Method
            </Typography>
            {collectionByMethodSeries.length > 0 ? (
              <Chart options={collectionByMethodChartOptions} series={collectionByMethodSeries} type="donut" height={250} />
            ) : (
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">No data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Budget Summary */}
      {financeData?.budget_summary?.length > 0 && (
        <Paper sx={{ p: 2.5, mb: 3, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 2 }}>
            Budget Utilization
          </Typography>
          <Grid container spacing={2}>
            {financeData.budget_summary.map((budget, idx) => {
              const utilization = budget.allocated > 0 ? (budget.spent / budget.allocated * 100) : 0
              return (
                <Grid item xs={12} sm={6} md={4} key={idx}>
                  <Box sx={{ p: 1.5, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.8rem', mb: 0.5 }}>
                      {budget.category?.replace('_', ' ')}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(utilization, 100)}
                      sx={{ height: 6, borderRadius: 3, mb: 0.5, bgcolor: '#e0e0e0', '& .MuiLinearProgress-bar': { borderRadius: 3, bgcolor: utilization > 90 ? '#C62828' : utilization > 70 ? '#E65100' : lagosGreen } }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">{formatCurrency(budget.spent)}</Typography>
                      <Typography variant="caption" color="text.secondary">{formatCurrency(budget.allocated)}</Typography>
                    </Box>
                  </Box>
                </Grid>
              )
            })}
          </Grid>
        </Paper>
      )}
    </Box>
  )
}

export default FinanceDashboard
