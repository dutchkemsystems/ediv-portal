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
  Translate as TranslateIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function French() {
  const [programs, setPrograms] = useState([])
  const [clubs, setClubs] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedProgram, setSelectedProgram] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    school: '',
    coordinator: '',
    meeting_day: '',
    member_count: '',
    level: '',
    status: '',
  })

  useEffect(() => {
    fetchPrograms()
    fetchClubs()
  }, [])

  const fetchPrograms = async () => {
    try {
      const response = await api.get('/french/programs/')
      setPrograms(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching French programs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchClubs = async () => {
    try {
      const response = await api.get('/french/clubs/')
      setClubs(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching French clubs:', error)
    }
  }

  const handleAdd = () => {
    setSelectedProgram(null)
    setFormData({
      name: '',
      description: '',
      school: '',
      coordinator: '',
      meeting_day: '',
      member_count: '',
      level: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (program) => {
    setSelectedProgram(program)
    setFormData({
      name: program.name,
      description: program.description || '',
      school: program.school,
      coordinator: program.coordinator || '',
      meeting_day: program.meeting_day || '',
      member_count: program.member_count || '',
      level: program.level || '',
      status: program.status,
    })
    setOpenDialog(true)
  }

  const handleDelete = (program) => {
    setSelectedProgram(program)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedProgram) {
        await api.put(`/french/programs/${selectedProgram.id}/`, formData)
      } else {
        await api.post('/french/programs/', formData)
      }
      setOpenDialog(false)
      fetchPrograms()
    } catch (error) {
      console.error('Error saving French program:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/french/programs/${selectedProgram.id}/`)
      setOpenDeleteDialog(false)
      fetchPrograms()
    } catch (error) {
      console.error('Error deleting French program:', error)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'INACTIVE': return 'default'
      case 'COMPLETED': return 'info'
      default: return 'default'
    }
  }

  const levelColor = (level) => {
    switch (level) {
      case 'BEGINNER': return 'info'
      case 'INTERMEDIATE': return 'warning'
      case 'ADVANCED': return 'success'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'name', label: 'Program Name' },
    { id: 'school', label: 'School' },
    { id: 'coordinator', label: 'Coordinator' },
    { id: 'meeting_day', label: 'Meeting Day' },
    { id: 'member_count', label: 'Members', align: 'right' },
    { id: 'level', label: 'Level', render: (row) => (
      <Chip label={row.level} size="small" color={levelColor(row.level)} />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading French programs..." />
  }

  const activeClubs = clubs.filter(c => c.status === 'ACTIVE').length
  const totalMembers = programs.reduce((sum, p) => sum + (parseInt(p.member_count) || 0), 0)
  const competitions = clubs.filter(c => c.activity_type === 'COMPETITION' || c.type === 'COMPETITION').length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">French Language Programs</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Program
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Programs"
            value={programs.length}
            icon={<TranslateIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Clubs"
            value={activeClubs}
            icon={<TranslateIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Members"
            value={totalMembers}
            icon={<TranslateIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Competitions"
            value={competitions}
            icon={<TranslateIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={programs}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedProgram ? 'Edit Program' : 'Add New French Program'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Program Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="School"
                value={formData.school}
                onChange={(e) => setFormData({ ...formData, school: e.target.value })}
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
                label="Coordinator"
                value={formData.coordinator}
                onChange={(e) => setFormData({ ...formData, coordinator: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Meeting Day</InputLabel>
                <Select
                  value={formData.meeting_day}
                  onChange={(e) => setFormData({ ...formData, meeting_day: e.target.value })}
                  label="Meeting Day"
                >
                  <MenuItem value="MONDAY">Monday</MenuItem>
                  <MenuItem value="TUESDAY">Tuesday</MenuItem>
                  <MenuItem value="WEDNESDAY">Wednesday</MenuItem>
                  <MenuItem value="THURSDAY">Thursday</MenuItem>
                  <MenuItem value="FRIDAY">Friday</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Member Count"
                type="number"
                value={formData.member_count}
                onChange={(e) => setFormData({ ...formData, member_count: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Level</InputLabel>
                <Select
                  value={formData.level}
                  onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                  label="Level"
                >
                  <MenuItem value="BEGINNER">Beginner</MenuItem>
                  <MenuItem value="INTERMEDIATE">Intermediate</MenuItem>
                  <MenuItem value="ADVANCED">Advanced</MenuItem>
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
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
                  <MenuItem value="COMPLETED">Completed</MenuItem>
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
            {selectedProgram ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete French Program"
        message={`Are you sure you want to delete ${selectedProgram?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default French
