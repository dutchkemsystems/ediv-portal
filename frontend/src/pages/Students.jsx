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
  Person as PersonIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Students() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState(null)

  useEffect(() => {
    fetchStudents()
  }, [])

  const fetchStudents = async () => {
    try {
      const response = await api.get('/students/students/')
      setStudents(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/students/students/${selectedStudent.id}/`)
      setOpenDeleteDialog(false)
      fetchStudents()
    } catch (error) {
      console.error('Error deleting student:', error)
    }
  }

  const columns = [
    { id: 'full_name', label: 'Name', render: (row) => row.user?.first_name + ' ' + row.user?.last_name },
    { id: 'admission_number', label: 'Admission No.' },
    { id: 'school_name', label: 'School' },
    { id: 'class_name_display', label: 'Class' },
    { id: 'gender', label: 'Gender', render: (row) => (
      <Chip label={row.gender === 'M' ? 'Male' : 'Female'} size="small" color={row.gender === 'M' ? 'primary' : 'secondary'} />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={row.status === 'ACTIVE' ? 'success' : 'default'} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading students..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Student Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Student
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Students"
            value={students.length}
            icon={<PersonIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Male Students"
            value={students.filter(s => s.gender === 'M').length}
            icon={<PersonIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Female Students"
            value={students.filter(s => s.gender === 'F').length}
            icon={<PersonIcon />}
            color="#e91e63"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Students"
            value={students.filter(s => s.status === 'ACTIVE').length}
            icon={<PersonIcon />}
            color="#388e3c"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={students}
        onEdit={(s) => console.log('Edit:', s)}
        onDelete={(s) => { setSelectedStudent(s); setOpenDeleteDialog(true); }}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Student"
        message={`Are you sure you want to delete ${selectedStudent?.full_name}? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Students
