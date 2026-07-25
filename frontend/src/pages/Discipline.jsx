import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Paper,
  Stack,
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Gavel as GavelIcon,
  CheckCircle as CheckCircleIcon,
  PendingActions as PendingIcon,
  Warning as WarningIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

const emptyForm = {
  student: '',
  title: '',
  incident_type: '',
  severity: '',
  description: '',
  incident_date: '',
  incident_time: '',
  location: '',
  witnesses: '',
  status: 'REPORTED',
  action_taken: '',
  follow_up_required: false,
  follow_up_date: '',
  follow_up_notes: '',
}

function Discipline() {
  const [incidents, setIncidents] = useState([])
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [filters, setFilters] = useState({ severity: '', status: '', incident_type: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchIncidents()
    fetchStudents()
  }, [])

  useEffect(() => {
    fetchIncidents()
  }, [filters])

  const fetchIncidents = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.severity) params.append('severity', filters.severity)
      if (filters.status) params.append('status', filters.status)
      if (filters.incident_type) params.append('incident_type', filters.incident_type)
      const query = params.toString()
      const response = await api.get(`/discipline/incidents/${query ? `?${query}` : ''}`)
      setIncidents(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async () => {
    try {
      const response = await api.get('/students/students/')
      setStudents(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => setFilters({ severity: '', status: '', incident_type: '' })
  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData(emptyForm)
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      student: item.student || '',
      title: item.title || '',
      incident_type: item.incident_type || '',
      severity: item.severity || '',
      description: item.description || '',
      incident_date: item.incident_date || '',
      incident_time: item.incident_time || '',
      location: item.location || '',
      witnesses: item.witnesses || '',
      status: item.status || 'REPORTED',
      action_taken: item.action_taken || '',
      follow_up_required: item.follow_up_required || false,
      follow_up_date: item.follow_up_date || '',
      follow_up_notes: item.follow_up_notes || '',
    })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.student) errors.student = 'Student is required'
    if (!formData.title.trim()) errors.title = 'Title is required'
    if (!formData.incident_type) errors.incident_type = 'Incident type is required'
    if (!formData.severity) errors.severity = 'Severity is required'
    if (!formData.description.trim()) errors.description = 'Description is required'
    if (!formData.incident_date) errors.incident_date = 'Date is required'
    if (!formData.status) errors.status = 'Status is required'
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      notify.warning('Please fill in all required fields')
      return
    }
    setSubmitting(true)
    try {
      if (selectedItem) {
        await api.put(`/discipline/incidents/${selectedItem.id}/`, formData)
        notify.success('Incident updated')
      } else {
        await api.post('/discipline/incidents/', formData)
        notify.success('Incident created')
      }
      setOpenFormDialog(false)
      setSelectedItem(null)
      fetchIncidents()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save incident'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        if (firstKey) { const val = data[firstKey]; msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}` }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/discipline/incidents/${selectedItem.id}/`)
      notify.success('Incident deleted')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      fetchIncidents()
    } catch (error) {
      notify.error('Failed to delete')
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'SEVERE': return 'error'
      case 'SERIOUS': return 'warning'
      case 'MODERATE': return 'info'
      case 'MINOR': return 'success'
      default: return 'default'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'RESOLVED': return 'success'
      case 'REPORTED': return 'warning'
      case 'INVESTIGATING': return 'info'
      case 'ESCALATED': return 'error'
      default: return 'default'
    }
  }

  const columns = [
    {
      id: 'student_name',
      label: 'Student',
      render: (row) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.student_name || '-'}</Typography>
      ),
    },
    { id: 'title', label: 'Title' },
    { id: 'incident_type', label: 'Type', render: (row) => (
      <Chip label={row.incident_type?.replace('_', ' ')} size="small" />
    )},
    { id: 'incident_date', label: 'Date' },
    { id: 'severity', label: 'Severity', render: (row) => (
      <Chip label={row.severity} size="small" color={getSeverityColor(row.severity)} />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
  ]

  if (loading) return <Loading message="Loading disciplinary records..." />

  const totalIncidents = incidents.length
  const thisMonth = incidents.filter(i => {
    const d = new Date(i.incident_date)
    const now = new Date()
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
  const resolvedCount = incidents.filter(i => i.status === 'RESOLVED').length
  const reportedCount = incidents.filter(i => i.status === 'REPORTED').length

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Discipline Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {totalIncidents} incident{totalIncidents !== 1 ? 's' : ''}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters {hasActiveFilters ? `(${Object.values(filters).filter(v => v).length})` : ''}
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            Report Incident
          </Button>
        </Stack>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Incidents</Typography>
            {hasActiveFilters && <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Severity</InputLabel>
                <Select value={filters.severity} onChange={(e) => handleFilterChange('severity', e.target.value)} label="Severity">
                  <MenuItem value="">All Severities</MenuItem>
                  <MenuItem value="MINOR">Minor</MenuItem>
                  <MenuItem value="MODERATE">Moderate</MenuItem>
                  <MenuItem value="SERIOUS">Serious</MenuItem>
                  <MenuItem value="SEVERE">Severe</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="REPORTED">Reported</MenuItem>
                  <MenuItem value="INVESTIGATING">Investigating</MenuItem>
                  <MenuItem value="RESOLVED">Resolved</MenuItem>
                  <MenuItem value="ESCALATED">Escalated</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Incident Type</InputLabel>
                <Select value={filters.incident_type} onChange={(e) => handleFilterChange('incident_type', e.target.value)} label="Incident Type">
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="LATE_COMING">Late Coming</MenuItem>
                  <MenuItem value="ABSENCE">Absence</MenuItem>
                  <MenuItem value="UNIFORM_VIOLATION">Uniform Violation</MenuItem>
                  <MenuItem value="DISRESPECT">Disrespect</MenuItem>
                  <MenuItem value="FIGHTING">Fighting</MenuItem>
                  <MenuItem value="BULLYING">Bullying</MenuItem>
                  <MenuItem value="CHEATING">Cheating</MenuItem>
                  <MenuItem value="VANDALISM">Vandalism</MenuItem>
                  <MenuItem value="THEFT">Theft</MenuItem>
                  <MenuItem value="SUBSTANCE_ABUSE">Substance Abuse</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Incidents" value={totalIncidents} icon={<GavelIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="This Month" value={thisMonth} icon={<WarningIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Resolved" value={resolvedCount} icon={<CheckCircleIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Reported" value={reportedCount} icon={<PendingIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable columns={columns} data={incidents} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{selectedItem ? 'Edit Incident' : 'Report New Incident'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.student}>
                <InputLabel>Student *</InputLabel>
                <Select value={formData.student} onChange={(e) => setFormData({ ...formData, student: e.target.value })} label="Student *">
                  {students.map(s => (
                    <MenuItem key={s.id} value={s.id}>{s.full_name || `${s.user?.first_name} ${s.user?.last_name}`} — {s.admission_number}</MenuItem>
                  ))}
                </Select>
                {formErrors.student && <Typography variant="caption" color="error">{formErrors.student}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Title"
                value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                error={!!formErrors.title} helperText={formErrors.title} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.incident_type}>
                <InputLabel>Incident Type *</InputLabel>
                <Select value={formData.incident_type} onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })} label="Incident Type *">
                  <MenuItem value="LATE_COMING">Late Coming</MenuItem>
                  <MenuItem value="ABSENCE">Absence</MenuItem>
                  <MenuItem value="UNIFORM_VIOLATION">Uniform Violation</MenuItem>
                  <MenuItem value="DISRESPECT">Disrespect</MenuItem>
                  <MenuItem value="FIGHTING">Fighting</MenuItem>
                  <MenuItem value="BULLYING">Bullying</MenuItem>
                  <MenuItem value="CHEATING">Cheating</MenuItem>
                  <MenuItem value="VANDALISM">Vandalism</MenuItem>
                  <MenuItem value="THEFT">Theft</MenuItem>
                  <MenuItem value="SUBSTANCE_ABUSE">Substance Abuse</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
                {formErrors.incident_type && <Typography variant="caption" color="error">{formErrors.incident_type}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.severity}>
                <InputLabel>Severity *</InputLabel>
                <Select value={formData.severity} onChange={(e) => setFormData({ ...formData, severity: e.target.value })} label="Severity *">
                  <MenuItem value="MINOR">Minor</MenuItem>
                  <MenuItem value="MODERATE">Moderate</MenuItem>
                  <MenuItem value="SERIOUS">Serious</MenuItem>
                  <MenuItem value="SEVERE">Severe</MenuItem>
                </Select>
                {formErrors.severity && <Typography variant="caption" color="error">{formErrors.severity}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth size="small" required label="Description" multiline rows={3}
                value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                error={!!formErrors.description} helperText={formErrors.description} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Incident Date" type="date" InputLabelProps={{ shrink: true }}
                value={formData.incident_date} onChange={(e) => setFormData({ ...formData, incident_date: e.target.value })}
                error={!!formErrors.incident_date} helperText={formErrors.incident_date} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" label="Incident Time" type="time" InputLabelProps={{ shrink: true }}
                value={formData.incident_time} onChange={(e) => setFormData({ ...formData, incident_time: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" label="Location"
                value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="e.g. Classroom, Playground, etc." />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.status}>
                <InputLabel>Status *</InputLabel>
                <Select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} label="Status *">
                  <MenuItem value="REPORTED">Reported</MenuItem>
                  <MenuItem value="INVESTIGATING">Investigating</MenuItem>
                  <MenuItem value="RESOLVED">Resolved</MenuItem>
                  <MenuItem value="ESCALATED">Escalated</MenuItem>
                </Select>
                {formErrors.status && <Typography variant="caption" color="error">{formErrors.status}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth size="small" label="Witnesses"
                value={formData.witnesses} onChange={(e) => setFormData({ ...formData, witnesses: e.target.value })}
                placeholder="Names of witnesses (if any)" />
            </Grid>
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Action & Follow-up</Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth size="small" label="Action Taken" multiline rows={2}
                value={formData.action_taken} onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={<Switch checked={formData.follow_up_required} onChange={(e) => setFormData({ ...formData, follow_up_required: e.target.checked })} />}
                label="Follow-up Required"
              />
            </Grid>
            {formData.follow_up_required && (
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Follow-up Date" type="date" InputLabelProps={{ shrink: true }}
                  value={formData.follow_up_date} onChange={(e) => setFormData({ ...formData, follow_up_date: e.target.value })} />
              </Grid>
            )}
            {formData.follow_up_required && (
              <Grid item xs={12}>
                <TextField fullWidth size="small" label="Follow-up Notes" multiline rows={2}
                  value={formData.follow_up_notes} onChange={(e) => setFormData({ ...formData, follow_up_notes: e.target.value })} />
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {submitting ? 'Saving...' : selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Incident Details
          {selectedItem?.severity && <Chip label={selectedItem.severity} size="small" sx={{ ml: 1 }} color={getSeverityColor(selectedItem.severity)} />}
          {selectedItem?.status && <Chip label={selectedItem.status} size="small" sx={{ ml: 0.5 }} color={getStatusColor(selectedItem.status)} />}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}><Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Incident Information</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Student</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.student_name}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Title</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.title}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Type</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.incident_type?.replace('_', ' ')}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Date</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.incident_date}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Time</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.incident_time || '-'}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Location</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.location || '-'}</Typography></Grid>
              <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Reported By</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.reported_by_name}</Typography></Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /><Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Details</Typography></Grid>
              <Grid item xs={12}><Typography variant="caption" color="text.secondary">Description</Typography><Typography variant="body2" sx={{ fontWeight: 500, whiteSpace: 'pre-wrap' }}>{selectedItem.description}</Typography></Grid>
              {selectedItem.witnesses && <Grid item xs={12}><Typography variant="caption" color="text.secondary">Witnesses</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.witnesses}</Typography></Grid>}

              {selectedItem.action_taken && (<>
                <Grid item xs={12}><Divider sx={{ my: 1 }} /><Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Action & Follow-up</Typography></Grid>
                <Grid item xs={12}><Typography variant="caption" color="text.secondary">Action Taken</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.action_taken}</Typography></Grid>
              </>)}
              {selectedItem.follow_up_required && (<>
                <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Follow-up Required</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>Yes</Typography></Grid>
                {selectedItem.follow_up_date && <Grid item xs={12} sm={4}><Typography variant="caption" color="text.secondary">Follow-up Date</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.follow_up_date}</Typography></Grid>}
                {selectedItem.follow_up_notes && <Grid item xs={12}><Typography variant="caption" color="text.secondary">Follow-up Notes</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.follow_up_notes}</Typography></Grid>}
              </>)}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />} onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }} sx={{ bgcolor: '#1a237e' }}>Edit</Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog open={openDeleteDialog} title="Delete Incident"
        message={`Are you sure you want to delete "${selectedItem?.title}"? This action cannot be undone.`}
        onConfirm={handleDelete} onCancel={() => setOpenDeleteDialog(false)} confirmText="Delete" severity="error" />
    </Box>
  )
}

export default Discipline
