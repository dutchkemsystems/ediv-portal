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
  DirectionsBus as BusIcon,
  Route as RouteIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Transport() {
  const [vehicles, setVehicles] = useState([])
  const [routes, setRoutes] = useState([])
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [formData, setFormData] = useState({
    vehicle_number: '',
    plate_number: '',
    capacity: '',
    driver_name: '',
    route_name: '',
    pickup_point: '',
    fare: '',
    status: '',
  })

  useEffect(() => {
    fetchVehicles()
    fetchRoutes()
    fetchAssignments()
    fetchStats()
  }, [])

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/transport/vehicles/')
      setVehicles(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching vehicles:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoutes = async () => {
    try {
      const response = await api.get('/transport/routes/')
      setRoutes(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching routes:', error)
    }
  }

  const fetchAssignments = async () => {
    try {
      const response = await api.get('/transport/student-transport/')
      setAssignments(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching assignments:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/analytics/stats/transport_stats/')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedVehicle(null)
    setFormData({
      vehicle_number: '',
      plate_number: '',
      capacity: '',
      driver_name: '',
      route_name: '',
      pickup_point: '',
      fare: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (vehicle) => {
    setSelectedVehicle(vehicle)
    setFormData({
      vehicle_number: vehicle.vehicle_number,
      plate_number: vehicle.plate_number,
      capacity: vehicle.capacity,
      driver_name: vehicle.driver_name,
      route_name: vehicle.route_name,
      pickup_point: vehicle.pickup_point,
      fare: vehicle.fare,
      status: vehicle.status,
    })
    setOpenDialog(true)
  }

  const handleDelete = (vehicle) => {
    setSelectedVehicle(vehicle)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedVehicle) {
        await api.put(`/transport/vehicles/${selectedVehicle.id}/`, formData)
      } else {
        await api.post('/transport/vehicles/', formData)
      }
      setOpenDialog(false)
      fetchVehicles()
    } catch (error) {
      console.error('Error saving vehicle:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/transport/vehicles/${selectedVehicle.id}/`)
      setOpenDeleteDialog(false)
      fetchVehicles()
    } catch (error) {
      console.error('Error deleting vehicle:', error)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      ACTIVE: 'success',
      INACTIVE: 'default',
      MAINTENANCE: 'warning',
      RETIRED: 'error',
    }
    return colors[status] || 'default'
  }

  const vehicleColumns = [
    { id: 'vehicle_number', label: 'Vehicle No.' },
    { id: 'plate_number', label: 'Plate Number', render: (row) => (
      <Chip label={row.plate_number} size="small" color="primary" variant="outlined" />
    )},
    { id: 'capacity', label: 'Capacity', align: 'right' },
    { id: 'driver_name', label: 'Driver', render: (row) => (
      <Chip
        icon={<PersonIcon />}
        label={row.driver_name}
        size="small"
        variant="outlined"
      />
    )},
    { id: 'route_name', label: 'Route' },
    { id: 'fare', label: 'Fare', align: 'right', render: (row) => (
      <Typography variant="body2" color="text.secondary">
        ₦{Number(row.fare).toLocaleString()}
      </Typography>
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
  ]

  const routeColumns = [
    { id: 'name', label: 'Route Name' },
    { id: 'pickup_point', label: 'Pickup Point' },
    { id: 'fare', label: 'Fare', align: 'right', render: (row) => (
      <Typography variant="body2" color="text.secondary">
        ₦{Number(row.fare).toLocaleString()}
      </Typography>
    )},
    { id: 'is_active', label: 'Status', render: (row) => (
      <Chip
        label={row.is_active ? 'Active' : 'Inactive'}
        size="small"
        color={row.is_active ? 'success' : 'default'}
      />
    )},
  ]

  const assignmentColumns = [
    { id: 'student_name', label: 'Student' },
    { id: 'vehicle_number', label: 'Vehicle' },
    { id: 'route_name', label: 'Route' },
    { id: 'pickup_point', label: 'Pickup Point' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={row.status === 'ACTIVE' ? 'success' : row.status === 'PENDING' ? 'warning' : 'default'}
      />
    )},
  ]

  if (loading) {
    return <Loading message="Loading transport..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Transport Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Vehicle
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Vehicles"
            value={vehicles.length}
            icon={<BusIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Routes"
            value={routes.filter(r => r.is_active).length}
            icon={<RouteIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Assigned Students"
            value={assignments.filter(a => a.status === 'ACTIVE').length}
            icon={<PersonIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Assignments"
            value={assignments.filter(a => a.status === 'PENDING').length}
            icon={<AssignmentIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Vehicles Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Vehicles</Typography>
          <DataTable
            columns={vehicleColumns}
            data={vehicles}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onView={(vehicle) => console.log('View:', vehicle)}
          />
        </CardContent>
      </Card>

      {/* Routes Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Routes</Typography>
          <DataTable
            columns={routeColumns}
            data={routes}
            onView={(route) => console.log('View:', route)}
          />
        </CardContent>
      </Card>

      {/* Assignments Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Student Assignments</Typography>
          <DataTable
            columns={assignmentColumns}
            data={assignments}
            onView={(assignment) => console.log('View:', assignment)}
          />
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Vehicle Number"
                value={formData.vehicle_number}
                onChange={(e) => setFormData({ ...formData, vehicle_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Plate Number"
                value={formData.plate_number}
                onChange={(e) => setFormData({ ...formData, plate_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Capacity"
                type="number"
                value={formData.capacity}
                onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Driver Name"
                value={formData.driver_name}
                onChange={(e) => setFormData({ ...formData, driver_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Route Name"
                value={formData.route_name}
                onChange={(e) => setFormData({ ...formData, route_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Pickup Point"
                value={formData.pickup_point}
                onChange={(e) => setFormData({ ...formData, pickup_point: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Fare"
                type="number"
                value={formData.fare}
                onChange={(e) => setFormData({ ...formData, fare: e.target.value })}
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
                  <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                  <MenuItem value="RETIRED">Retired</MenuItem>
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
            {selectedVehicle ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Vehicle"
        message={`Are you sure you want to delete ${selectedVehicle?.vehicle_number}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Transport
