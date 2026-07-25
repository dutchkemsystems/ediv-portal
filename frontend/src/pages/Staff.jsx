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
  Divider,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Stack,
} from '@mui/material'
import {
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
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
  phone_number: '',
  category: 'TEACHING',
  designation: 'TEACHER',
  employment_type: 'PERMANENT',
  qualification: 'Bachelors',
  date_of_birth: '',
  gender: 'M',
  marital_status: 'SINGLE',
  state_of_origin: '',
  lga_of_origin: '',
  residential_address: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  bank_name: '',
  bank_account_number: '',
  bank_account_name: '',
  date_joined: '',
  school: '',
  department: '',
  pension_pin: '',
  tax_id: '',
  grade_level: '',
  step: 1,
  salary: 0,
}

const steps = ['Personal Info', 'Employment Details', 'Financial & Contact']

function Staff() {
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [schools, setSchools] = useState([])
  const [departments, setDepartments] = useState([])
  const [currentUser, setCurrentUser] = useState(null)

  // Dialogs
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedStaff, setSelectedStaff] = useState(null)
  const [formData, setFormData] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [activeStep, setActiveStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [createdStaff, setCreatedStaff] = useState(null)

  // Filters
  const [filters, setFilters] = useState({
    category: '',
    designation: '',
    school: '',
    employment_type: '',
    is_active: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  const canManageStaff = ['SYSADMIN', 'TG_PS', 'PRI', 'VP'].includes(currentUser?.role)

  useEffect(() => {
    fetchStaff()
    fetchCurrentUser()
    fetchSchools()
    fetchDepartments()
  }, [])

  useEffect(() => {
    fetchStaff()
  }, [filters])

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/users/users/me/')
      setCurrentUser(response.data)
    } catch (error) {
      // silent
    }
  }

  const fetchStaff = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.category) params.append('category', filters.category)
      if (filters.designation) params.append('designation', filters.designation)
      if (filters.school) params.append('school', filters.school)
      if (filters.employment_type) params.append('employment_type', filters.employment_type)
      if (filters.is_active) params.append('is_active', filters.is_active)
      const query = params.toString()
      const url = `/staff/staff/${query ? `?${query}` : ''}`
      const response = await api.get(url)
      setStaff(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load staff')
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

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/departments/departments/')
      setDepartments(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    setFilters({ category: '', designation: '', school: '', employment_type: '', is_active: '' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedStaff(null)
    setFormData(emptyForm)
    setFormErrors({})
    setActiveStep(0)
    setCreatedStaff(null)
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (staffMember) => {
    setSelectedStaff(staffMember)
    setFormData({
      first_name: staffMember.user?.first_name || '',
      last_name: staffMember.user?.last_name || '',
      email: staffMember.user?.email || '',
      phone_number: staffMember.user?.phone_number || '',
      category: staffMember.category || 'TEACHING',
      designation: staffMember.designation || 'TEACHER',
      employment_type: staffMember.employment_type || 'PERMANENT',
      qualification: staffMember.qualification || 'Bachelors',
      date_of_birth: staffMember.date_of_birth || '',
      gender: staffMember.gender || 'M',
      marital_status: staffMember.marital_status || 'SINGLE',
      state_of_origin: staffMember.state_of_origin || '',
      lga_of_origin: staffMember.lga_of_origin || '',
      residential_address: staffMember.residential_address || '',
      emergency_contact_name: staffMember.emergency_contact_name || '',
      emergency_contact_phone: staffMember.emergency_contact_phone || '',
      bank_name: staffMember.bank_name || '',
      bank_account_number: staffMember.bank_account_number || '',
      bank_account_name: staffMember.bank_account_name || '',
      date_joined: staffMember.date_joined || '',
      school: staffMember.school || '',
      department: staffMember.department || '',
      pension_pin: staffMember.pension_pin || '',
      tax_id: staffMember.tax_id || '',
      grade_level: staffMember.grade_level || '',
      step: staffMember.step || 1,
      salary: staffMember.salary || 0,
    })
    setFormErrors({})
    setActiveStep(0)
    setCreatedStaff(null)
    setOpenFormDialog(true)
  }

  const handleOpenView = (staffMember) => {
    setSelectedStaff(staffMember)
    setOpenViewDialog(true)
  }

  const handleDialogClose = () => {
    setOpenFormDialog(false)
    setCreatedStaff(null)
    setFormData(emptyForm)
    setActiveStep(0)
    setSelectedStaff(null)
  }

  const isStepValid = (step) => {
    const f = formData
    if (step === 0) {
      return f.first_name && f.last_name && f.date_of_birth && f.gender && f.state_of_origin && f.lga_of_origin && f.residential_address
    }
    if (step === 1) {
      return f.category && f.designation && f.employment_type && f.qualification && f.date_joined
    }
    if (step === 2) {
      return f.emergency_contact_name && f.emergency_contact_phone && f.bank_name && f.bank_account_number && f.bank_account_name
    }
    return true
  }

  const handleSubmit = async () => {
    if (!isStepValid(activeStep)) {
      notify.warning('Please fill in all required fields')
      return
    }
    setSubmitting(true)
    try {
      if (selectedStaff) {
        // Edit mode - use PUT
        const payload = {
          admission_number: selectedStaff.admission_number,
          ...formData,
          school: formData.school || null,
          department: formData.department || null,
        }
        await api.put(`/staff/staff/${selectedStaff.id}/`, payload)
        notify.success('Staff updated successfully')
        setOpenFormDialog(false)
        setSelectedStaff(null)
        fetchStaff()
      } else {
        // Create mode
        const response = await api.post('/users/users/create-staff/', formData)
        setCreatedStaff(response.data)
        notify.success('Staff account created successfully')
        fetchStaff()
      }
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save staff'
      if (data) {
        if (data.error) msg = data.error
        else if (typeof data === 'object') {
          const firstKey = Object.keys(data)[0]
          if (firstKey) {
            const val = data[firstKey]
            msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`
          }
        }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/staff/staff/${selectedStaff.id}/`)
      notify.success('Staff deleted successfully')
      setOpenDeleteDialog(false)
      setSelectedStaff(null)
      fetchStaff()
    } catch (error) {
      notify.error('Failed to delete staff')
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
          <Typography variant="caption" color="text.secondary">{row.staff_id}</Typography>
        </Box>
      ),
    },
    { id: 'employee_number', label: 'Employee No.' },
    {
      id: 'category',
      label: 'Category',
      render: (row) => {
        const colors = { TEACHING: 'primary', NON_TEACHING: 'warning', ADMINISTRATIVE: 'info' }
        return <Chip label={row.category?.replace('_', ' ')} size="small" color={colors[row.category] || 'default'} />
      },
    },
    { id: 'designation', label: 'Designation', render: (row) => row.designation?.replace('_', ' ') || '-' },
    { id: 'school_name', label: 'School', render: (row) => row.school_name || 'Head Office' },
    {
      id: 'is_active',
      label: 'Status',
      render: (row) => (
        <Chip label={row.is_active ? 'Active' : 'Inactive'} size="small" color={row.is_active ? 'success' : 'default'} />
      ),
    },
  ]

  if (loading) {
    return <Loading message="Loading staff..." />
  }

  const filteredStaff = staff
  const teachingCount = filteredStaff.filter(s => s.category === 'TEACHING').length
  const nonTeachingCount = filteredStaff.filter(s => s.category === 'NON_TEACHING').length
  const activeCount = filteredStaff.filter(s => s.is_active).length
  const adminCount = filteredStaff.filter(s => s.category === 'ADMINISTRATIVE').length

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Staff Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {filteredStaff.length} staff member{filteredStaff.length !== 1 ? 's' : ''}
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
          {canManageStaff && (
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={handleOpenCreate}
              sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}
            >
              Add Staff
            </Button>
          )}
        </Stack>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Staff</Typography>
            {hasActiveFilters && (
              <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>
                Clear All
              </Button>
            )}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={2.4}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  <MenuItem value="TEACHING">Teaching</MenuItem>
                  <MenuItem value="NON_TEACHING">Non-Teaching</MenuItem>
                  <MenuItem value="ADMINISTRATIVE">Administrative</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FormControl fullWidth size="small">
                <InputLabel>Designation</InputLabel>
                <Select
                  value={filters.designation}
                  onChange={(e) => handleFilterChange('designation', e.target.value)}
                  label="Designation"
                >
                  <MenuItem value="">All Designations</MenuItem>
                  <MenuItem value="PRINCIPAL">Principal</MenuItem>
                  <MenuItem value="VICE_PRINCIPAL">Vice Principal</MenuItem>
                  <MenuItem value="HEAD_TEACHER">Head Teacher</MenuItem>
                  <MenuItem value="SENIOR_TEACHER">Senior Teacher</MenuItem>
                  <MenuItem value="TEACHER">Teacher</MenuItem>
                  <MenuItem value="LIBRARIAN">Librarian</MenuItem>
                  <MenuItem value="BURSAR">Bursar</MenuItem>
                  <MenuItem value="SECRETARY">Secretary</MenuItem>
                  <MenuItem value="CLERK">Clerk</MenuItem>
                  <MenuItem value="SECURITY">Security</MenuItem>
                  <MenuItem value="CLEANER">Cleaner</MenuItem>
                  <MenuItem value="DRIVER">Driver</MenuItem>
                  <MenuItem value="TECHNICIAN">Technician</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
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
            <Grid item xs={12} sm={6} md={2.4}>
              <FormControl fullWidth size="small">
                <InputLabel>Employment Type</InputLabel>
                <Select
                  value={filters.employment_type}
                  onChange={(e) => handleFilterChange('employment_type', e.target.value)}
                  label="Employment Type"
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="PERMANENT">Permanent</MenuItem>
                  <MenuItem value="CONTRACT">Contract</MenuItem>
                  <MenuItem value="TEMPORARY">Temporary</MenuItem>
                  <MenuItem value="VOLUNTEER">Volunteer</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.is_active}
                  onChange={(e) => handleFilterChange('is_active', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="true">Active</MenuItem>
                  <MenuItem value="false">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Staff" value={filteredStaff.length} icon={<PeopleIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Teaching" value={teachingCount} icon={<PeopleIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Non-Teaching" value={nonTeachingCount + adminCount} icon={<PeopleIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Staff" value={activeCount} icon={<PeopleIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filteredStaff}
        onView={handleOpenView}
        onEdit={canManageStaff ? handleOpenEdit : undefined}
        onDelete={canManageStaff ? (s) => { setSelectedStaff(s); setOpenDeleteDialog(true); } : undefined}
      />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600 }}>
          {selectedStaff ? (
            <><EditIcon /> Edit Staff Member</>
          ) : (
            <><PersonAddIcon /> Add Staff Member</>
          )}
        </DialogTitle>
        <DialogContent>
          {createdStaff ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">Staff Account Created</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Name:</strong> {createdStaff.user.first_name} {createdStaff.user.last_name}<br />
                <strong>Email:</strong> {createdStaff.user.email}<br />
                <strong>Role:</strong> {createdStaff.user.role}<br />
                <strong>Staff ID:</strong> {createdStaff.staff.staff_id}<br />
                <strong>Employee No:</strong> {createdStaff.staff.employee_number}<br />
                <strong>Category:</strong> {createdStaff.staff.category}<br />
                <strong>Designation:</strong> {createdStaff.staff.designation}<br />
                <strong>School:</strong> {createdStaff.staff.school}<br />
                <strong>Temporary Password:</strong> <code>{createdStaff.user.temp_password}</code><br /><br />
                Please share these credentials securely. The staff member should change their password on first login.
              </Typography>
            </Alert>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              {/* Step 0: Personal Info */}
              {activeStep === 0 && (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="First Name"
                      value={formData.first_name}
                      onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                      error={!!formErrors.first_name} helperText={formErrors.first_name} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="Last Name"
                      value={formData.last_name}
                      onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                      error={!!formErrors.last_name} helperText={formErrors.last_name} />
                  </Grid>
                  {!selectedStaff && (
                    <Grid item xs={12} sm={6}>
                      <TextField fullWidth size="small" required label="Email" type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                    </Grid>
                  )}
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Phone Number"
                      value={formData.phone_number}
                      onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="Date of Birth" type="date"
                      InputLabelProps={{ shrink: true }}
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small" required>
                      <InputLabel>Gender</InputLabel>
                      <Select value={formData.gender} label="Gender"
                        onChange={(e) => setFormData({ ...formData, gender: e.target.value })}>
                        <MenuItem value="M">Male</MenuItem>
                        <MenuItem value="F">Female</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Marital Status</InputLabel>
                      <Select value={formData.marital_status} label="Marital Status"
                        onChange={(e) => setFormData({ ...formData, marital_status: e.target.value })}>
                        <MenuItem value="SINGLE">Single</MenuItem>
                        <MenuItem value="MARRIED">Married</MenuItem>
                        <MenuItem value="DIVORCED">Divorced</MenuItem>
                        <MenuItem value="WIDOWED">Widowed</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="State of Origin"
                      value={formData.state_of_origin}
                      onChange={(e) => setFormData({ ...formData, state_of_origin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="LGA of Origin"
                      value={formData.lga_of_origin}
                      onChange={(e) => setFormData({ ...formData, lga_of_origin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField fullWidth size="small" required label="Residential Address" multiline rows={2}
                      value={formData.residential_address}
                      onChange={(e) => setFormData({ ...formData, residential_address: e.target.value })} />
                  </Grid>
                </Grid>
              )}

              {/* Step 1: Employment Details */}
              {activeStep === 1 && (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small" required>
                      <InputLabel>Category</InputLabel>
                      <Select value={formData.category} label="Category"
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}>
                        <MenuItem value="TEACHING">Teaching Staff</MenuItem>
                        <MenuItem value="NON_TEACHING">Non-Teaching Staff</MenuItem>
                        <MenuItem value="ADMINISTRATIVE">Administrative Staff</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small" required>
                      <InputLabel>Designation</InputLabel>
                      <Select value={formData.designation} label="Designation"
                        onChange={(e) => setFormData({ ...formData, designation: e.target.value })}>
                        <MenuItem value="PRINCIPAL">Principal</MenuItem>
                        <MenuItem value="VICE_PRINCIPAL">Vice Principal</MenuItem>
                        <MenuItem value="HEAD_TEACHER">Head Teacher</MenuItem>
                        <MenuItem value="SENIOR_TEACHER">Senior Teacher</MenuItem>
                        <MenuItem value="TEACHER">Teacher</MenuItem>
                        <MenuItem value="LIBRARIAN">Librarian</MenuItem>
                        <MenuItem value="LABORATORY_ATTENDANT">Laboratory Attendant</MenuItem>
                        <MenuItem value="BURSAR">Bursar</MenuItem>
                        <MenuItem value="SECRETARY">Secretary</MenuItem>
                        <MenuItem value="CLERK">Clerk</MenuItem>
                        <MenuItem value="GARDENER">Gardener</MenuItem>
                        <MenuItem value="SECURITY">Security</MenuItem>
                        <MenuItem value="CLEANER">Cleaner</MenuItem>
                        <MenuItem value="DRIVER">Driver</MenuItem>
                        <MenuItem value="TECHNICIAN">Technician</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small" required>
                      <InputLabel>Employment Type</InputLabel>
                      <Select value={formData.employment_type} label="Employment Type"
                        onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}>
                        <MenuItem value="PERMANENT">Permanent</MenuItem>
                        <MenuItem value="CONTRACT">Contract</MenuItem>
                        <MenuItem value="TEMPORARY">Temporary</MenuItem>
                        <MenuItem value="VOLUNTEER">Volunteer</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small" required>
                      <InputLabel>Qualification</InputLabel>
                      <Select value={formData.qualification} label="Qualification"
                        onChange={(e) => setFormData({ ...formData, qualification: e.target.value })}>
                        <MenuItem value="PhD">Doctorate</MenuItem>
                        <MenuItem value="Masters">Masters Degree</MenuItem>
                        <MenuItem value="Bachelors">Bachelors Degree</MenuItem>
                        <MenuItem value="HND">Higher National Diploma</MenuItem>
                        <MenuItem value="OND">Ordinary National Diploma</MenuItem>
                        <MenuItem value="NCE">Nigeria Certificate in Education</MenuItem>
                        <MenuItem value="SSCE">Senior School Certificate</MenuItem>
                        <MenuItem value="OTHER">Other</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="Date Joined" type="date"
                      InputLabelProps={{ shrink: true }}
                      value={formData.date_joined}
                      onChange={(e) => setFormData({ ...formData, date_joined: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>School</InputLabel>
                      <Select value={formData.school} label="School"
                        onChange={(e) => setFormData({ ...formData, school: e.target.value })}>
                        <MenuItem value="">None (Head Office)</MenuItem>
                        {schools.map(s => (
                          <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Department</InputLabel>
                      <Select value={formData.department} label="Department"
                        onChange={(e) => setFormData({ ...formData, department: e.target.value })}>
                        <MenuItem value="">None</MenuItem>
                        {departments.map(d => (
                          <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Grade Level"
                      value={formData.grade_level}
                      onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Step" type="number"
                      value={formData.step}
                      onChange={(e) => setFormData({ ...formData, step: parseInt(e.target.value) || 1 })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Salary" type="number"
                      value={formData.salary}
                      onChange={(e) => setFormData({ ...formData, salary: parseFloat(e.target.value) || 0 })} />
                  </Grid>
                </Grid>
              )}

              {/* Step 2: Financial & Contact */}
              {activeStep === 2 && (
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Emergency Contact</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="Emergency Contact Name"
                      value={formData.emergency_contact_name}
                      onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" required label="Emergency Contact Phone"
                      value={formData.emergency_contact_phone}
                      onChange={(e) => setFormData({ ...formData, emergency_contact_phone: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1, mt: 1 }}>Bank Details</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth size="small" required label="Bank Name"
                      value={formData.bank_name}
                      onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth size="small" required label="Account Number"
                      value={formData.bank_account_number}
                      onChange={(e) => setFormData({ ...formData, bank_account_number: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth size="small" required label="Account Name"
                      value={formData.bank_account_name}
                      onChange={(e) => setFormData({ ...formData, bank_account_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1, mt: 1 }}>Other (Optional)</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Pension PIN"
                      value={formData.pension_pin}
                      onChange={(e) => setFormData({ ...formData, pension_pin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth size="small" label="Tax ID"
                      value={formData.tax_id}
                      onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })} />
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={handleDialogClose}>
            {createdStaff ? 'Close' : 'Cancel'}
          </Button>
          {!createdStaff && (
            <>
              {activeStep > 0 && (
                <Button onClick={() => setActiveStep(activeStep - 1)}>Back</Button>
              )}
              {activeStep < steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(activeStep + 1)}
                  disabled={!isStepValid(activeStep)}
                >
                  Next
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={submitting}
                  sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}
                >
                  {submitting ? 'Saving...' : selectedStaff ? 'Update Staff' : 'Create Staff Account'}
                </Button>
              )}
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Staff Details
          {selectedStaff && (
            <Chip
              label={selectedStaff.is_active ? 'Active' : 'Inactive'}
              size="small"
              sx={{ ml: 1, bgcolor: selectedStaff.is_active ? '#E8F5E9' : '#FFF3E0', color: selectedStaff.is_active ? '#2E7D32' : '#E65100' }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedStaff && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              {/* Personal Info */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Personal Information</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Full Name</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.user?.first_name} {selectedStaff.user?.last_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Staff ID</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.staff_id}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Employee Number</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.employee_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.date_of_birth}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Gender</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.gender === 'M' ? 'Male' : 'Female'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Marital Status</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.marital_status || '-'}</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              {/* Employment Info */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Employment Information</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Category</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.category?.replace('_', ' ')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Designation</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.designation?.replace('_', ' ')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Employment Type</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.employment_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Qualification</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.qualification}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Date Joined</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.date_joined}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">School</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.school_name || 'Head Office'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Grade Level</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.grade_level || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Step</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.step || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Years of Service</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.years_of_service || 0} years</Typography>
              </Grid>

              <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

              {/* Contact & Bank */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Contact & Bank Details</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Emergency Contact</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.emergency_contact_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Emergency Phone</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.emergency_contact_phone}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Bank</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.bank_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Account Number</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.bank_account_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Account Name</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedStaff.bank_account_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">Salary</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>₦{Number(selectedStaff.salary || 0).toLocaleString()}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          {canManageStaff && selectedStaff && (
            <Button
              variant="contained"
              startIcon={<EditIcon />}
              onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedStaff) }}
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
        title="Delete Staff"
        message={`Are you sure you want to delete ${selectedStaff?.user?.first_name} ${selectedStaff?.user?.last_name}? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Staff
