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
  Gavel as GavelIcon,
  CheckCircle as CheckCircleIcon,
  PendingActions as PendingIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Discipline() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [formData, setFormData] = useState({
    student: '',
    incident_type: '',
    description: '',
    date: '',
    severity: '',
    action_taken: '',
    reported_by: '',
    status: '',
  })

  useEffect(() => {
    fetchIncidents()
    fetchStats()
  }, [])

  const fetchIncidents = async () => {
    try {
      const response = await api.get('/discipline/incidents/')
      setIncidents(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching incidents:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/discipline/incidents/')
      const data = response.data.results || response.data
      const now = new Date()
      const thisMonth = data.filter((i) => {
        const d = new Date(i.date)
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
      })
      setStats({
        total: data.length,
        this_month: thisMonth.length,
        resolved: data.filter((i) => i.status === 'RESOLVED').length,
        pending: data.filter((i) => i.status === 'PENDING').length,
      })
    } catch (error) {
      console.error('Error fetching discipline stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedIncident(null)
    setFormData({
      student: '',
      incident_type: '',
      description: '',
      date: '',
      severity: '',
      action_taken: '',
      reported_by: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (incident) => {
    setSelectedIncident(incident)
    setFormData({
      student: incident.student || '',
      incident_type: incident.incident_type || '',
      description: incident.description || '',
      date: incident.date || '',
      severity: incident.severity || '',
      action_taken: incident.action_taken || '',
      reported_by: incident.reported_by || '',
      status: incident.status || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (incident) => {
    setSelectedIncident(incident)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedIncident) {
        await api.put(`/discipline/incidents/${selectedIncident.id}/`, formData)
      } else {
        await api.post('/discipline/incidents/', formData)
      }
      setOpenDialog(false)
      fetchIncidents()
      fetchStats()
    } catch (error) {
      console.error('Error saving incident:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/discipline/incidents/${selectedIncident.id}/`)
      setOpenDeleteDialog(false)
      fetchIncidents()
      fetchStats()
    } catch (error) {
      console.error('Error deleting incident:', error)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'error'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'info'
      case 'LOW': return 'success'
      default: return 'default'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'RESOLVED': return 'success'
      case 'PENDING': return 'warning'
      case 'INVESTIGATING': return 'info'
      case 'ESCALATED': return 'error'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'student', label: 'Student' },
    { id: 'incident_type', label: 'Incident Type' },
    { id: 'description', label: 'Description', render: (row) => (
      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
        {row.description}
      </Typography>
    )},
    { id: 'date', label: 'Date' },
    { id: 'severity', label: 'Severity', render: (row) => (
      <Chip label={row.severity} size="small" color={getSeverityColor(row.severity)} />
    )},
    { id: 'action_taken', label: 'Action Taken' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading disciplinary records..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Discipline Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Report Incident
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Incidents"
            value={stats?.total ?? incidents.length}
            icon={<GavelIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="This Month"
            value={stats?.this_month ?? 0}
            icon={<WarningIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resolved"
            value={stats?.resolved ?? incidents.filter((i) => i.status === 'RESOLVED').length}
            icon={<CheckCircleIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending"
            value={stats?.pending ?? incidents.filter((i) => i.status === 'PENDING').length}
            icon={<PendingIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={incidents}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(incident) => console.log('View:', incident)}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedIncident ? 'Edit Incident' : 'Report New Incident'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Student"
                value={formData.student}
                onChange={(e) => setFormData({ ...formData, student: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Incident Type</InputLabel>
                <Select
                  value={formData.incident_type}
                  onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                  label="Incident Type"
                >
                  <MenuItem value="BULLYING">Bullying</MenuItem>
                  <MenuItem value="VANDALISM">Vandalism</MenuItem>
                  <MenuItem value="THEFT">Theft</MenuItem>
                  <MenuItem value="FIGHTING">Fighting</MenuItem>
                  <MenuItem value="CHEATING">Cheating</MenuItem>
                  <MenuItem value="TARDINESS">Tardiness</MenuItem>
                  <MenuItem value="DISRESPECT">Disrespect</MenuItem>
                  <MenuItem value="SUBSTANCE_ABUSE">Substance Abuse</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  label="Severity"
                >
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="MEDIUM">Medium</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="CRITICAL">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Action Taken"
                value={formData.action_taken}
                onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Reported By"
                value={formData.reported_by}
                onChange={(e) => setFormData({ ...formData, reported_by: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="PENDING">Pending</MenuItem>
                  <MenuItem value="INVESTIGATING">Investigating</MenuItem>
                  <MenuItem value="RESOLVED">Resolved</MenuItem>
                  <MenuItem value="ESCALATED">Escalated</MenuItem>
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
            {selectedIncident ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Incident"
        message={`Are you sure you want to delete this incident record for "${selectedIncident?.student}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Discipline
