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
  Tabs,
  Tab,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as PresentIcon,
  Cancel as AbsentIcon,
  AccessTime as LateIcon,
  EventNote as AttendanceIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Attendance() {
  const [tab, setTab] = useState(0)
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [filterDate, setFilterDate] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [formData, setFormData] = useState({
    student: '',
    staff: '',
    date: '',
    status: '',
    check_in_time: '',
    check_out_time: '',
    notes: '',
  })

  useEffect(() => {
    fetchRecords()
  }, [tab])

  const fetchRecords = async () => {
    try {
      setLoading(true)
      const endpoint = tab === 0
        ? '/attendance/student-attendance/'
        : '/attendance/staff-attendance/'
      const response = await api.get(endpoint)
      setRecords(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load attendance records')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedRecord(null)
    setFormData({
      student: '',
      staff: '',
      date: new Date().toISOString().split('T')[0],
      status: '',
      check_in_time: '',
      check_out_time: '',
      notes: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (record) => {
    setSelectedRecord(record)
    setFormData({
      student: record.student || '',
      staff: record.staff || '',
      date: record.date || '',
      status: record.status || '',
      check_in_time: record.check_in_time || '',
      check_out_time: record.check_out_time || '',
      notes: record.notes || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (record) => {
    setSelectedRecord(record)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      const endpoint = tab === 0
        ? '/attendance/student-attendance/'
        : '/attendance/staff-attendance/'
      if (selectedRecord) {
        await api.put(`/attendance/${tab === 0 ? 'student-attendance' : 'staff-attendance'}/${selectedRecord.id}/`, formData)
      } else {
        await api.post(endpoint, formData)
      }
      setOpenDialog(false)
      fetchRecords()
    } catch (error) {
      console.error('Error saving attendance:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/attendance/${tab === 0 ? 'student-attendance' : 'staff-attendance'}/${selectedRecord.id}/`)
      setOpenDeleteDialog(false)
      fetchRecords()
    } catch (error) {
      console.error('Error deleting attendance:', error)
    }
  }

  const filteredRecords = records.filter((r) => {
    if (filterDate && r.date !== filterDate) return false
    if (filterStatus && r.status !== filterStatus) return false
    return true
  })

  const todayStr = new Date().toISOString().split('T')[0]
  const todayRecords = records.filter((r) => r.date === todayStr)

  const stats = {
    total: records.length,
    presentToday: todayRecords.filter((r) => r.status === 'PRESENT').length,
    absentToday: todayRecords.filter((r) => r.status === 'ABSENT').length,
    lateToday: todayRecords.filter((r) => r.status === 'LATE').length,
  }

  const statusColor = (status) => {
    switch (status) {
      case 'PRESENT': return 'success'
      case 'ABSENT': return 'error'
      case 'LATE': return 'warning'
      case 'EXCUSED': return 'info'
      default: return 'default'
    }
  }

  const columns = tab === 0
    ? [
        { id: 'student_name', label: 'Student' },
        { id: 'date', label: 'Date' },
        { id: 'status', label: 'Status', render: (row) => (
          <Chip label={row.status} size="small" color={statusColor(row.status)} />
        )},
        { id: 'check_in_time', label: 'Check In' },
        { id: 'check_out_time', label: 'Check Out' },
        { id: 'notes', label: 'Notes' },
      ]
    : [
        { id: 'staff_name', label: 'Staff' },
        { id: 'date', label: 'Date' },
        { id: 'status', label: 'Status', render: (row) => (
          <Chip label={row.status} size="small" color={statusColor(row.status)} />
        )},
        { id: 'check_in_time', label: 'Check In' },
        { id: 'check_out_time', label: 'Check Out' },
        { id: 'notes', label: 'Notes' },
      ]

  if (loading) {
    return <Loading message="Loading attendance records..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Attendance Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Record
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Records"
            value={stats.total}
            icon={<AttendanceIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Present Today"
            value={stats.presentToday}
            icon={<PresentIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Absent Today"
            value={stats.absentToday}
            icon={<AbsentIcon />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Late Today"
            value={stats.lateToday}
            icon={<LateIcon />}
            color="#f57c00"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}
        >
          <Tab label="Student Attendance" />
          <Tab label="Staff Attendance" />
        </Tabs>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          label="Filter by Date"
          type="date"
          size="small"
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 180 }}
        />
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Filter by Status</InputLabel>
          <Select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            label="Filter by Status"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="PRESENT">Present</MenuItem>
            <MenuItem value="ABSENT">Absent</MenuItem>
            <MenuItem value="LATE">Late</MenuItem>
            <MenuItem value="EXCUSED">Excused</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filteredRecords}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedRecord ? 'Edit Attendance' : 'Add Attendance Record'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {tab === 0 && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Student ID"
                  value={formData.student}
                  onChange={(e) => setFormData({ ...formData, student: e.target.value })}
                />
              </Grid>
            )}
            {tab === 1 && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Staff ID"
                  value={formData.staff}
                  onChange={(e) => setFormData({ ...formData, staff: e.target.value })}
                />
              </Grid>
            )}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                InputLabelProps={{ shrink: true }}
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
                  <MenuItem value="PRESENT">Present</MenuItem>
                  <MenuItem value="ABSENT">Absent</MenuItem>
                  <MenuItem value="LATE">Late</MenuItem>
                  <MenuItem value="EXCUSED">Excused</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Check In Time"
                type="time"
                value={formData.check_in_time}
                onChange={(e) => setFormData({ ...formData, check_in_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Check Out Time"
                type="time"
                value={formData.check_out_time}
                onChange={(e) => setFormData({ ...formData, check_out_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={2}
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
            {selectedRecord ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Attendance Record"
        message="Are you sure you want to delete this attendance record? This action cannot be undone."
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Attendance
