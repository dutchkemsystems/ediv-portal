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
  Work as JobIcon,
  People as ApplicantIcon,
  Receipt as PayslipIcon,
  AccountBalance as PayrollIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function HR() {
  const [tab, setTab] = useState(0)
  const [jobPostings, setJobPostings] = useState([])
  const [applications, setApplications] = useState([])
  const [payrollPeriods, setPayrollPeriods] = useState([])
  const [payslips, setPayslips] = useState([])
  const [loading, setLoading] = useState(true)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [jobFilters, setJobFilters] = useState({ status: '' })
  const [appFilters, setAppFilters] = useState({ status: '' })
  const [payrollFilters, setPayrollFilters] = useState({ status: '' })
  const [payslipFilters, setPayslipFilters] = useState({ status: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchAll()
  }, [])

  useEffect(() => {
    if (tab === 0) fetchJobPostings()
    if (tab === 1) fetchApplications()
    if (tab === 2) fetchPayrollPeriods()
    if (tab === 3) fetchPayslips()
  }, [jobFilters, appFilters, payrollFilters, payslipFilters])

  const fetchAll = async () => {
    try {
      setLoading(true)
      await Promise.all([fetchJobPostings(), fetchApplications(), fetchPayrollPeriods(), fetchPayslips()])
    } finally {
      setLoading(false)
    }
  }

  const buildQuery = (filters) => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v) })
    const q = params.toString()
    return q ? `?${q}` : ''
  }

  const fetchJobPostings = async () => {
    try {
      const res = await api.get(`/hr/job-postings/${buildQuery(jobFilters)}`)
      setJobPostings(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const fetchApplications = async () => {
    try {
      const res = await api.get(`/hr/applications/${buildQuery(appFilters)}`)
      setApplications(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const fetchPayrollPeriods = async () => {
    try {
      const res = await api.get(`/hr/payroll-periods/${buildQuery(payrollFilters)}`)
      setPayrollPeriods(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const fetchPayslips = async () => {
    try {
      const res = await api.get(`/hr/payslips/${buildQuery(payslipFilters)}`)
      setPayslips(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const handleFilterChange = (field, value) => {
    if (tab === 0) setJobFilters(prev => ({ ...prev, [field]: value }))
    if (tab === 1) setAppFilters(prev => ({ ...prev, [field]: value }))
    if (tab === 2) setPayrollFilters(prev => ({ ...prev, [field]: value }))
    if (tab === 3) setPayslipFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    setJobFilters({ status: '' })
    setAppFilters({ status: '' })
    setPayrollFilters({ status: '' })
    setPayslipFilters({ status: '' })
  }

  const getActiveFilters = () => {
    if (tab === 0) return jobFilters
    if (tab === 1) return appFilters
    if (tab === 2) return payrollFilters
    return payslipFilters
  }

  const hasActiveFilters = Object.values(getActiveFilters()).some(v => v !== '')

  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData({ title: '', department: '', salary_range: '', status: '', application_date: '', payment_period: '', amount: '', description: '' })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
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
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
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
    setSubmitting(true)
    try {
      const endpoint = getEndpoint()
      if (selectedItem) {
        await api.put(`/hr/${endpoint}/${selectedItem.id}/`, formData)
        notify.success('Record updated')
      } else {
        await api.post(`/hr/${endpoint}/`, formData)
        notify.success('Record created')
      }
      setOpenFormDialog(false)
      setFormErrors({})
      fetchAll()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save'
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
      const endpoint = getEndpoint()
      await api.delete(`/hr/${endpoint}/${selectedItem.id}/`)
      notify.success('Record deleted')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      fetchAll()
    } catch (error) {
      notify.error('Failed to delete')
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
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Human Resources</Typography>
          <Typography variant="body2" color="text.secondary">
            {tab === 0 ? `${jobPostings.length} job postings` : tab === 1 ? `${applications.length} applications` : tab === 2 ? `${payrollPeriods.length} payroll periods` : `${payslips.length} payslips`}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters {hasActiveFilters ? `(${Object.values(getActiveFilters()).filter(v => v).length})` : ''}
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            Add Record
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => { setTab(v); setShowFilters(false) }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}>
          <Tab label={`Job Postings (${jobPostings.length})`} />
          <Tab label={`Applications (${applications.length})`} />
          <Tab label={`Payroll (${payrollPeriods.length})`} />
          <Tab label={`Payslips (${payslips.length})`} />
        </Tabs>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter</Typography>
            {hasActiveFilters && <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={getActiveFilters().status || ''} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                  <MenuItem value="">All Statuses</MenuItem>
                  {tab === 0 && <><MenuItem value="DRAFT">Draft</MenuItem><MenuItem value="OPEN">Open</MenuItem><MenuItem value="CLOSED">Closed</MenuItem></>}
                  {tab === 1 && <><MenuItem value="UNDER_REVIEW">Under Review</MenuItem><MenuItem value="APPROVED">Approved</MenuItem><MenuItem value="REJECTED">Rejected</MenuItem><MenuItem value="PENDING">Pending</MenuItem></>}
                  {tab === 2 && <><MenuItem value="DRAFT">Draft</MenuItem><MenuItem value="PROCESSING">Processing</MenuItem><MenuItem value="APPROVED">Approved</MenuItem><MenuItem value="PAID">Paid</MenuItem></>}
                  {tab === 3 && <><MenuItem value="PENDING">Pending</MenuItem><MenuItem value="PROCESSING">Processing</MenuItem><MenuItem value="PAID">Paid</MenuItem></>}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Open Positions" value={openPositions} icon={<JobIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Applications" value={applications.length} icon={<ApplicantIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Payslips" value={pendingPayslips} icon={<PayslipIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Payroll" value={`₦${payrollPeriods.reduce((sum, p) => sum + (Number(p.total_amount) || 0), 0).toLocaleString()}`} icon={<PayrollIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Tables */}
      {tab === 0 && <DataTable columns={jobColumns} data={jobPostings} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />}
      {tab === 1 && <DataTable columns={applicationColumns} data={applications} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />}
      {tab === 2 && <DataTable columns={payrollPeriodColumns} data={payrollPeriods} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />}
      {tab === 3 && <DataTable columns={payslipColumns} data={payslips} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />}

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
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
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {submitting ? 'Saving...' : selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {tab === 0 ? 'Job Posting' : tab === 1 ? 'Application' : tab === 2 ? 'Payroll Period' : 'Payslip'} Details
          {selectedItem?.status && (
            <Chip label={selectedItem.status} size="small" sx={{ ml: 1 }} color={statusColor(selectedItem.status)} />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              {tab === 0 && (<>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Position</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.title}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Department</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.department}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Salary Range</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.salary_range || '-'}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Posted</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.posting_date || '-'}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Closing</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.closing_date || '-'}</Typography></Grid>
                {selectedItem.description && <Grid item xs={12}><Divider sx={{ my: 1 }} /><Typography variant="caption" color="text.secondary">Description</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.description}</Typography></Grid>}
              </>)}
              {tab === 1 && (<>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Applicant</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.applicant_name}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Position</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.job_title}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Applied</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.application_date}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Qualification</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.qualification || '-'}</Typography></Grid>
              </>)}
              {tab === 2 && (<>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Period</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.name}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Total Amount</Typography><Typography variant="body2" sx={{ fontWeight: 500, color: '#388e3c' }}>₦{Number(selectedItem.total_amount || 0).toLocaleString()}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Start Date</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.start_date}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">End Date</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.end_date}</Typography></Grid>
              </>)}
              {tab === 3 && (<>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Staff</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.staff_name}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Period</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.payment_period}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Basic Salary</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>₦{Number(selectedItem.basic_salary || 0).toLocaleString()}</Typography></Grid>
                <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Net Pay</Typography><Typography variant="body2" sx={{ fontWeight: 500, color: '#388e3c' }}>₦{Number(selectedItem.net_pay || 0).toLocaleString()}</Typography></Grid>
              </>)}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />} onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }} sx={{ bgcolor: '#1a237e' }}>Edit</Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog
        open={openDeleteDialog}
        title={getDeleteTitle()}
        message={getDeleteMessage()}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default HR
