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
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function CoCurricular() {
  const [activities, setActivities] = useState([])
  const [competitions, setCompetitions] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedActivity, setSelectedActivity] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    activity_type: '',
    school: '',
    coordinator: '',
    schedule: '',
    participant_count: '',
    status: '',
  })

  useEffect(() => {
    fetchActivities()
    fetchCompetitions()
  }, [])

  const fetchActivities = async () => {
    try {
      const response = await api.get('/co-curricular/activities/')
      setActivities(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching co-curricular activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCompetitions = async () => {
    try {
      const response = await api.get('/co-curricular/competitions/')
      setCompetitions(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching competitions:', error)
    }
  }

  const handleAdd = () => {
    setSelectedActivity(null)
    setFormData({
      name: '',
      activity_type: '',
      school: '',
      coordinator: '',
      schedule: '',
      participant_count: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (activity) => {
    setSelectedActivity(activity)
    setFormData({
      name: activity.name,
      activity_type: activity.activity_type,
      school: activity.school,
      coordinator: activity.coordinator || '',
      schedule: activity.schedule || '',
      participant_count: activity.participant_count || '',
      status: activity.status,
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
        await api.put(`/co-curricular/activities/${selectedActivity.id}/`, formData)
      } else {
        await api.post('/co-curricular/activities/', formData)
      }
      setOpenDialog(false)
      fetchActivities()
    } catch (error) {
      console.error('Error saving co-curricular activity:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/co-curricular/activities/${selectedActivity.id}/`)
      setOpenDeleteDialog(false)
      fetchActivities()
    } catch (error) {
      console.error('Error deleting co-curricular activity:', error)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'INACTIVE': return 'default'
      case 'UPCOMING': return 'info'
      default: return 'default'
    }
  }

  const typeColor = (type) => {
    switch (type) {
      case 'SPORTS': return 'success'
      case 'CULTURE': return 'secondary'
      case 'CLUB': return 'info'
      case 'DEBATE': return 'warning'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'name', label: 'Activity Name' },
    { id: 'activity_type', label: 'Type', render: (row) => (
      <Chip label={row.activity_type} size="small" color={typeColor(row.activity_type)} />
    )},
    { id: 'school', label: 'School' },
    { id: 'coordinator', label: 'Coordinator' },
    { id: 'schedule', label: 'Schedule' },
    { id: 'participant_count', label: 'Participants', align: 'right' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading co-curricular activities..." />
  }

  const activeActivities = activities.filter(a => a.status === 'ACTIVE').length
  const totalParticipants = activities.reduce((sum, a) => sum + (parseInt(a.participant_count) || 0), 0)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Co-Curricular Activities</Typography>
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
            icon={<TrophyIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active"
            value={activeActivities}
            icon={<TrophyIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Competitions"
            value={competitions.length}
            icon={<TrophyIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Participants"
            value={totalParticipants}
            icon={<TrophyIcon />}
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
        <DialogTitle>{selectedActivity ? 'Edit Activity' : 'Add New Activity'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Activity Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Activity Type</InputLabel>
                <Select
                  value={formData.activity_type}
                  onChange={(e) => setFormData({ ...formData, activity_type: e.target.value })}
                  label="Activity Type"
                >
                  <MenuItem value="SPORTS">Sports</MenuItem>
                  <MenuItem value="CULTURE">Culture</MenuItem>
                  <MenuItem value="CLUB">Club</MenuItem>
                  <MenuItem value="DEBATE">Debate</MenuItem>
                  <MenuItem value="MUSIC">Music</MenuItem>
                  <MenuItem value="DRAMA">Drama</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="School"
                value={formData.school}
                onChange={(e) => setFormData({ ...formData, school: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Coordinator"
                value={formData.coordinator}
                onChange={(e) => setFormData({ ...formData, coordinator: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Schedule"
                value={formData.schedule}
                onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Participant Count"
                type="number"
                value={formData.participant_count}
                onChange={(e) => setFormData({ ...formData, participant_count: e.target.value })}
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
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
                  <MenuItem value="UPCOMING">Upcoming</MenuItem>
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
            {selectedActivity ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Activity"
        message={`Are you sure you want to delete ${selectedActivity?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default CoCurricular
