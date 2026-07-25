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
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Person as PersonIcon,
  Edit as EditIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

const emptyForm = {
  first_name: '',
  last_name: '',
  email: '',
  admission_number: '',
  school: '',
  class_name: '',
  date_of_birth: '',
  gender: 'M',
  blood_group: '',
  nationality: 'Nigerian',
  state_of_origin: '',
  lga_of_origin: '',
  residential_address: '',
  parent_name: '',
  parent_phone: '',
  parent_email: '',
  parent_occupation: '',
  parent_address: '',
  guardian_name: '',
  guardian_phone: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  medical_conditions: '',
  allergies: '',
  previous_school: '',
  admission_date: '',
  status: 'ACTIVE',
  is_boarding: false,
  bus_route: '',
}

function Students() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [schools, setSchools] = useState([])
  const [classes, setClasses] = useState([])

  // Dialogs
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [formData, setFormData] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [formTab, setFormTab] = useState(0)
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [filters, setFilters] = useState({
    school: '',
    class_name: '',
    status: '',
    gender: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchStudents()
    fetchSchools()
    fetchClasses()
  }, [])

  useEffect(() => {
    fetchStudents()
  }, [filters])

  const fetchStudents = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.school) params.append('school', filters.school)
      if (filters.class_name) params.append('class_name', filters.class_name)
      if (filters.status) params.append('status', filters.status)
      if (filters.gender) params.append('gender', filters.gender)
      const query = params.toString()
      const url = `/students/students/${query ? `?${query}` : ''}`
      const response = await api.get(url)
      setStudents(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load students')
    } finally {
      setLoading(false)
    }
  }

  const fetchSchools = async () => {
    try {
      const response = await api.get('/schools/schools/')
      setSchools(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const fetchClasses = async () => {
    try {
      const response = await api.get('/academics/classes/')
      setClasses(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    setFilters({ school: '', class_name: '', status: '', gender: '' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedStudent(null)
    setFormData(emptyForm)
    setFormErrors({})
    setFormTab(0)
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (student) => {
    setSelectedStudent(student)
    setFormData({
      first_name: student.user?.first_name || '',
      last_name: student.user?.last_name || '',
      email: student.user?.email || '',
      admission_number: student.admission_number || '',
      school: student.school || '',
      class_name: student.class_name || '',
      date_of_birth: student.date_of_birth || '',
      gender: student.gender || 'M',
      blood_group: student.blood_group || '',
      nationality: student.nationality || 'Nigerian',
      state_of_origin: student.state_of_origin || '',
      lga_of_origin: student.lga_of_origin || '',
      residential_address: student.residential_address || '',
      parent_name: student.parent_name || '',
      parent_phone: student.parent_phone || '',
      parent_email: student.parent_email || '',
      parent_occupation: student.parent_occupation || '',
      parent_address: student.parent_address || '',
      guardian_name: student.guardian_name || '',
      guardian_phone: student.guardian_phone || '',
      emergency_contact_name: student.emergency_contact_name || '',
      emergency_contact_phone: student.emergency_contact_phone || '',
      medical_conditions: student.medical_conditions || '',
      allergies: student.allergies || '',
      previous_school: student.previous_school || '',
      admission_date: student.admission_date || '',
      status: student.status || 'ACTIVE',
      is_boarding: student.is_boarding || false,
      bus_route: student.bus_route || '',
    })
    setFormErrors({})
    setFormTab(0)
    setOpenFormDialog(true)
  }

  const handleOpenView = (student) => {
    setSelectedStudent(student)
    setOpenViewDialog(true)
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.first_name.trim()) errors.first_name = 'First name is required'
    if (!formData.last_name.trim()) errors.last_name = 'Last name is required'
    if (!formData.admission_number.trim()) errors.admission_number = 'Admission number is required'
    if (!formData.school) errors.school = 'School is required'
    if (!formData.date_of_birth) errors.date_of_birth = 'Date of birth is required'
    if (!formData.state_of_origin.trim()) errors.state_of_origin = 'State of origin is required'
    if (!formData.lga_of_origin.trim()) errors.lga_of_origin = 'LGA of origin is required'
    if (!formData.residential_address.trim()) errors.residential_address = 'Address is required'
    if (!formData.parent_name.trim()) errors.parent_name = 'Parent name is required'
    if (!formData.parent_phone.trim()) errors.parent_phone = 'Parent phone is required'
    if (!formData.emergency_contact_name.trim()) errors.emergency_contact_name = 'Emergency contact is required'
    if (!formData.emergency_contact_phone.trim()) errors.emergency_contact_phone = 'Emergency phone is required'
    if (!formData.admission_date) errors.admission_date = 'Admission date is required'
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
      const payload = {
        admission_number: formData.admission_number,
        school: formData.school,
        class_name: formData.class_name || null,
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        blood_group: formData.blood_group,
        nationality: formData.nationality,
        state_of_origin: formData.state_of_origin,
        lga_of_origin: formData.lga_of_origin,
        residential_address: formData.residential_address,
        parent_name: formData.parent_name,
        parent_phone: formData.parent_phone,
        parent_email: formData.parent_email,
        parent_occupation: formData.parent_occupation,
        parent_address: formData.parent_address,
        guardian_name: formData.guardian_name,
        guardian_phone: formData.guardian_phone,
        emergency_contact_name: formData.emergency_contact_name,
        emergency_contact_phone: formData.emergency_contact_phone,
        medical_conditions: formData.medical_conditions,
        allergies: formData.allergies,
        previous_school: formData.previous_school,
        admission_date: formData.admission_date,
        status: formData.status,
        is_boarding: formData.is_boarding,
        bus_route: formData.bus_route,
      }

      if (selectedStudent) {
        await api.put(`/students/students/${selectedStudent.id}/`, payload)
        notify.success('Student updated successfully')
      } else {
        // For create, we need user data too
        const createPayload = {
          ...payload,
          user_data: {
            first_name: formData.first_name,
            last_name: formData.last_name,
            email: formData.email,
          },
        }
        await api.post('/students/students/', createPayload)
        notify.success('Student created successfully')
      }
      setOpenFormDialog(false)
      setFormErrors({})
      fetchStudents()
    } catch (error) {
      const msg = error.response?.data?.detail || error.response?.data?.message || 'Failed to save student'
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/students/students/${selectedStudent.id}/`)
      notify.success('Student deleted successfully')
      setOpenDeleteDialog(false)
      setSelectedStudent(null)
      fetchStudents()
    } catch (error) {
      notify.error('Failed to delete student')
    }
  }

  const columns = [
    {
      id: 'full_name',
      label: 'Name',
      render: (row) => (
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {row.user?.first_name} {row.user?.last_name}
          </Typography>
          <Typography variant="caption" color="text.secondary">{row.admission_number}</Typography>
        </Box>
      ),
    },
    { id: 'school_name', label: 'School' },
    { id: 'class_name_display', label: 'Class', render: (row) => row.class_name_display || '-' },
    {
      id: 'gender',
      label: 'Gender',
      render: (row) => (
        <Chip label={row.gender === 'M' ? 'Male' : 'Female'} size="small" color={row.gender === 'M' ? 'primary' : 'secondary'} />
      ),
    },
    {
      id: 'status',
      label: 'Status',
      render: (row) => {
        const colors = { ACTIVE: 'success', INACTIVE: 'default', GRADUATED: 'info', TRANSFERRED: 'warning', EXPELLED: 'error', WITHDRAWN: 'default' }
        return <Chip label={row.status} size="small" color={colors[row.status] || 'default'} />
      },
    },
  ]

  if (loading) {
    return <Loading message="Loading students..." />
  }

  const filteredStudents = students
  const maleCount = filteredStudents.filter(s => s.gender === 'M').length
  const femaleCount = filteredStudents.filter(s => s.gender === 'F').length
  const activeCount = filteredStudents.filter(s => s.status === 'ACTIVE').length

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Student Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {filteredStudents.length} student{filteredStudents.length !== 1 ? 's' : ''}
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
            Add Student
          </Button>
        </Stack>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Students</Typography>
            {hasActiveFilters && (
              <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>
                Clear All
              </Button>
            )}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>School</InputLabel>
                <Select
                  value={filters.school}
                  onChange={(e) => handleFilterChange('school', e.target.value)}
                  label="School"
                >
                  <MenuItem value="">All Schools</MenuItem>
                  {schools.map(s => (
                    <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Class</InputLabel>
                <Select
                  value={filters.class_name}
                  onChange={(e) => handleFilterChange('class_name', e.target.value)}
                  label="Class"
                >
                  <MenuItem value="">All Classes</MenuItem>
                  {classes.map(c => (
                    <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
                  <MenuItem value="GRADUATED">Graduated</MenuItem>
                  <MenuItem value="TRANSFERRED">Transferred</MenuItem>
                  <MenuItem value="EXPELLED">Expelled</MenuItem>
                  <MenuItem value="WITHDRAWN">Withdrawn</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Gender</InputLabel>
                <Select
                  value={filters.gender}
                  onChange={(e) => handleFilterChange('gender', e.target.value)}
                  label="Gender"
                >
                  <MenuItem value="">All Genders</MenuItem>
                  <MenuItem value="M">Male</MenuItem>
                  <MenuItem value="F">Female</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Students" value={filteredStudents.length} icon={<PersonIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Male Students" value={maleCount} icon={<PersonIcon />} color="#1976d2" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Female Students" value={femaleCount} icon={<PersonIcon />} color="#e91e63" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Students" value={activeCount} icon={<PersonIcon />} color="#388e3c" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filteredStudents}
        onView={handleOpenView}
        onEdit={handleOpenEdit}
        onDelete={(s) => { setSelectedStudent(s); setOpenDeleteDialog(true); }}
      />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {selectedStudent ? 'Edit Student' : 'Add New Student'}
        </DialogTitle>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={formTab} onChange={(_, v) => setFormTab(v)} sx={{ px: 2 }}>
            <Tab label="Personal" />
            <Tab label="School" />
            <Tab label="Contact" />
            <Tab label="Emergency & Medical" />
          </Tabs>
        </Box>
        <DialogContent sx={{ minHeight: 350 }}>
          {/* Tab 0: Personal */}
          {formTab === 0 && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="First Name *"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  error={!!formErrors.first_name} helperText={formErrors.first_name}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Last Name *"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  error={!!formErrors.last_name} helperText={formErrors.last_name}
                />
              </Grid>
              {!selectedStudent && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth size="small" label="Email" type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Date of Birth *" type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  error={!!formErrors.date_of_birth} helperText={formErrors.date_of_birth}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Gender</InputLabel>
                  <Select value={formData.gender} onChange={(e) => setFormData({ ...formData, gender: e.target.value })} label="Gender">
                    <MenuItem value="M">Male</MenuItem>
                    <MenuItem value="F">Female</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Blood Group"
                  value={formData.blood_group}
                  onChange={(e) => setFormData({ ...formData, blood_group: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Nationality"
                  value={formData.nationality}
                  onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="State of Origin *"
                  value={formData.state_of_origin}
                  onChange={(e) => setFormData({ ...formData, state_of_origin: e.target.value })}
                  error={!!formErrors.state_of_origin} helperText={formErrors.state_of_origin}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="LGA of Origin *"
                  value={formData.lga_of_origin}
                  onChange={(e) => setFormData({ ...formData, lga_of_origin: e.target.value })}
                  error={!!formErrors.lga_of_origin} helperText={formErrors.lga_of_origin}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth size="small" label="Residential Address *" multiline rows={2}
                  value={formData.residential_address}
                  onChange={(e) => setFormData({ ...formData, residential_address: e.target.value })}
                  error={!!formErrors.residential_address} helperText={formErrors.residential_address}
                />
              </Grid>
            </Grid>
          )}

          {/* Tab 1: School */}
          {formTab === 1 && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Admission Number *"
                  value={formData.admission_number}
                  onChange={(e) => setFormData({ ...formData, admission_number: e.target.value })}
                  error={!!formErrors.admission_number} helperText={formErrors.admission_number}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small" error={!!formErrors.school}>
                  <InputLabel>School *</InputLabel>
                  <Select
                    value={formData.school}
                    onChange={(e) => setFormData({ ...formData, school: e.target.value })}
                    label="School *"
                  >
                    {schools.map(s => (
                      <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                    ))}
                  </Select>
                  {formErrors.school && <Typography variant="caption" color="error">{formErrors.school}</Typography>}
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Class</InputLabel>
                  <Select
                    value={formData.class_name}
                    onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                    label="Class"
                  >
                    <MenuItem value="">None</MenuItem>
                    {classes.map(c => (
                      <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Admission Date *" type="date"
                  value={formData.admission_date}
                  onChange={(e) => setFormData({ ...formData, admission_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  error={!!formErrors.admission_date} helperText={formErrors.admission_date}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    label="Status"
                  >
                    <MenuItem value="ACTIVE">Active</MenuItem>
                    <MenuItem value="INACTIVE">Inactive</MenuItem>
                    <MenuItem value="GRADUATED">Graduated</MenuItem>
                    <MenuItem value="TRANSFERRED">Transferred</MenuItem>
                    <MenuItem value="EXPELLED">Expelled</MenuItem>
                    <MenuItem value="WITHDRAWN">Withdrawn</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_boarding}
                      onChange={(e) => setFormData({ ...formData, is_boarding: e.target.checked })}
                    />
                  }
                  label="Boarding Student"
                />
              </Grid>
              {formData.is_boarding && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth size="small" label="Bus Route"
                    value={formData.bus_route}
                    onChange={(e) => setFormData({ ...formData, bus_route: e.target.value })}
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Previous School"
                  value={formData.previous_school}
                  onChange={(e) => setFormData({ ...formData, previous_school: e.target.value })}
                />
              </Grid>
            </Grid>
          )}

          {/* Tab 2: Contact */}
          {formTab === 2 && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Parent/Guardian Name *"
                  value={formData.parent_name}
                  onChange={(e) => setFormData({ ...formData, parent_name: e.target.value })}
                  error={!!formErrors.parent_name} helperText={formErrors.parent_name}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Parent Phone *"
                  value={formData.parent_phone}
                  onChange={(e) => setFormData({ ...formData, parent_phone: e.target.value })}
                  error={!!formErrors.parent_phone} helperText={formErrors.parent_phone}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Parent Email" type="email"
                  value={formData.parent_email}
                  onChange={(e) => setFormData({ ...formData, parent_email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Parent Occupation"
                  value={formData.parent_occupation}
                  onChange={(e) => setFormData({ ...formData, parent_occupation: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth size="small" label="Parent Address" multiline rows={2}
                  value={formData.parent_address}
                  onChange={(e) => setFormData({ ...formData, parent_address: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>Guardian (if different)</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Guardian Name"
                  value={formData.guardian_name}
                  onChange={(e) => setFormData({ ...formData, guardian_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Guardian Phone"
                  value={formData.guardian_phone}
                  onChange={(e) => setFormData({ ...formData, guardian_phone: e.target.value })}
                />
              </Grid>
            </Grid>
          )}

          {/* Tab 3: Emergency & Medical */}
          {formTab === 3 && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Emergency Contact Name *"
                  value={formData.emergency_contact_name}
                  onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })}
                  error={!!formErrors.emergency_contact_name} helperText={formErrors.emergency_contact_name}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth size="small" label="Emergency Contact Phone *"
                  value={formData.emergency_contact_phone}
                  onChange={(e) => setFormData({ ...formData, emergency_contact_phone: e.target.value })}
                  error={!!formErrors.emergency_contact_phone} helperText={formErrors.emergency_contact_phone}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth size="small" label="Medical Conditions" multiline rows={2}
                  value={formData.medical_conditions}
                  onChange={(e) => setFormData({ ...formData, medical_conditions: e.target.value })}
                  placeholder="e.g. Asthma, Diabetes..."
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth size="small" label="Allergies" multiline rows={2}
                  value={formData.allergies}
                  onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                  placeholder="e.g. Peanuts, Penicillin..."
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          {formTab > 0 && (
            <Button onClick={() => setFormTab(formTab - 1)}>Back</Button>
          )}
          {formTab < 3 ? (
            <Button variant="contained" onClick={() => setFormTab(formTab + 1)} sx={{ bgcolor: '#1a237e' }}>
              Next
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting}
              sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
            >
              {submitting ? 'Saving...' : selectedStudent ? 'Update Student' : 'Create Student'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Student Details
          {selectedStudent && (
            <Chip
              label={selectedStudent.status}
              size="small"
              sx={{ ml: 1, bgcolor: selectedStudent.status === 'ACTIVE' ? '#E8F5E9' : '#FFF3E0', color: selectedStudent.status === 'ACTIVE' ? '#2E7D32' : '#E65100' }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedStudent && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              {/* Personal Info */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Personal Information</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Full Name</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.user?.first_name} {selectedStudent.user?.last_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Admission Number</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.admission_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.date_of_birth}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Gender</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.gender === 'M' ? 'Male' : 'Female'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Blood Group</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.blood_group || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Nationality</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.nationality || '-'}</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              {/* School Info */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>School Information</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">School</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.school_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Class</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.class_name_display || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Admission Date</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.admission_date}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Boarding</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.is_boarding ? 'Yes' : 'No'}</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              {/* Parent/Guardian Info */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Parent / Guardian</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Parent Name</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.parent_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Parent Phone</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.parent_phone}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Parent Email</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.parent_email || '-'}</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              {/* Emergency */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Emergency Contact</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Contact Name</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.emergency_contact_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Contact Phone</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.emergency_contact_phone}</Typography>
              </Grid>
              {selectedStudent.medical_conditions && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">Medical Conditions</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.medical_conditions}</Typography>
                </Grid>
              )}
              {selectedStudent.allergies && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">Allergies</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStudent.allergies}</Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          {selectedStudent && (
            <Button
              variant="contained"
              startIcon={<EditIcon />}
              onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedStudent) }}
              sx={{ bgcolor: '#1a237e' }}
            >
              Edit
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Student"
        message={`Are you sure you want to delete ${selectedStudent?.user?.first_name} ${selectedStudent?.user?.last_name}? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Students
