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
} from '@mui/material'
import {
  Add as AddIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Staff() {
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedStaff, setSelectedStaff] = useState(null)

  useEffect(() => {
    fetchStaff()
  }, [])

  const fetchStaff = async () => {
    try {
      const response = await api.get('/staff/staff/')
      setStaff(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching staff:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/staff/staff/${selectedStaff.id}/`)
      setOpenDeleteDialog(false)
      fetchStaff()
    } catch (error) {
      console.error('Error deleting staff:', error)
    }
  }

  const columns = [
    { id: 'full_name', label: 'Name', render: (row) => row.user?.first_name + ' ' + row.user?.last_name },
    { id: 'staff_id', label: 'Staff ID' },
    { id: 'employee_number', label: 'Employee No.' },
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category} size="small" />
    )},
    { id: 'designation', label: 'Designation' },
    { id: 'school_name', label: 'School', render: (row) => row.school_name || 'Head Office' },
    { id: 'is_active', label: 'Status', render: (row) => (
      <Chip label={row.is_active ? 'Active' : 'Inactive'} size="small" color={row.is_active ? 'success' : 'default'} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading staff..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Staff Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Staff
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Staff"
            value={staff.length}
            icon={<PeopleIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Teaching Staff"
            value={staff.filter(s => s.category === 'TEACHING').length}
            icon={<PeopleIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Non-Teaching"
            value={staff.filter(s => s.category === 'NON_TEACHING').length}
            icon={<PeopleIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Staff"
            value={staff.filter(s => s.is_active).length}
            icon={<PeopleIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={staff}
        onEdit={(s) => console.log('Edit:', s)}
        onDelete={(s) => { setSelectedStaff(s); setOpenDeleteDialog(true); }}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Staff"
        message={`Are you sure you want to delete ${selectedStaff?.full_name}? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Staff
