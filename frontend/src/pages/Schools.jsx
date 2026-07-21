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
  School as SchoolIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Schools() {
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedSchool, setSelectedSchool] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    school_type: '',
    lga: '',
    address: '',
    phone: '',
    email: '',
  })

  useEffect(() => {
    fetchSchools()
    fetchStats()
  }, [])

  const fetchSchools = async () => {
    try {
      const response = await api.get('/schools/schools/')
      setSchools(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching schools:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/analytics/stats/school_stats/')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedSchool(null)
    setFormData({
      name: '',
      code: '',
      school_type: '',
      lga: '',
      address: '',
      phone: '',
      email: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (school) => {
    setSelectedSchool(school)
    setFormData({
      name: school.name,
      code: school.code,
      school_type: school.school_type,
      lga: school.lga,
      address: school.address,
      phone: school.phone || '',
      email: school.email || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (school) => {
    setSelectedSchool(school)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedSchool) {
        await api.put(`/schools/schools/${selectedSchool.id}/`, formData)
      } else {
        await api.post('/schools/schools/', formData)
      }
      setOpenDialog(false)
      fetchSchools()
    } catch (error) {
      console.error('Error saving school:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/schools/schools/${selectedSchool.id}/`)
      setOpenDeleteDialog(false)
      fetchSchools()
    } catch (error) {
      console.error('Error deleting school:', error)
    }
  }

  const columns = [
    { id: 'name', label: 'School Name' },
    { id: 'code', label: 'Code' },
    { id: 'school_type', label: 'Type', render: (row) => (
      <Chip label={row.school_type} size="small" color={row.school_type === 'SENIOR' ? 'primary' : 'secondary'} />
    )},
    { id: 'lga', label: 'LGA' },
    { id: 'current_enrollment', label: 'Students', align: 'right' },
    { id: 'is_active', label: 'Status', render: (row) => (
      <Chip label={row.is_active ? 'Active' : 'Inactive'} size="small" color={row.is_active ? 'success' : 'default'} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading schools..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Schools Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add School
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Schools"
            value={schools.length}
            icon={<SchoolIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Junior Secondary"
            value={schools.filter(s => s.school_type === 'JUNIOR').length}
            icon={<SchoolIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Senior Secondary"
            value={schools.filter(s => s.school_type === 'SENIOR').length}
            icon={<SchoolIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Schools"
            value={schools.filter(s => s.is_active).length}
            icon={<SchoolIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={schools}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(school) => console.log('View:', school)}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedSchool ? 'Edit School' : 'Add New School'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="School Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="School Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>School Type</InputLabel>
                <Select
                  value={formData.school_type}
                  onChange={(e) => setFormData({ ...formData, school_type: e.target.value })}
                  label="School Type"
                >
                  <MenuItem value="JUNIOR">Junior Secondary</MenuItem>
                  <MenuItem value="SENIOR">Senior Secondary</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>LGA</InputLabel>
                <Select
                  value={formData.lga}
                  onChange={(e) => setFormData({ ...formData, lga: e.target.value })}
                  label="LGA"
                >
                  <MenuItem value="APAPA">Apapa</MenuItem>
                  <MenuItem value="MAINLAND">Mainland</MenuItem>
                  <MenuItem value="SURULERE">Surulere</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                multiline
                rows={2}
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
            {selectedSchool ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete School"
        message={`Are you sure you want to delete ${selectedSchool?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Schools
