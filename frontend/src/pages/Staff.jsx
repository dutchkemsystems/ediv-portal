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

const initialStaffForm = {
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
  school_id: '',
  department_id: '',
  pension_pin: '',
  tax_id: '',
  grade_level: '',
  step: 1,
  salary: 0,
}

function Staff() {
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedStaff, setSelectedStaff] = useState(null)

  const [currentUser, setCurrentUser] = useState(null)
  const [openStaffDialog, setOpenStaffDialog] = useState(false)
  const [staffForm, setStaffForm] = useState(initialStaffForm)
  const [createdStaff, setCreatedStaff] = useState(null)
  const [creatingStaff, setCreatingStaff] = useState(false)
  const [activeStep, setActiveStep] = useState(0)

  const canCreateStaff = ['SYSADMIN', 'TG', 'PS', 'PRI', 'VP'].includes(currentUser?.role)

  const steps = ['Personal Info', 'Employment Details', 'Financial & Contact']

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

  const handleCreateStaff = async () => {
    setCreatingStaff(true)
    try {
      const response = await api.post('/users/users/create-staff/', staffForm)
      setCreatedStaff(response.data)
      notify.success('Staff account created successfully')
      fetchStaff()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to create staff'
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
      setCreatingStaff(false)
    }
  }

  const handleDialogClose = () => {
    setOpenStaffDialog(false)
    setCreatedStaff(null)
    setStaffForm(initialStaffForm)
    setActiveStep(0)
  }

  const isStepValid = (step) => {
    const f = staffForm
    if (step === 0) {
      return f.first_name && f.last_name && f.email && f.date_of_birth && f.gender && f.state_of_origin && f.lga_of_origin && f.residential_address
    }
    if (step === 1) {
      return f.category && f.designation && f.employment_type && f.qualification && f.date_joined
    }
    if (step === 2) {
      return f.emergency_contact_name && f.emergency_contact_phone && f.bank_name && f.bank_account_number && f.bank_account_name
    }
    return true
  }

  const columns = [
    { id: 'full_name', label: 'Name', render: (row) => row.user?.first_name + ' ' + row.user?.last_name },
    { id: 'staff_id', label: 'Staff ID' },
    { id: 'employee_number', label: 'Employee No.' },
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category?.replace('_', ' ')} size="small" color={row.category === 'TEACHING' ? 'primary' : 'default'} />
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
        {canCreateStaff && (
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={() => { setCreatedStaff(null); setStaffForm(initialStaffForm); setActiveStep(0); setOpenStaffDialog(true) }}
            sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}
          >
            Add Staff Member
          </Button>
        )}
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Staff" value={staff.length} icon={<PeopleIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Teaching Staff" value={staff.filter(s => s.category === 'TEACHING').length} icon={<PeopleIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Non-Teaching" value={staff.filter(s => s.category === 'NON_TEACHING').length} icon={<PeopleIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Staff" value={staff.filter(s => s.is_active).length} icon={<PeopleIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={staff}
        onEdit={(s) => console.log('Edit:', s)}
        onDelete={(s) => { setSelectedStaff(s); setOpenDeleteDialog(true); }}
      />

      {/* Create Staff Dialog */}
      <Dialog open={openStaffDialog} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PersonAddIcon /> Add Staff Member
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
                    <TextField fullWidth required label="First Name" value={staffForm.first_name}
                      onChange={(e) => setStaffForm({ ...staffForm, first_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="Last Name" value={staffForm.last_name}
                      onChange={(e) => setStaffForm({ ...staffForm, last_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="Email" type="email" value={staffForm.email}
                      onChange={(e) => setStaffForm({ ...staffForm, email: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth label="Phone Number" value={staffForm.phone_number}
                      onChange={(e) => setStaffForm({ ...staffForm, phone_number: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="Date of Birth" type="date" InputLabelProps={{ shrink: true }}
                      value={staffForm.date_of_birth}
                      onChange={(e) => setStaffForm({ ...staffForm, date_of_birth: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Gender</InputLabel>
                      <Select value={staffForm.gender} label="Gender"
                        onChange={(e) => setStaffForm({ ...staffForm, gender: e.target.value })}>
                        <MenuItem value="M">Male</MenuItem>
                        <MenuItem value="F">Female</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Marital Status</InputLabel>
                      <Select value={staffForm.marital_status} label="Marital Status"
                        onChange={(e) => setStaffForm({ ...staffForm, marital_status: e.target.value })}>
                        <MenuItem value="SINGLE">Single</MenuItem>
                        <MenuItem value="MARRIED">Married</MenuItem>
                        <MenuItem value="DIVORCED">Divorced</MenuItem>
                        <MenuItem value="WIDOWED">Widowed</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="State of Origin" value={staffForm.state_of_origin}
                      onChange={(e) => setStaffForm({ ...staffForm, state_of_origin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="LGA of Origin" value={staffForm.lga_of_origin}
                      onChange={(e) => setStaffForm({ ...staffForm, lga_of_origin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField fullWidth required label="Residential Address" multiline rows={2} value={staffForm.residential_address}
                      onChange={(e) => setStaffForm({ ...staffForm, residential_address: e.target.value })} />
                  </Grid>
                </Grid>
              )}

              {/* Step 1: Employment Details */}
              {activeStep === 1 && (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Category</InputLabel>
                      <Select value={staffForm.category} label="Category"
                        onChange={(e) => setStaffForm({ ...staffForm, category: e.target.value })}>
                        <MenuItem value="TEACHING">Teaching Staff</MenuItem>
                        <MenuItem value="NON_TEACHING">Non-Teaching Staff</MenuItem>
                        <MenuItem value="ADMINISTRATIVE">Administrative Staff</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Designation</InputLabel>
                      <Select value={staffForm.designation} label="Designation"
                        onChange={(e) => setStaffForm({ ...staffForm, designation: e.target.value })}>
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
                    <FormControl fullWidth required>
                      <InputLabel>Employment Type</InputLabel>
                      <Select value={staffForm.employment_type} label="Employment Type"
                        onChange={(e) => setStaffForm({ ...staffForm, employment_type: e.target.value })}>
                        <MenuItem value="PERMANENT">Permanent</MenuItem>
                        <MenuItem value="CONTRACT">Contract</MenuItem>
                        <MenuItem value="TEMPORARY">Temporary</MenuItem>
                        <MenuItem value="VOLUNTEER">Volunteer</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth required>
                      <InputLabel>Qualification</InputLabel>
                      <Select value={staffForm.qualification} label="Qualification"
                        onChange={(e) => setStaffForm({ ...staffForm, qualification: e.target.value })}>
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
                    <TextField fullWidth required label="Date Joined" type="date" InputLabelProps={{ shrink: true }}
                      value={staffForm.date_joined}
                      onChange={(e) => setStaffForm({ ...staffForm, date_joined: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth label="Grade Level" value={staffForm.grade_level}
                      onChange={(e) => setStaffForm({ ...staffForm, grade_level: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth label="Step" type="number" value={staffForm.step}
                      onChange={(e) => setStaffForm({ ...staffForm, step: parseInt(e.target.value) || 1 })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth label="Salary" type="number" value={staffForm.salary}
                      onChange={(e) => setStaffForm({ ...staffForm, salary: parseFloat(e.target.value) || 0 })} />
                  </Grid>
                </Grid>
              )}

              {/* Step 2: Financial & Contact */}
              {activeStep === 2 && (
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Emergency Contact</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="Emergency Contact Name" value={staffForm.emergency_contact_name}
                      onChange={(e) => setStaffForm({ ...staffForm, emergency_contact_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField fullWidth required label="Emergency Contact Phone" value={staffForm.emergency_contact_phone}
                      onChange={(e) => setStaffForm({ ...staffForm, emergency_contact_phone: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Bank Details</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth required label="Bank Name" value={staffForm.bank_name}
                      onChange={(e) => setStaffForm({ ...staffForm, bank_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth required label="Account Number" value={staffForm.bank_account_number}
                      onChange={(e) => setStaffForm({ ...staffForm, bank_account_number: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth required label="Account Name" value={staffForm.bank_account_name}
                      onChange={(e) => setStaffForm({ ...staffForm, bank_account_name: e.target.value })} />
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Other (Optional)</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth label="Pension PIN" value={staffForm.pension_pin}
                      onChange={(e) => setStaffForm({ ...staffForm, pension_pin: e.target.value })} />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField fullWidth label="Tax ID" value={staffForm.tax_id}
                      onChange={(e) => setStaffForm({ ...staffForm, tax_id: e.target.value })} />
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>
            {createdStaff ? 'Close' : 'Cancel'}
          </Button>
          {!createdStaff && (
            <>
              {activeStep > 0 && (
                <Button onClick={() => setActiveStep(activeStep - 1)}>Back</Button>
              )}
              {activeStep < steps.length - 1 ? (
                <Button variant="contained" onClick={() => setActiveStep(activeStep + 1)}
                  disabled={!isStepValid(activeStep)}>
                  Next
                </Button>
              ) : (
                <Button variant="contained" onClick={handleCreateStaff}
                  disabled={creatingStaff}
                  sx={{ bgcolor: '#388e3c', '&:hover': { bgcolor: '#2e7d32' } }}>
                  {creatingStaff ? 'Creating...' : 'Create Staff Account'}
                </Button>
              )}
            </>
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
