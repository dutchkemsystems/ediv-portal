import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
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
  School as SchoolIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function CPD() {
  const [activities, setActivities] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedActivity, setSelectedActivity] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    trainer: '',
    start_date: '',
    end_date: '',
    hours: '',
    status: '',
    enrollment_count: '',
  })

  useEffect(() => {
    fetchActivities()
    fetchEnrollments()
  }, [])

  const fetchActivities = async () => {
    try {
      const response = await api.get('/cpd/activities/')
      setActivities(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching CPD activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchEnrollments = async () => {
    try {
      const response = await api.get('/cpd/enrollments/')
      setEnrollments(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching enrollments:', error)
    }
  }

  const handleAdd = () => {
    setSelectedActivity(null)
    setFormData({
      title: '',
      description: '',
      trainer: '',
      start_date: '',
      end_date: '',
      hours: '',
      status: '',
      enrollment_count: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (activity) => {
    setSelectedActivity(activity)
    setFormData({
      title: activity.title,
      description: activity.description || '',
      trainer: activity.trainer || '',
      start_date: activity.start_date || '',
      end_date: activity.end_date || '',
      hours: activity.hours || '',
      status: activity.status,
      enrollment_count: activity.enrollment_count || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (activity) => {
    setSelectedActivity(activity)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedActivity) {
        await api.put(`/cpd/activities/${selectedActivity.id}/`, formData)
      } else {
        await api.post('/cpd/activities/', formData)
      }
      setOpenDialog(false)
      fetchActivities()
    } catch (error) {
      console.error('Error saving CPD activity:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/cpd/activities/${selectedActivity.id}/`)
      setOpenDeleteDialog(false)
      fetchActivities()
    } catch (error) {
      console.error('Error deleting CPD activity:', error)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'ONGOING': return 'info'
      case 'COMPLETED': return 'success'
      case 'UPCOMING': return 'warning'
      case 'CANCELLED': return 'error'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'title', label: 'Title' },
    { id: 'trainer', label: 'Trainer' },
    { id: 'start_date', label: 'Start Date' },
    { id: 'end_date', label: 'End Date' },
    { id: 'hours', label: 'Hours', align: 'right' },
    { id: 'enrollment_count', label: 'Enrolled', align: 'right' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading CPD activities..." />
  }

  const ongoing = activities.filter(a => a.status === 'ONGOING').length
  const completed = activities.filter(a => a.status === 'COMPLETED').length
  const certificatesIssued = enrollments.filter(e => e.certificate_issued || e.status === 'COMPLETED').length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Continuing Professional Development</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Activity
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Activities"
            value={activities.length}
            icon={<SchoolIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Ongoing"
            value={ongoing}
            icon={<SchoolIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={completed}
            icon={<SchoolIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Certificates Issued"
            value={certificatesIssued}
            icon={<SchoolIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={activities}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedActivity ? 'Edit CPD Activity' : 'Add New CPD Activity'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Trainer"
                value={formData.trainer}
                onChange={(e) => setFormData({ ...formData, trainer: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Hours"
                type="number"
                value={formData.hours}
                onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
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
                  <MenuItem value="UPCOMING">Upcoming</MenuItem>
                  <MenuItem value="ONGOING">Ongoing</MenuItem>
                  <MenuItem value="COMPLETED">Completed</MenuItem>
                  <MenuItem value="CANCELLED">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Enrollment Count"
                type="number"
                value={formData.enrollment_count}
                onChange={(e) => setFormData({ ...formData, enrollment_count: e.target.value })}
              />
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
            {selectedActivity ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete CPD Activity"
        message={`Are you sure you want to delete ${selectedActivity?.title}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default CPD
