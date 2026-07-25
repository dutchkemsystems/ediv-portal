import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  Paper,
  Stack,
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  AccountBalance as FinanceIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendIcon,
  Payment as PaymentIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import KoraPayCheckout from '../components/KoraPayCheckout'
import api from '../api/client'
import { notify } from '../utils/notifications'

const emptyFeeStructure = {
  name: '',
  fee_type: 'TUITION',
  amount: '',
  school: '',
  academic_year: '',
  term: '',
  is_compulsory: true,
  is_active: true,
  description: '',
}

function Finance() {
  const [payments, setPayments] = useState([])
  const [studentFees, setStudentFees] = useState([])
  const [feeStructures, setFeeStructures] = useState([])
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)

  // KoraPay checkout state
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [selectedFee, setSelectedFee] = useState(null)

  // Dialogs
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState(emptyFeeStructure)
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [feeFilters, setFeeFilters] = useState({ status: '', student: '' })
  const [paymentFilters, setPaymentFilters] = useState({ is_confirmed: '', payment_method: '' })
  const [structureFilters, setStructureFilters] = useState({ school: '', fee_type: '', term: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchData()
    fetchSchools()
  }, [])

  useEffect(() => {
    if (tabValue === 0) fetchStudentFees()
    if (tabValue === 1) fetchPayments()
    if (tabValue === 2) fetchFeeStructures()
  }, [feeFilters, paymentFilters, structureFilters])

  const fetchData = async () => {
    try {
      setLoading(true)
      await Promise.all([fetchStudentFees(), fetchPayments(), fetchFeeStructures()])
    } finally {
      setLoading(false)
    }
  }

  const fetchStudentFees = async () => {
    try {
      const params = new URLSearchParams()
      if (feeFilters.status) params.append('status', feeFilters.status)
      if (feeFilters.student) params.append('student', feeFilters.student)
      const query = params.toString()
      const res = await api.get(`/finance/student-fees/${query ? `?${query}` : ''}`)
      setStudentFees(res.data.results || res.data || [])
    } catch (error) {
      // silent
    }
  }

  const fetchPayments = async () => {
    try {
      const params = new URLSearchParams()
      if (paymentFilters.is_confirmed) params.append('is_confirmed', paymentFilters.is_confirmed)
      if (paymentFilters.payment_method) params.append('payment_method', paymentFilters.payment_method)
      const query = params.toString()
      const res = await api.get(`/finance/payments/${query ? `?${query}` : ''}`)
      setPayments(res.data.results || res.data || [])
    } catch (error) {
      // silent
    }
  }

  const fetchFeeStructures = async () => {
    try {
      const params = new URLSearchParams()
      if (structureFilters.school) params.append('school', structureFilters.school)
      if (structureFilters.fee_type) params.append('fee_type', structureFilters.fee_type)
      if (structureFilters.term) params.append('term', structureFilters.term)
      const query = params.toString()
      const res = await api.get(`/finance/fee-structures/${query ? `?${query}` : ''}`)
      setFeeStructures(res.data.results || res.data || [])
    } catch (error) {
      // silent
    }
  }

  const fetchSchools = async () => {
    try {
      const res = await api.get('/schools/schools/')
      setSchools(res.data.results || res.data || [])
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    if (tabValue === 0) setFeeFilters(prev => ({ ...prev, [field]: value }))
    if (tabValue === 1) setPaymentFilters(prev => ({ ...prev, [field]: value }))
    if (tabValue === 2) setStructureFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    if (tabValue === 0) setFeeFilters({ status: '', student: '' })
    if (tabValue === 1) setPaymentFilters({ is_confirmed: '', payment_method: '' })
    if (tabValue === 2) setStructureFilters({ school: '', fee_type: '', term: '' })
  }

  const getActiveFilters = () => {
    if (tabValue === 0) return feeFilters
    if (tabValue === 1) return paymentFilters
    return structureFilters
  }

  const hasActiveFilters = Object.values(getActiveFilters()).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData(emptyFeeStructure)
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      name: item.name || '',
      fee_type: item.fee_type || 'TUITION',
      amount: item.amount || '',
      school: item.school || '',
      academic_year: item.academic_year || '',
      term: item.term || '',
      is_compulsory: item.is_compulsory !== false,
      is_active: item.is_active !== false,
      description: item.description || '',
    })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const handlePayNow = (fee) => {
    setSelectedFee(fee)
    setCheckoutOpen(true)
  }

  const handlePaymentSuccess = () => {
    setCheckoutOpen(false)
    setSelectedFee(null)
    fetchData()
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.name.trim()) errors.name = 'Fee name is required'
    if (!formData.amount || formData.amount <= 0) errors.amount = 'Amount is required'
    if (!formData.school) errors.school = 'School is required'
    if (!formData.academic_year.trim()) errors.academic_year = 'Academic year is required'
    if (!formData.term) errors.term = 'Term is required'
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
      const payload = { ...formData, amount: parseFloat(formData.amount) }
      if (selectedItem) {
        await api.put(`/finance/fee-structures/${selectedItem.id}/`, payload)
        notify.success('Fee structure updated')
      } else {
        await api.post('/finance/fee-structures/', payload)
        notify.success('Fee structure created')
      }
      setOpenFormDialog(false)
      setFormErrors({})
      fetchFeeStructures()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save fee structure'
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
      await api.delete(`/finance/fee-structures/${selectedItem.id}/`)
      notify.success('Fee structure deleted')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      fetchFeeStructures()
    } catch (error) {
      notify.error('Failed to delete fee structure')
    }
  }

  const formatCurrency = (amount) => `₦${Number(amount || 0).toLocaleString()}`

  // Columns
  const studentFeeColumns = [
    {
      id: 'student_name',
      label: 'Student',
      render: (row) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {row.student_name || row.student?.user?.first_name || 'N/A'}
        </Typography>
      ),
    },
    { id: 'fee_name', label: 'Fee', render: (row) => row.fee_name || row.fee_structure?.name || 'N/A' },
    { id: 'amount_due', label: 'Due', align: 'right', render: (row) => formatCurrency(row.amount_due) },
    { id: 'amount_paid', label: 'Paid', align: 'right', render: (row) => formatCurrency(row.amount_paid) },
    {
      id: 'balance',
      label: 'Balance',
      align: 'right',
      render: (row) => (
        <Typography color={row.balance > 0 ? 'error' : 'success'} fontWeight="bold" variant="body2">
          {formatCurrency(row.balance)}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      render: (row) => (
        <Chip
          label={row.status}
          size="small"
          color={row.status === 'COMPLETED' ? 'success' : row.status === 'PARTIAL' ? 'warning' : 'error'}
        />
      ),
    },
  ]

  const paymentColumns = [
    {
      id: 'student_name',
      label: 'Student',
      render: (row) => row.student_fee?.student_name || row.student_name || 'N/A',
    },
    { id: 'fee_name', label: 'Fee Type', render: (row) => row.student_fee?.fee_name || row.fee_name || 'N/A' },
    { id: 'amount', label: 'Amount', align: 'right', render: (row) => formatCurrency(row.amount) },
    { id: 'payment_method', label: 'Method', render: (row) => row.payment_method?.replace('_', ' ') || '-' },
    { id: 'reference_number', label: 'Reference' },
    { id: 'payment_date', label: 'Date' },
    {
      id: 'is_confirmed',
      label: 'Status',
      render: (row) => (
        <Chip label={row.is_confirmed ? 'Confirmed' : 'Pending'} size="small" color={row.is_confirmed ? 'success' : 'warning'} />
      ),
    },
  ]

  const feeStructureColumns = [
    { id: 'name', label: 'Fee Name' },
    { id: 'school_name', label: 'School', render: (row) => row.school_name || row.school?.name || 'N/A' },
    { id: 'fee_type', label: 'Type', render: (row) => row.fee_type?.replace('_', ' ') || '-' },
    { id: 'amount', label: 'Amount', align: 'right', render: (row) => formatCurrency(row.amount) },
    { id: 'academic_year', label: 'Year' },
    { id: 'term', label: 'Term', render: (row) => row.term?.replace('FIRST', '1st').replace('SECOND', '2nd').replace('THIRD', '3rd') || '-' },
    { id: 'is_compulsory', label: 'Compulsory', render: (row) => <Chip label={row.is_compulsory ? 'Yes' : 'No'} size="small" color={row.is_compulsory ? 'warning' : 'default'} /> },
  ]

  if (loading) return <Loading message="Loading finance data..." />

  const totalCollected = payments.filter(p => p.is_confirmed).reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
  const totalPending = payments.filter(p => !p.is_confirmed).reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
  const totalDue = studentFees.filter(f => f.balance > 0).reduce((sum, f) => sum + parseFloat(f.balance || 0), 0)

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Finance Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {tabValue === 0 ? `${studentFees.length} fee records` : tabValue === 1 ? `${payments.length} payments` : `${feeStructures.length} fee structures`}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters {hasActiveFilters ? `(${Object.values(getActiveFilters()).filter(v => v).length})` : ''}
          </Button>
          {tabValue === 2 && (
            <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
              sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
              Add Fee Structure
            </Button>
          )}
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setShowFilters(false) }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}>
          <Tab label={`Student Fees (${studentFees.length})`} />
          <Tab label={`Payments (${payments.length})`} />
          <Tab label={`Fee Structures (${feeStructures.length})`} />
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
          {tabValue === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select value={feeFilters.status} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                    <MenuItem value="">All Statuses</MenuItem>
                    <MenuItem value="PENDING">Pending</MenuItem>
                    <MenuItem value="PARTIAL">Partial</MenuItem>
                    <MenuItem value="COMPLETED">Completed</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
          {tabValue === 1 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Confirmation</InputLabel>
                  <Select value={paymentFilters.is_confirmed} onChange={(e) => handleFilterChange('is_confirmed', e.target.value)} label="Confirmation">
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="true">Confirmed</MenuItem>
                    <MenuItem value="false">Pending</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Payment Method</InputLabel>
                  <Select value={paymentFilters.payment_method} onChange={(e) => handleFilterChange('payment_method', e.target.value)} label="Payment Method">
                    <MenuItem value="">All Methods</MenuItem>
                    <MenuItem value="CASH">Cash</MenuItem>
                    <MenuItem value="BANK_TRANSFER">Bank Transfer</MenuItem>
                    <MenuItem value="ONLINE">Online</MenuItem>
                    <MenuItem value="POS">POS</MenuItem>
                    <MenuItem value="CHEQUE">Cheque</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
          {tabValue === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>School</InputLabel>
                  <Select value={structureFilters.school} onChange={(e) => handleFilterChange('school', e.target.value)} label="School">
                    <MenuItem value="">All Schools</MenuItem>
                    {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Fee Type</InputLabel>
                  <Select value={structureFilters.fee_type} onChange={(e) => handleFilterChange('fee_type', e.target.value)} label="Fee Type">
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="TUITION">Tuition</MenuItem>
                    <MenuItem value="DEVELOPMENT">Development</MenuItem>
                    <MenuItem value="SPORTS">Sports</MenuItem>
                    <MenuItem value="LIBRARY">Library</MenuItem>
                    <MenuItem value="LABORATORY">Laboratory</MenuItem>
                    <MenuItem value="EXAMINATION">Examination</MenuItem>
                    <MenuItem value="ICT">ICT</MenuItem>
                    <MenuItem value="PTA">PTA</MenuItem>
                    <MenuItem value="OTHER">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Term</InputLabel>
                  <Select value={structureFilters.term} onChange={(e) => handleFilterChange('term', e.target.value)} label="Term">
                    <MenuItem value="">All Terms</MenuItem>
                    <MenuItem value="FIRST">First Term</MenuItem>
                    <MenuItem value="SECOND">Second Term</MenuItem>
                    <MenuItem value="THIRD">Third Term</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Collected" value={formatCurrency(totalCollected)} icon={<MoneyIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Payments" value={formatCurrency(totalPending)} icon={<FinanceIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Outstanding" value={formatCurrency(totalDue)} icon={<PaymentIcon />} color="#d32f2f" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Transactions" value={payments.length} icon={<TrendIcon />} color="#1a237e" />
        </Grid>
      </Grid>

      {/* Tables */}
      {tabValue === 0 && (
        <DataTable columns={studentFeeColumns} data={studentFees}
          onView={(fee) => fee.balance > 0 ? handlePayNow(fee) : undefined} />
      )}
      {tabValue === 1 && (
        <DataTable columns={paymentColumns} data={payments} onView={handleOpenView} />
      )}
      {tabValue === 2 && (
        <DataTable columns={feeStructureColumns} data={feeStructures}
          onView={handleOpenView} onEdit={handleOpenEdit}
          onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}

      {/* KoraPay Checkout */}
      {selectedFee && (
        <KoraPayCheckout
          open={checkoutOpen}
          onClose={() => { setCheckoutOpen(false); setSelectedFee(null) }}
          onSuccess={handlePaymentSuccess}
          studentFeeId={selectedFee.id}
          amount={selectedFee.balance}
          studentName={selectedFee.student_name || selectedFee.student?.user?.first_name || 'Student'}
          studentEmail={selectedFee.student_email || selectedFee.student?.user?.email || ''}
          feeName={selectedFee.fee_name || selectedFee.fee_structure?.name || 'School Fee'}
        />
      )}

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{selectedItem ? 'Edit Fee Structure' : 'Add Fee Structure'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Fee Name"
                value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                error={!!formErrors.name} helperText={formErrors.name} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Fee Type</InputLabel>
                <Select value={formData.fee_type} onChange={(e) => setFormData({ ...formData, fee_type: e.target.value })} label="Fee Type">
                  <MenuItem value="TUITION">Tuition Fee</MenuItem>
                  <MenuItem value="DEVELOPMENT">Development Levy</MenuItem>
                  <MenuItem value="SPORTS">Sports Fee</MenuItem>
                  <MenuItem value="LIBRARY">Library Fee</MenuItem>
                  <MenuItem value="LABORATORY">Laboratory Fee</MenuItem>
                  <MenuItem value="EXAMINATION">Examination Fee</MenuItem>
                  <MenuItem value="ICT">ICT Fee</MenuItem>
                  <MenuItem value="PTA">PTA Levy</MenuItem>
                  <MenuItem value="INSURANCE">Insurance</MenuItem>
                  <MenuItem value="MEDICAL">Medical Fee</MenuItem>
                  <MenuItem value="TRANSPORT">Transport Fee</MenuItem>
                  <MenuItem value="UNIFORM">Uniform Fee</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Amount (₦)" type="number"
                value={formData.amount} onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                error={!!formErrors.amount} helperText={formErrors.amount} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.school}>
                <InputLabel>School *</InputLabel>
                <Select value={formData.school} onChange={(e) => setFormData({ ...formData, school: e.target.value })} label="School *">
                  {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                </Select>
                {formErrors.school && <Typography variant="caption" color="error">{formErrors.school}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Academic Year" placeholder="2025/2026"
                value={formData.academic_year} onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                error={!!formErrors.academic_year} helperText={formErrors.academic_year} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small" required error={!!formErrors.term}>
                <InputLabel>Term *</InputLabel>
                <Select value={formData.term} onChange={(e) => setFormData({ ...formData, term: e.target.value })} label="Term *">
                  <MenuItem value="FIRST">First Term</MenuItem>
                  <MenuItem value="SECOND">Second Term</MenuItem>
                  <MenuItem value="THIRD">Third Term</MenuItem>
                </Select>
                {formErrors.term && <Typography variant="caption" color="error">{formErrors.term}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={<Switch checked={formData.is_compulsory} onChange={(e) => setFormData({ ...formData, is_compulsory: e.target.checked })} />}
                label="Compulsory"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={<Switch checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />}
                label="Active"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth size="small" label="Description" multiline rows={2}
                value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
            </Grid>
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
        <DialogTitle sx={{ fontWeight: 600 }}>Payment Details</DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Payment Information</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Student</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.student_fee?.student_name || selectedItem.student_name || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Fee Type</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.student_fee?.fee_name || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Amount</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#388e3c' }}>{formatCurrency(selectedItem.amount)}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Payment Method</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.payment_method?.replace('_', ' ') || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Reference Number</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.reference_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Payment Date</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.payment_date}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Status</Typography>
                <Chip label={selectedItem.is_confirmed ? 'Confirmed' : 'Pending'} size="small" color={selectedItem.is_confirmed ? 'success' : 'warning'} />
              </Grid>
              {selectedItem.receipt_number && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">Receipt Number</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.receipt_number}</Typography>
                </Grid>
              )}
              {selectedItem.notes && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" color="text.secondary">Notes</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.notes}</Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Fee Structure"
        message={`Are you sure you want to delete "${selectedItem?.name}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Finance
