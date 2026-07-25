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
  Tabs,
  Tab,
  Divider,
  Paper,
  Stack,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  CheckCircle as PresentIcon,
  Cancel as AbsentIcon,
  AccessTime as LateIcon,
  EventNote as AttendanceIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

const emptyStudentForm = {
  student: '',
  date: new Date().toISOString().split('T')[0],
  status: 'PRESENT',
  time_in: '',
  time_out: '',
  remark: '',
}

const emptyStaffForm = {
  staff: '',
  date: new Date().toISOString().split('T')[0],
  status: 'PRESENT',
  time_in: '',
  time_out: '',
  overtime_hours: 0,
  remark: '',
}

function Attendance() {
  const [tab, setTab] = useState(0)
  const [records, setRecords] = useState([])
  const [students, setStudents] = useState([])
  const [staffList, setStaffList] = useState([])
  const [loading, setLoading] = useState(true)

  // Dialogs
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [formData, setFormData] = useState(emptyStudentForm)
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [filters, setFilters] = useState({
    date: '',
    status: '',
    student: '',
    staff: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchRecords()
    fetchStudents()
    fetchStaff()
  }, [])

  useEffect(() => {
    fetchRecords()
  }, [tab, filters])

  const fetchRecords = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.date) params.append('date', filters.date)
      if (filters.status) params.append('status', filters.status)
      if (tab === 0 && filters.student) params.append('student', filters.student)
      if (tab === 1 && filters.staff) params.append('staff', filters.staff)
      const query = params.toString()
      const endpoint = tab === 0 ? '/attendance/student-attendance/' : '/attendance/staff-attendance/'
      const response = await api.get(`${endpoint}${query ? `?${query}` : ''}`)
      setRecords(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load attendance records')
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async () => {
    try {
      const response = await api.get('/students/students/')
      setStudents(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const fetchStaff = async () => {
    try {
      const response = await api.get('/staff/staff/')
      setStaffList(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    setFilters({ date: '', status: '', student: '', staff: '' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedRecord(null)
    setFormData(tab === 0 ? { ...emptyStudentForm, date: new Date().toISOString().split('T')[0] } : { ...emptyStaffForm, date: new Date().toISOString().split('T')[0] })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (record) => {
    setSelectedRecord(record)
    if (tab === 0) {
      setFormData({
        student: record.student || '',
        date: record.date || '',
        status: record.status || 'PRESENT',
        time_in: record.time_in || '',
        time_out: record.time_out || '',
        remark: record.remark || '',
      })
    } else {
      setFormData({
        staff: record.staff || '',
        date: record.date || '',
        status: record.status || 'PRESENT',
        time_in: record.time_in || '',
        time_out: record.time_out || '',
        overtime_hours: record.overtime_hours || 0,
        remark: record.remark || '',
      })
    }
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (record) => {
    setSelectedRecord(record)
    setOpenViewDialog(true)
  }

  const validateForm = () => {
    const errors = {}
    if (tab === 0 && !formData.student) errors.student = 'Student is required'
    if (tab === 1 && !formData.staff) errors.staff = 'Staff member is required'
    if (!formData.date) errors.date = 'Date is required'
    if (!formData.status) errors.status = 'Status is required'
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      notify.warning('Please fill in all required fields')
      return
    }
    setSubmitting(true)
    try {
      const endpoint = tab === 0 ? 'student-attendance' : 'staff-attendance'
      const payload = { ...formData }
      if (tab === 1) payload.overtime_hours = parseFloat(formData.overtime_hours) || 0

      if (selectedRecord) {
        await api.put(`/attendance/${endpoint}/${selectedRecord.id}/`, payload)
        notify.success('Attendance record updated')
      } else {
        await api.post(`/attendance/${endpoint}/`, payload)
        notify.success('Attendance record created')
      }
      setOpenFormDialog(false)
      setFormErrors({})
      fetchRecords()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save attendance'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        if (firstKey) {
          const val = data[firstKey]
          msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`
        }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      const endpoint = tab === 0 ? 'student-attendance' : 'staff-attendance'
      await api.delete(`/attendance/${endpoint}/${selectedRecord.id}/`)
      notify.success('Attendance record deleted')
      setOpenDeleteDialog(false)
      setSelectedRecord(null)
      fetchRecords()
    } catch (error) {
      notify.error('Failed to delete attendance record')
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'PRESENT': return 'success'
      case 'ABSENT': return 'error'
      case 'LATE': return 'warning'
      case 'EXCUSED': return 'info'
      case 'ON_LEAVE': return 'default'
      default: return 'default'
    }
  }

  const todayStr = new Date().toISOString().split('T')[0]
  const presentToday = records.filter(r => r.date === todayStr && r.status === 'PRESENT').length
  const absentToday = records.filter(r => r.date === todayStr && r.status === 'ABSENT').length
  const lateToday = records.filter(r => r.date === todayStr && r.status === 'LATE').length
  const excusedToday = records.filter(r => r.date === todayStr && r.status === 'EXCUSED').length

  const studentColumns = [
    {
      id: 'student_name',
      label: 'Student',
      render: (row) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.student_name}</Typography>
      ),
    },
    { id: 'date', label: 'Date' },
    {
      id: 'status',
      label: 'Status',
      render: (row) => <Chip label={row.status} size="small" color={statusColor(row.status)} />,
    },
    { id: 'time_in', label: 'Time In', render: (row) => row.time_in || '-' },
    { id: 'time_out', label: 'Time Out', render: (row) => row.time_out || '-' },
    { id: 'remark', label: 'Remark', render: (row) => row.remark || '-' },
  ]

  const staffColumns = [
    {
      id: 'staff_name',
      label: 'Staff',
      render: (row) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.staff_name}</Typography>
      ),
    },
    { id: 'date', label: 'Date' },
    {
      id: 'status',
      label: 'Status',
      render: (row) => <Chip label={row.status} size="small" color={statusColor(row.status)} />,
    },
    { id: 'time_in', label: 'Time In', render: (row) => row.time_in || '-' },
    { id: 'time_out', label: 'Time Out', render: (row) => row.time_out || '-' },
    { id: 'overtime_hours', label: 'Overtime', render: (row) => row.overtime_hours > 0 ? `${row.overtime_hours}h` : '-' },
    { id: 'remark', label: 'Remark', render: (row) => row.remark || '-' },
  ]

  if (loading) {
    return <Loading message="Loading attendance records..." />
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Attendance Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {records.length} record{records.length !== 1 ? 's' : ''}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
            color={hasActiveFilters ? 'primary' : 'inherit'}
          >
            Filters {hasActiveFilters ? `(${Object.values(filters).filter(v => v).length})` : ''}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Add Record
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 2 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => { setTab(v); setShowFilters(false) }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}
        >
          <Tab label={`Student Attendance (${records.length})`} />
          <Tab label={`Staff Attendance (${records.length})`} />
        </Tabs>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Attendance</Typography>
            {hasActiveFilters && (
              <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>
            )}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth size="small" label="Date" type="date"
                value={filters.date} onChange={(e) => handleFilterChange('date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="PRESENT">Present</MenuItem>
                  <MenuItem value="ABSENT">Absent</MenuItem>
                  <MenuItem value="LATE">Late</MenuItem>
                  <MenuItem value="EXCUSED">Excused</MenuItem>
                  <MenuItem value="ON_LEAVE">On Leave</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {tab === 0 && (
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Student</InputLabel>
                  <Select value={filters.student} onChange={(e) => handleFilterChange('student', e.target.value)} label="Student">
                    <MenuItem value="">All Students</MenuItem>
                    {students.map(s => (
                      <MenuItem key={s.id} value={s.id}>{s.full_name || `${s.user?.first_name} ${s.user?.last_name}`}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
            {tab === 1 && (
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Staff</InputLabel>
                  <Select value={filters.staff} onChange={(e) => handleFilterChange('staff', e.target.value)} label="Staff">
                    <MenuItem value="">All Staff</MenuItem>
                    {staffList.map(s => (
                      <MenuItem key={s.id} value={s.id}>{s.full_name || `${s.user?.first_name} ${s.user?.last_name}`}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Records" value={records.length} icon={<AttendanceIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Present Today" value={presentToday} icon={<PresentIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Absent Today" value={absentToday} icon={<AbsentIcon />} color="#d32f2f" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Late Today" value={lateToday} icon={<LateIcon />} color="#f57c00" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={tab === 0 ? studentColumns : staffColumns}
        data={records}
        onView={handleOpenView}
        onEdit={handleOpenEdit}
        onDelete={(r) => { setSelectedRecord(r); setOpenDeleteDialog(true) }}
      />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {selectedRecord ? 'Edit Attendance' : `Add ${tab === 0 ? 'Student' : 'Staff'} Attendance`}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            {tab === 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small" required error={!!formErrors.student}>
                  <InputLabel>Student *</InputLabel>
                  <Select value={formData.student} onChange={(e) => setFormData({ ...formData, student: e.target.value })} label="Student *">
                    {students.map(s => (
                      <MenuItem key={s.id} value={s.id}>
                        {s.full_name || `${s.user?.first_name} ${s.user?.last_name}`} — {s.admission_number}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.student && <Typography variant="caption" color="error">{formErrors.student}</Typography>}
                </FormControl>
              </Grid>
            )}
            {tab === 1 && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small" required error={!!formErrors.staff}>
                  <InputLabel>Staff Member *</InputLabel>
                  <Select value={formData.staff} onChange={(e) => setFormData({ ...formData, staff: e.target.value })} label="Staff Member *">
                    {staffList.map(s => (
                      <MenuItem key={s.id} value={s.id}>
                        {s.full_name || `${s.user?.first_name} ${s.user?.last_name}`} — {s.staff_id}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.staff && <Typography variant="caption" color="error">{formErrors.staff}</Typography>}
                </FormControl>
              </Grid>
            )}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth size="small" required label="Date" type="date"
                value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                InputLabelProps={{ shrink: true }}
                error={!!formErrors.date} helperText={formErrors.date}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.status}>
                <InputLabel>Status *</InputLabel>
                <Select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} label="Status *">
                  <MenuItem value="PRESENT">Present</MenuItem>
                  <MenuItem value="ABSENT">Absent</MenuItem>
                  <MenuItem value="LATE">Late</MenuItem>
                  <MenuItem value="EXCUSED">Excused</MenuItem>
                  <MenuItem value="ON_LEAVE">On Leave</MenuItem>
                </Select>
                {formErrors.status && <Typography variant="caption" color="error">{formErrors.status}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth size="small" label="Time In" type="time"
                value={formData.time_in} onChange={(e) => setFormData({ ...formData, time_in: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth size="small" label="Time Out" type="time"
                value={formData.time_out} onChange={(e) => setFormData({ ...formData, time_out: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            {tab === 1 && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Overtime Hours" type="number"
                  value={formData.overtime_hours} onChange={(e) => setFormData({ ...formData, overtime_hours: e.target.value })}
                />
              </Grid>
            )}
            <Grid item xs={12}>
              <TextField
                fullWidth size="small" label="Remark" multiline rows={2}
                value={formData.remark} onChange={(e) => setFormData({ ...formData, remark: e.target.value })}
                placeholder="Optional notes about this attendance record"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button
            variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {submitting ? 'Saving...' : selectedRecord ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Attendance Details
          {selectedRecord && (
            <Chip
              label={selectedRecord.status}
              size="small"
              sx={{ ml: 1 }}
              color={statusColor(selectedRecord.status)}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedRecord && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>
                  {tab === 0 ? 'Student' : 'Staff'} Information
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">{tab === 0 ? 'Student Name' : 'Staff Name'}</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {tab === 0 ? selectedRecord.student_name : selectedRecord.staff_name}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Date</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.date}</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Attendance Details</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Status</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.status}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Time In</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.time_in || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Time Out</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.time_out || '-'}</Typography>
              </Grid>
              {tab === 1 && selectedRecord.overtime_hours > 0 && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">Overtime Hours</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.overtime_hours}h</Typography>
                </Grid>
              )}
              {selectedRecord.remark && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">Remark</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.remark}</Typography>
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Recorded By</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedRecord.recorded_by_name || 'System'}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />}
            onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedRecord) }}
            sx={{ bgcolor: '#1a237e' }}>
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Attendance Record"
        message={`Are you sure you want to delete this ${tab === 0 ? 'student' : 'staff'} attendance record? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Attendance
