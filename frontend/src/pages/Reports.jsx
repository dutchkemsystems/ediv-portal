import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
} from '@mui/material'
import {
  Assessment as ReportIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material'
import Loading from '../components/common/Loading'
import StatCard from '../components/common/StatCard'
import api from '../api/client'

function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await api.get('/reports/reports/')
      setReports(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (report, format) => {
    try {
      const response = await api.post(`/reports/reports/${report.id}/export/`, { format }, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${report.title}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error exporting report:', error)
    }
  }

  if (loading) {
    return <Loading message="Loading reports..." />
  }

  const reportTypes = [
    { type: 'ACADEMIC', label: 'Academic Reports', color: '#1a237e' },
    { type: 'FINANCIAL', label: 'Financial Reports', color: '#388e3c' },
    { type: 'ATTENDANCE', label: 'Attendance Reports', color: '#f57c00' },
    { type: 'STAFF', label: 'Staff Reports', color: '#d32f2f' },
    { type: 'ENROLLMENT', label: 'Enrollment Reports', color: '#9c27b0' },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Reports</Typography>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Reports"
            value={reports.length}
            icon={<ReportIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Scheduled"
            value={reports.filter(r => r.is_scheduled).length}
            icon={<ReportIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="This Month"
            value={reports.filter(r => {
              const date = new Date(r.created_at)
              const now = new Date()
              return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()
            }).length}
            icon={<ReportIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Report Types"
            value={reportTypes.length}
            icon={<ReportIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Report Types */}
      <Typography variant="h6" sx={{ mb: 2 }}>Report Categories</Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {reportTypes.map((type) => (
          <Grid item xs={12} sm={6} md={4} key={type.type}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ReportIcon sx={{ color: type.color, mr: 1 }} />
                  <Typography variant="h6">{type.label}</Typography>
                </Box>
                <Typography variant="h4" sx={{ color: type.color, mb: 1 }}>
                  {reports.filter(r => r.report_type === type.type).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available reports
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Available Reports */}
      <Typography variant="h6" sx={{ mb: 2 }}>Available Reports</Typography>
      <Grid container spacing={3}>
        {reports.map((report) => (
          <Grid item xs={12} sm={6} md={4} key={report.id}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ReportIcon sx={{ color: '#1a237e', mr: 1 }} />
                  <Typography variant="h6" noWrap>{report.title}</Typography>
                </Box>
                <Chip label={report.report_type} size="small" sx={{ mb: 1 }} />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {report.description || 'No description'}
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Created: {new Date(report.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" startIcon={<ViewIcon />}>
                  View
                </Button>
                <Button size="small" startIcon={<DownloadIcon />} onClick={() => handleExport(report, 'pdf')}>
                  PDF
                </Button>
                <Button size="small" onClick={() => handleExport(report, 'excel')}>
                  Excel
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default Reports
