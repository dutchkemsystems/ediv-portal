import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Notifications as NotificationsIcon,
  Email as EmailIcon,
  Sms as SmsIcon,
  NotificationsActive as NotificationsActiveIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Notifications() {
  const [templates, setTemplates] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    title: '',
    message: '',
    notification_type: '',
    channel: '',
  })

  useEffect(() => {
    fetchTemplates()
    fetchLogs()
    fetchStats()
  }, [])

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/notifications/templates/')
      setTemplates(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchLogs = async () => {
    try {
      const response = await api.get('/notifications/logs/')
      setLogs(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching logs:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/analytics/stats/notification_stats/')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedTemplate(null)
    setFormData({
      name: '',
      title: '',
      message: '',
      notification_type: '',
      channel: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (template) => {
    setSelectedTemplate(template)
    setFormData({
      name: template.name,
      title: template.title,
      message: template.message,
      notification_type: template.notification_type,
      channel: template.channel,
    })
    setOpenDialog(true)
  }

  const handleDelete = (template) => {
    setSelectedTemplate(template)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedTemplate) {
        await api.put(`/notifications/templates/${selectedTemplate.id}/`, formData)
      } else {
        await api.post('/notifications/templates/', formData)
      }
      setOpenDialog(false)
      fetchTemplates()
    } catch (error) {
      console.error('Error saving template:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/notifications/templates/${selectedTemplate.id}/`)
      setOpenDeleteDialog(false)
      fetchTemplates()
    } catch (error) {
      console.error('Error deleting template:', error)
    }
  }

  const getTypeColor = (type) => {
    const colors = {
      INFO: 'info',
      WARNING: 'warning',
      ERROR: 'error',
      SUCCESS: 'success',
    }
    return colors[type] || 'default'
  }

  const getChannelIcon = (channel) => {
    const icons = {
      EMAIL: <EmailIcon fontSize="small" />,
      SMS: <SmsIcon fontSize="small" />,
      IN_APP: <NotificationsActiveIcon fontSize="small" />,
    }
    return icons[channel] || <NotificationsIcon fontSize="small" />
  }

  const templateColumns = [
    { id: 'name', label: 'Template Name' },
    { id: 'title', label: 'Title' },
    { id: 'notification_type', label: 'Type', render: (row) => (
      <Chip label={row.notification_type} size="small" color={getTypeColor(row.notification_type)} />
    )},
    { id: 'channel', label: 'Channel', render: (row) => (
      <Chip
        icon={getChannelIcon(row.channel)}
        label={row.channel}
        size="small"
        variant="outlined"
      />
    )},
    { id: 'created_at', label: 'Created', render: (row) => (
      <Typography variant="body2" color="text.secondary">
        {new Date(row.created_at).toLocaleDateString()}
      </Typography>
    )},
  ]

  const logColumns = [
    { id: 'title', label: 'Title' },
    { id: 'message', label: 'Message', render: (row) => (
      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
        {row.message}
      </Typography>
    )},
    { id: 'notification_type', label: 'Type', render: (row) => (
      <Chip label={row.notification_type} size="small" color={getTypeColor(row.notification_type)} />
    )},
    { id: 'channel', label: 'Channel', render: (row) => (
      <Chip
        icon={getChannelIcon(row.channel)}
        label={row.channel}
        size="small"
        variant="outlined"
      />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={row.status === 'SENT' ? 'success' : row.status === 'FAILED' ? 'error' : 'warning'}
      />
    )},
    { id: 'sent_at', label: 'Sent At', render: (row) => (
      <Typography variant="body2" color="text.secondary">
        {row.sent_at ? new Date(row.sent_at).toLocaleString() : '-'}
      </Typography>
    )},
  ]

  if (loading) {
    return <Loading message="Loading notifications..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Notifications Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Template
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Templates"
            value={templates.length}
            icon={<NotificationsIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Sent Today"
            value={logs.filter(l => l.sent_at && new Date(l.sent_at).toDateString() === new Date().toDateString() && l.status === 'SENT').length}
            icon={<EmailIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Failed"
            value={logs.filter(l => l.status === 'FAILED').length}
            icon={<NotificationsIcon />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Channels Active"
            value={[...new Set(templates.map(t => t.channel))].length}
            icon={<SmsIcon />}
            color="#f57c00"
          />
        </Grid>
      </Grid>

      {/* Templates Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Notification Templates</Typography>
          <DataTable
            columns={templateColumns}
            data={templates}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onView={(template) => console.log('View:', template)}
          />
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Notification Logs</Typography>
          <DataTable
            columns={logColumns}
            data={logs}
            onView={(log) => console.log('View:', log)}
          />
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedTemplate ? 'Edit Template' : 'Add New Template'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Template Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message"
                multiline
                rows={4}
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Notification Type</InputLabel>
                <Select
                  value={formData.notification_type}
                  onChange={(e) => setFormData({ ...formData, notification_type: e.target.value })}
                  label="Notification Type"
                >
                  <MenuItem value="INFO">Info</MenuItem>
                  <MenuItem value="WARNING">Warning</MenuItem>
                  <MenuItem value="ERROR">Error</MenuItem>
                  <MenuItem value="SUCCESS">Success</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Channel</InputLabel>
                <Select
                  value={formData.channel}
                  onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                  label="Channel"
                >
                  <MenuItem value="EMAIL">Email</MenuItem>
                  <MenuItem value="SMS">SMS</MenuItem>
                  <MenuItem value="IN_APP">In-App</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {selectedTemplate ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Template"
        message={`Are you sure you want to delete ${selectedTemplate?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Notifications
