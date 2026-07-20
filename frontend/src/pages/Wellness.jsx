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
  SelfImprovement as WellnessIcon,
  EventNote as SessionIcon,
  CheckCircle as CompletedIcon,
  Inventory as ResourceIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Wellness() {
  const [sessions, setSessions] = useState([])
  const [checkIns, setCheckIns] = useState([])
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedSession, setSelectedSession] = useState(null)
  const [formData, setFormData] = useState({
    student: '',
    counselor: '',
    session_date: '',
    session_type: '',
    status: 'scheduled',
    notes: '',
    concern_type: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [sessionsRes, checkInsRes, resourcesRes] = await Promise.all([
        api.get('/wellness/counseling-sessions/'),
        api.get('/wellness/check-ins/'),
        api.get('/wellness/resources/'),
      ])
      setSessions(sessionsRes.data.results || sessionsRes.data)
      setCheckIns(checkInsRes.data.results || checkInsRes.data)
      setResources(resourcesRes.data.results || resourcesRes.data)
    } catch (error) {
      console.error('Error fetching wellness data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedSession(null)
    setFormData({
      student: '',
      counselor: '',
      session_date: '',
      session_type: '',
      status: 'scheduled',
      notes: '',
      concern_type: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (session) => {
    setSelectedSession(session)
    setFormData({
      student: session.student,
      counselor: session.counselor,
      session_date: session.session_date || '',
      session_type: session.session_type,
      status: session.status,
      notes: session.notes || '',
      concern_type: session.concern_type || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (session) => {
    setSelectedSession(session)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedSession) {
        await api.put(`/wellness/counseling-sessions/${selectedSession.id}/`, formData)
      } else {
        await api.post('/wellness/counseling-sessions/', formData)
      }
      setOpenDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error saving session:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/wellness/counseling-sessions/${selectedSession.id}/`)
      setOpenDeleteDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }

  const columns = [
    { id: 'student', label: 'Student' },
    { id: 'counselor', label: 'Counselor' },
    { id: 'session_date', label: 'Date' },
    { id: 'session_type', label: 'Type', render: (row) => (
      <Chip
        label={row.session_type}
        size="small"
        color={row.session_type === 'group' ? 'primary' : 'secondary'}
      />
    )},
    { id: 'concern_type', label: 'Concern' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={row.status === 'completed' ? 'success' : row.status === 'pending' ? 'warning' : 'info'}
      />
    )},
  ]

  if (loading) {
    return <Loading message="Loading wellness data..." />
  }

  const pendingSessions = sessions.filter(s => s.status === 'pending')
  const completedSessions = sessions.filter(s => s.status === 'completed')

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Wellness & Counseling</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          New Session
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Sessions"
            value={sessions.length}
            icon={<SessionIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending"
            value={pendingSessions.length}
            icon={<WellnessIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={completedSessions.length}
            icon={<CompletedIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resources Available"
            value={resources.length}
            icon={<ResourceIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={sessions}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(session) => console.log('View:', session)}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedSession ? 'Edit Session' : 'New Counseling Session'}</DialogTitle>
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
              <TextField
                fullWidth
                label="Counselor"
                value={formData.counselor}
                onChange={(e) => setFormData({ ...formData, counselor: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Session Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.session_date}
                onChange={(e) => setFormData({ ...formData, session_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Session Type</InputLabel>
                <Select
                  value={formData.session_type}
                  onChange={(e) => setFormData({ ...formData, session_type: e.target.value })}
                  label="Session Type"
                >
                  <MenuItem value="individual">Individual</MenuItem>
                  <MenuItem value="group">Group</MenuItem>
                  <MenuItem value="virtual">Virtual</MenuItem>
                  <MenuItem value="emergency">Emergency</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Concern Type</InputLabel>
                <Select
                  value={formData.concern_type}
                  onChange={(e) => setFormData({ ...formData, concern_type: e.target.value })}
                  label="Concern Type"
                >
                  <MenuItem value="academic">Academic</MenuItem>
                  <MenuItem value="behavioral">Behavioral</MenuItem>
                  <MenuItem value="emotional">Emotional</MenuItem>
                  <MenuItem value="social">Social</MenuItem>
                  <MenuItem value="family">Family</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
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
            {selectedSession ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Session"
        message={`Are you sure you want to delete this counseling session? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Wellness
