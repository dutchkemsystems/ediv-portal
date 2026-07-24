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
  Alert,
} from '@mui/material'
import {
  Add as AddIcon,
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Staff() {
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedStaff, setSelectedStaff] = useState(null)

  const [currentUser, setCurrentUser] = useState(null)
  const [openTeacherDialog, setOpenTeacherDialog] = useState(false)
  const [teacherForm, setTeacherForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
  })
  const [createdTeacher, setCreatedTeacher] = useState(null)
  const [creatingTeacher, setCreatingTeacher] = useState(false)

  const canCreateTeacher = currentUser?.role === 'PRI' || currentUser?.role === 'VP'

  useEffect(() => {
    fetchStaff()
    fetchCurrentUser()
  }, [])

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/users/users/me/')
      setCurrentUser(response.data)
    } catch (error) {
      console.error('Failed to fetch current user')
    }
  }

  const fetchStaff = async () => {
    try {
      const response = await api.get('/staff/staff/')
      setStaff(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load staff')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/staff/staff/${selectedStaff.id}/`)
      notify.success('Staff deleted successfully')
      setOpenDeleteDialog(false)
      fetchStaff()
    } catch (error) {
      notify.error('Failed to delete staff')
    }
  }

  const handleCreateTeacher = async () => {
    setCreatingTeacher(true)
    try {
      const response = await api.post('/users/users/create-teacher/', teacherForm)
      setCreatedTeacher(response.data.teacher)
      notify.success('Teacher account created successfully')
      setTeacherForm({ first_name: '', last_name: '', email: '', phone_number: '' })
      fetchStaff()
    } catch (error) {
      const msg = error.response?.data?.error || error.response?.data?.email?.[0] || 'Failed to create teacher'
      notify.error(msg)
    } finally {
      setCreatingTeacher(false)
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
        <Box sx={{ display: 'flex', gap: 1 }}>
          {canCreateTeacher && (
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={() => { setCreatedTeacher(null); setOpenTeacherDialog(true) }}
              sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}
            >
              Create Teacher Account
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Add Staff
          </Button>
        </Box>
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

      {/* Create Teacher Dialog */}
      <Dialog open={openTeacherDialog} onClose={() => setOpenTeacherDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PersonAddIcon /> Create Teacher Account
        </DialogTitle>
        <DialogContent>
          {createdTeacher ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">Teacher Account Created</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Name:</strong> {createdTeacher.first_name} {createdTeacher.last_name}<br />
                <strong>Email:</strong> {createdTeacher.email}<br />
                <strong>School:</strong> {createdTeacher.school}<br />
                <strong>Temporary Password:</strong> <code>{createdTeacher.temp_password}</code><br /><br />
                Please share these credentials securely with the teacher. They should change their password on first login.
              </Typography>
            </Alert>
          ) : (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  value={teacherForm.first_name}
                  onChange={(e) => setTeacherForm({ ...teacherForm, first_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  value={teacherForm.last_name}
                  onChange={(e) => setTeacherForm({ ...teacherForm, last_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={teacherForm.email}
                  onChange={(e) => setTeacherForm({ ...teacherForm, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Phone Number"
                  value={teacherForm.phone_number}
                  onChange={(e) => setTeacherForm({ ...teacherForm, phone_number: e.target.value })}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTeacherDialog(false)}>
            {createdTeacher ? 'Close' : 'Cancel'}
          </Button>
          {!createdTeacher && (
            <Button
              onClick={handleCreateTeacher}
              variant="contained"
              disabled={creatingTeacher || !teacherForm.first_name || !teacherForm.last_name || !teacherForm.email}
              sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}
            >
              {creatingTeacher ? 'Creating...' : 'Create Account'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

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
