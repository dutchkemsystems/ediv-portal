import React, { useState, useEffect } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import api from '../../api/client'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const CHART_COLORS = [
  '#1a237e', '#f57c00', '#388e3c', '#d32f2f',
  '#7b1fa2', '#0097a7', '#ff8f00', '#558b2f',
  '#00695c', '#ad1457', '#283593', '#e65100',
]

function DashboardCharts() {
  const [enrollmentData, setEnrollmentData] = useState(null)
  const [attendanceData, setAttendanceData] = useState(null)
  const [financialData, setFinancialData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCharts = async () => {
      try {
        const [enrollmentRes, attendanceRes, financialRes] = await Promise.all([
          api.get('/analytics/stats/enrollment_stats/'),
          api.get('/analytics/stats/attendance_stats/'),
          api.get('/analytics/stats/financial_stats/'),
        ])
        setEnrollmentData(enrollmentRes.data)
        setAttendanceData(attendanceRes.data)
        setFinancialData(financialRes.data)
      } catch (error) {
        console.error('Error fetching chart data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchCharts()
  }, [])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const enrollmentChartData = enrollmentData?.length ? {
    labels: enrollmentData.map((item) => item.school__name),
    datasets: [
      {
        label: 'Enrolled Students',
        data: enrollmentData.map((item) => item.count),
        backgroundColor: CHART_COLORS.slice(0, enrollmentData.length),
        borderColor: CHART_COLORS.slice(0, enrollmentData.length).map((c) => c + 'cc'),
        borderWidth: 1,
      },
    ],
  } : null

  const attendanceChartData = attendanceData?.length ? {
    labels: attendanceData.map((item) => item.status),
    datasets: [
      {
        label: 'Attendance Records',
        data: attendanceData.map((item) => item.count),
        backgroundColor: ['#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'],
        borderColor: ['#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'],
        borderWidth: 1,
      },
    ],
  } : null

  const financialChartData = financialData ? {
    labels: ['Amount Collected', 'Outstanding Dues'],
    datasets: [
      {
        label: 'Amount (NGN)',
        data: [financialData.total_collected, financialData.total_due],
        backgroundColor: ['#388e3c', '#d32f2f'],
        borderColor: ['#388e3c', '#d32f2f'],
        borderWidth: 1,
      },
    ],
  } : null

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  }

  const barOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  }

  return (
    <Grid container spacing={3} sx={{ mt: 3 }}>
      {enrollmentChartData && (
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Enrollment by School
            </Typography>
            <Box sx={{ height: 350, position: 'relative' }}>
              <Bar data={enrollmentChartData} options={barOptions} />
            </Box>
          </Paper>
        </Grid>
      )}
      {attendanceChartData && (
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Attendance Overview (Last 7 Days)
            </Typography>
            <Box sx={{ height: 350, display: 'flex', justifyContent: 'center' }}>
              <Doughnut data={attendanceChartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
      )}
      {financialChartData && (
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Financial Summary
            </Typography>
            <Box sx={{ height: 300, position: 'relative' }}>
              <Bar data={financialChartData} options={{
                ...barOptions,
                plugins: {
                  ...barOptions.plugins,
                  legend: { display: false },
                },
              }} />
            </Box>
            {financialData && (
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Collection Rate: {financialData.collection_rate?.toFixed(1) || 0}%
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      )}
    </Grid>
  )
}

export default DashboardCharts
