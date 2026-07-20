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
  Schedule as ScheduleIcon,
  AccessTime as AccessTimeIcon,
  Today as TodayIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Timetable() {
  const [periods, setPeriods] = useState([])
  const [timetables, setTimetables] = useState([])
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedPeriod, setSelectedPeriod] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    start_time: '',
    end_time: '',
    day_of_week: '',
    subject: '',
    teacher: '',
    classroom: '',
    period: '',
  })

  useEffect(() => {
    fetchPeriods()
    fetchTimetables()
    fetchEntries()
    fetchStats()
  }, [])

  const fetchPeriods = async () => {
    try {
      const response = await api.get('/timetable/periods/')
      setPeriods(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching periods:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTimetables = async () => {
    try {
      const response = await api.get('/timetable/timetables/')
      setTimetables(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching timetables:', error)
    }
  }

  const fetchEntries = async () => {
    try {
      const response = await api.get('/timetable/entries/')
      setEntries(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching entries:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/analytics/stats/timetable_stats/')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedPeriod(null)
    setFormData({
      name: '',
      start_time: '',
      end_time: '',
      day_of_week: '',
      subject: '',
      teacher: '',
      classroom: '',
      period: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (period) => {
    setSelectedPeriod(period)
    setFormData({
      name: period.name,
      start_time: period.start_time,
      end_time: period.end_time,
      day_of_week: period.day_of_week,
      subject: period.subject,
      teacher: period.teacher,
      classroom: period.classroom,
      period: period.period,
    })
    setOpenDialog(true)
  }

  const handleDelete = (period) => {
    setSelectedPeriod(period)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedPeriod) {
        await api.put(`/timetable/periods/${selectedPeriod.id}/`, formData)
      } else {
        await api.post('/timetable/periods/', formData)
      }
      setOpenDialog(false)
      fetchPeriods()
    } catch (error) {
      console.error('Error saving period:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/timetable/periods/${selectedPeriod.id}/`)
      setOpenDeleteDialog(false)
      fetchPeriods()
    } catch (error) {
      console.error('Error deleting period:', error)
    }
  }

  const getDayColor = (day) => {
    const colors = {
      MONDAY: 'primary',
      TUESDAY: 'secondary',
      WEDNESDAY: 'success',
      THURSDAY: 'warning',
      FRIDAY: 'error',
      SATURDAY: 'info',
      SUNDAY: 'default',
    }
    return colors[day] || 'default'
  }

  const periodColumns = [
    { id: 'name', label: 'Period Name' },
    { id: 'start_time', label: 'Start Time', render: (row) => (
      <Chip
        icon={<AccessTimeIcon />}
        label={row.start_time}
        size="small"
        color="primary"
        variant="outlined"
      />
    )},
    { id: 'end_time', label: 'End Time', render: (row) => (
      <Chip
        icon={<AccessTimeIcon />}
        label={row.end_time}
        size="small"
        color="secondary"
        variant="outlined"
      />
    )},
    { id: 'day_of_week', label: 'Day', render: (row) => (
      <Chip label={row.day_of_week} size="small" color={getDayColor(row.day_of_week)} />
    )},
    { id: 'subject', label: 'Subject' },
    { id: 'teacher', label: 'Teacher', render: (row) => (
      <Chip
        icon={<PersonIcon />}
        label={row.teacher}
        size="small"
        variant="outlined"
      />
    )},
    { id: 'classroom', label: 'Classroom' },
    { id: 'period', label: 'Period', align: 'right' },
  ]

  const entryColumns = [
    { id: 'subject', label: 'Subject' },
    { id: 'teacher', label: 'Teacher' },
    { id: 'classroom', label: 'Classroom' },
    { id: 'day_of_week', label: 'Day', render: (row) => (
      <Chip label={row.day_of_week} size="small" color={getDayColor(row.day_of_week)} />
    )},
    { id: 'start_time', label: 'Time', render: (row) => (
      <Typography variant="body2" color="text.secondary">
        {row.start_time} - {row.end_time}
      </Typography>
    )},
  ]

  if (loading) {
    return <Loading message="Loading timetable..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Timetable Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Period
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Periods"
            value={periods.length}
            icon={<ScheduleIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Timetables"
            value={timetables.filter(t => t.is_active).length}
            icon={<TodayIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Classes"
            value={entries.filter(e => e.day_of_week === new Date().toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase()).length}
            icon={<AccessTimeIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Teacher Schedules"
            value={[...new Set(entries.map(e => e.teacher))].length}
            icon={<PersonIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Periods Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Periods</Typography>
          <DataTable
            columns={periodColumns}
            data={periods}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onView={(period) => console.log('View:', period)}
          />
        </CardContent>
      </Card>

      {/* Entries Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Timetable Entries</Typography>
          <DataTable
            columns={entryColumns}
            data={entries}
            onView={(entry) => console.log('View:', entry)}
          />
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedPeriod ? 'Edit Period' : 'Add New Period'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Period Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Day of Week</InputLabel>
                <Select
                  value={formData.day_of_week}
                  onChange={(e) => setFormData({ ...formData, day_of_week: e.target.value })}
                  label="Day of Week"
                >
                  <MenuItem value="MONDAY">Monday</MenuItem>
                  <MenuItem value="TUESDAY">Tuesday</MenuItem>
                  <MenuItem value="WEDNESDAY">Wednesday</MenuItem>
                  <MenuItem value="THURSDAY">Thursday</MenuItem>
                  <MenuItem value="FRIDAY">Friday</MenuItem>
                  <MenuItem value="SATURDAY">Saturday</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Start Time"
                type="time"
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="End Time"
                type="time"
                value={formData.end_time}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Teacher"
                value={formData.teacher}
                onChange={(e) => setFormData({ ...formData, teacher: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Classroom"
                value={formData.classroom}
                onChange={(e) => setFormData({ ...formData, classroom: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Period Number"
                type="number"
                value={formData.period}
                onChange={(e) => setFormData({ ...formData, period: e.target.value })}
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
            {selectedPeriod ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Period"
        message={`Are you sure you want to delete ${selectedPeriod?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Timetable
