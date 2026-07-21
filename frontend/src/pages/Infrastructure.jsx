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
  Build as BuildIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Infrastructure() {
  const [facilities, setFacilities] = useState([])
  const [maintenanceRequests, setMaintenanceRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedFacility, setSelectedFacility] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    facility_type: '',
    school: '',
    condition: '',
    last_maintenance: '',
    next_maintenance: '',
    status: '',
  })

  useEffect(() => {
    fetchFacilities()
    fetchMaintenanceRequests()
  }, [])

  const fetchFacilities = async () => {
    try {
      const response = await api.get('/infrastructure/facilities/')
      setFacilities(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching facilities:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchMaintenanceRequests = async () => {
    try {
      const response = await api.get('/infrastructure/maintenance-requests/')
      setMaintenanceRequests(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching maintenance requests:', error)
    }
  }

  const handleAdd = () => {
    setSelectedFacility(null)
    setFormData({
      name: '',
      facility_type: '',
      school: '',
      condition: '',
      last_maintenance: '',
      next_maintenance: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (facility) => {
    setSelectedFacility(facility)
    setFormData({
      name: facility.name,
      facility_type: facility.facility_type,
      school: facility.school,
      condition: facility.condition,
      last_maintenance: facility.last_maintenance || '',
      next_maintenance: facility.next_maintenance || '',
      status: facility.status,
    })
    setOpenDialog(true)
  }

  const handleDelete = (facility) => {
    setSelectedFacility(facility)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedFacility) {
        await api.put(`/infrastructure/facilities/${selectedFacility.id}/`, formData)
      } else {
        await api.post('/infrastructure/facilities/', formData)
      }
      setOpenDialog(false)
      fetchFacilities()
    } catch (error) {
      console.error('Error saving facility:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/infrastructure/facilities/${selectedFacility.id}/`)
      setOpenDeleteDialog(false)
      fetchFacilities()
    } catch (error) {
      console.error('Error deleting facility:', error)
    }
  }

  const conditionColor = (condition) => {
    switch (condition) {
      case 'GOOD': return 'success'
      case 'FAIR': return 'warning'
      case 'POOR': return 'error'
      default: return 'default'
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'MAINTENANCE': return 'warning'
      case 'INACTIVE': return 'default'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'name', label: 'Facility Name' },
    { id: 'facility_type', label: 'Type' },
    { id: 'school', label: 'School' },
    { id: 'condition', label: 'Condition', render: (row) => (
      <Chip label={row.condition} size="small" color={conditionColor(row.condition)} />
    )},
    { id: 'last_maintenance', label: 'Last Maintenance' },
    { id: 'next_maintenance', label: 'Next Maintenance' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading infrastructure data..." />
  }

  const goodCondition = facilities.filter(f => f.condition === 'GOOD').length
  const needsRepair = facilities.filter(f => f.condition === 'POOR' || f.condition === 'FAIR').length
  const pendingMaintenance = maintenanceRequests.filter(r => r.status === 'PENDING').length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Infrastructure Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Facility
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Facilities"
            value={facilities.length}
            icon={<BuildIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Good Condition"
            value={goodCondition}
            icon={<BuildIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Needs Repair"
            value={needsRepair}
            icon={<BuildIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Maintenance"
            value={pendingMaintenance}
            icon={<BuildIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={facilities}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedFacility ? 'Edit Facility' : 'Add New Facility'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Facility Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Facility Type</InputLabel>
                <Select
                  value={formData.facility_type}
                  onChange={(e) => setFormData({ ...formData, facility_type: e.target.value })}
                  label="Facility Type"
                >
                  <MenuItem value="CLASSROOM">Classroom</MenuItem>
                  <MenuItem value="LABORATORY">Laboratory</MenuItem>
                  <MenuItem value="LIBRARY">Library</MenuItem>
                  <MenuItem value="SPORTS">Sports Facility</MenuItem>
                  <MenuItem value="ADMIN">Administrative</MenuItem>
                  <MenuItem value="SANITARY">Sanitary</MenuItem>
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
              <FormControl fullWidth>
                <InputLabel>Condition</InputLabel>
                <Select
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                  label="Condition"
                >
                  <MenuItem value="GOOD">Good</MenuItem>
                  <MenuItem value="FAIR">Fair</MenuItem>
                  <MenuItem value="POOR">Poor</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Maintenance"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.last_maintenance}
                onChange={(e) => setFormData({ ...formData, last_maintenance: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Next Maintenance"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.next_maintenance}
                onChange={(e) => setFormData({ ...formData, next_maintenance: e.target.value })}
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
                  <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
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
            {selectedFacility ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Facility"
        message={`Are you sure you want to delete ${selectedFacility?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Infrastructure
