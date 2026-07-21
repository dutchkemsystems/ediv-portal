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
  Work as JobIcon,
  People as ApplicantIcon,
  Receipt as PayslipIcon,
  AccountBalance as PayrollIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function HR() {
  const [tab, setTab] = useState(0)
  const [jobPostings, setJobPostings] = useState([])
  const [applications, setApplications] = useState([])
  const [payrollPeriods, setPayrollPeriods] = useState([])
  const [payslips, setPayslips] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    salary_range: '',
    status: '',
    application_date: '',
    payment_period: '',
    amount: '',
    description: '',
  })

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [jobsRes, appsRes, periodsRes, payslipsRes] = await Promise.all([
        api.get('/hr/job-postings/').catch(() => ({ data: { results: [] } })),
        api.get('/hr/applications/').catch(() => ({ data: { results: [] } })),
        api.get('/hr/payroll-periods/').catch(() => ({ data: { results: [] } })),
        api.get('/hr/payslips/').catch(() => ({ data: { results: [] } })),
      ])
      setJobPostings(jobsRes.data.results || jobsRes.data)
      setApplications(appsRes.data.results || appsRes.data)
      setPayrollPeriods(periodsRes.data.results || periodsRes.data)
      setPayslips(payslipsRes.data.results || payslipsRes.data)
    } catch (error) {
      console.error('Error fetching HR data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedItem(null)
    setFormData({
      title: '',
      department: '',
      salary_range: '',
      status: '',
      application_date: '',
      payment_period: '',
      amount: '',
      description: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      title: item.title || '',
      department: item.department || '',
      salary_range: item.salary_range || '',
      status: item.status || '',
      application_date: item.application_date || '',
      payment_period: item.payment_period || '',
      amount: item.amount || '',
      description: item.description || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (item) => {
    setSelectedItem(item)
    setOpenDeleteDialog(true)
  }

  const getEndpoint = () => {
    switch (tab) {
      case 0: return 'job-postings'
      case 1: return 'applications'
      case 2: return 'payroll-periods'
      case 3: return 'payslips'
      default: return 'job-postings'
    }
  }

  const handleSubmit = async () => {
    try {
      const endpoint = getEndpoint()
      if (selectedItem) {
        await api.put(`/hr/${endpoint}/${selectedItem.id}/`, formData)
      } else {
        await api.post(`/hr/${endpoint}/`, formData)
      }
      setOpenDialog(false)
      fetchAll()
    } catch (error) {
      console.error('Error saving record:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      const endpoint = getEndpoint()
      await api.delete(`/hr/${endpoint}/${selectedItem.id}/`)
      setOpenDeleteDialog(false)
      fetchAll()
    } catch (error) {
      console.error('Error deleting record:', error)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'OPEN': case 'APPROVED': case 'PAID': return 'success'
      case 'CLOSED': case 'REJECTED': case 'PENDING': return 'warning'
      case 'DRAFT': case 'UNDER_REVIEW': case 'PROCESSING': return 'info'
      default: return 'default'
    }
  }

  const openPositions = jobPostings.filter((j) => j.status === 'OPEN').length
  const pendingPayslips = payslips.filter((p) => p.status === 'PENDING' || p.status === 'PROCESSING').length

  const jobColumns = [
    { id: 'title', label: 'Position' },
    { id: 'department', label: 'Department' },
    { id: 'salary_range', label: 'Salary Range' },
    { id: 'posting_date', label: 'Posted' },
    { id: 'closing_date', label: 'Closing' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  const applicationColumns = [
    { id: 'applicant_name', label: 'Applicant' },
    { id: 'job_title', label: 'Position' },
    { id: 'application_date', label: 'Applied' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
    { id: 'qualification', label: 'Qualification' },
  ]

  const payrollPeriodColumns = [
    { id: 'name', label: 'Period' },
    { id: 'start_date', label: 'Start Date' },
    { id: 'end_date', label: 'End Date' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
    { id: 'total_amount', label: 'Total', align: 'right' },
  ]

  const payslipColumns = [
    { id: 'staff_name', label: 'Staff' },
    { id: 'payment_period', label: 'Period' },
    { id: 'basic_salary', label: 'Basic Salary', align: 'right' },
    { id: 'allowances', label: 'Allowances', align: 'right' },
    { id: 'deductions', label: 'Deductions', align: 'right' },
    { id: 'net_pay', label: 'Net Pay', align: 'right' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
  ]

  const getDialogTitle = () => {
    const labels = ['Job Posting', 'Application', 'Payroll Period', 'Payslip']
    return selectedItem ? `Edit ${labels[tab]}` : `Add ${labels[tab]}`
  }

  const getDeleteTitle = () => {
    const labels = ['Job Posting', 'Application', 'Payroll Period', 'Payslip']
    return `Delete ${labels[tab]}`
  }

  const getDeleteMessage = () => {
    return `Are you sure you want to delete this record? This action cannot be undone.`
  }

  if (loading) {
    return <Loading message="Loading HR data..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Human Resources</Typography>
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
            title="Open Positions"
            value={openPositions}
            icon={<JobIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Applications"
            value={applications.length}
            icon={<ApplicantIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Payslips"
            value={pendingPayslips}
            icon={<PayslipIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Payroll"
            value={`₦${payrollPeriods.reduce((sum, p) => sum + (Number(p.total_amount) || 0), 0).toLocaleString()}`}
            icon={<PayrollIcon />}
            color="#d32f2f"
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
          <Tab label="Job Postings" />
          <Tab label="Applications" />
          <Tab label="Payroll Periods" />
          <Tab label="Payslips" />
        </Tabs>
      </Box>

      {/* Tables */}
      {tab === 0 && (
        <DataTable
          columns={jobColumns}
          data={jobPostings}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      {tab === 1 && (
        <DataTable
          columns={applicationColumns}
          data={applications}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      {tab === 2 && (
        <DataTable
          columns={payrollPeriodColumns}
          data={payrollPeriods}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      {tab === 3 && (
        <DataTable
          columns={payslipColumns}
          data={payslips}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{getDialogTitle()}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Job Posting fields */}
            {tab === 0 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Position Title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Department"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Salary Range"
                    value={formData.salary_range}
                    onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                    placeholder="e.g. ₦100,000 - ₦150,000"
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
                      <MenuItem value="DRAFT">Draft</MenuItem>
                      <MenuItem value="OPEN">Open</MenuItem>
                      <MenuItem value="CLOSED">Closed</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </Grid>
              </>
            )}

            {/* Application fields */}
            {tab === 1 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Applicant Name"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Applied Position"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Application Date"
                    type="date"
                    value={formData.application_date}
                    onChange={(e) => setFormData({ ...formData, application_date: e.target.value })}
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
                      <MenuItem value="UNDER_REVIEW">Under Review</MenuItem>
                      <MenuItem value="APPROVED">Approved</MenuItem>
                      <MenuItem value="REJECTED">Rejected</MenuItem>
                      <MenuItem value="PENDING">Pending</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}

            {/* Payroll Period fields */}
            {tab === 2 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Period Name"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g. January 2026"
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
                      <MenuItem value="DRAFT">Draft</MenuItem>
                      <MenuItem value="PROCESSING">Processing</MenuItem>
                      <MenuItem value="APPROVED">Approved</MenuItem>
                      <MenuItem value="PAID">Paid</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Start Date"
                    type="date"
                    value={formData.application_date}
                    onChange={(e) => setFormData({ ...formData, application_date: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="End Date"
                    type="date"
                    value={formData.payment_period}
                    onChange={(e) => setFormData({ ...formData, payment_period: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Total Amount"
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  />
                </Grid>
              </>
            )}

            {/* Payslip fields */}
            {tab === 3 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Staff Name"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Payment Period"
                    value={formData.payment_period}
                    onChange={(e) => setFormData({ ...formData, payment_period: e.target.value })}
                    placeholder="e.g. January 2026"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Basic Salary"
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
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
                      <MenuItem value="PENDING">Pending</MenuItem>
                      <MenuItem value="PROCESSING">Processing</MenuItem>
                      <MenuItem value="PAID">Paid</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title={getDeleteTitle()}
        message={getDeleteMessage()}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default HR
