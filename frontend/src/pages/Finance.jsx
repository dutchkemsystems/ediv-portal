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
} from '@mui/material'
import {
  Add as AddIcon,
  AccountBalance as FinanceIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendIcon,
  Payment as PaymentIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import KoraPayCheckout from '../components/KoraPayCheckout'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Finance() {
  const [payments, setPayments] = useState([])
  const [studentFees, setStudentFees] = useState([])
  const [feeStructures, setFeeStructures] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)

  // KoraPay checkout state
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [selectedFee, setSelectedFee] = useState(null)

  // Dialog state
  const [openDialog, setOpenDialog] = useState(false)
  const [dialogType, setDialogType] = useState('') // 'fee-structure', 'budget'
  const [formData, setFormData] = useState({})

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [paymentsRes, feesRes, structuresRes] = await Promise.all([
        api.get('/finance/payments/').catch(() => ({ data: { results: [] } })),
        api.get('/finance/student-fees/').catch(() => ({ data: { results: [] } })),
        api.get('/finance/fee-structures/').catch(() => ({ data: { results: [] } })),
      ])
      setPayments(paymentsRes.data.results || paymentsRes.data || [])
      setStudentFees(feesRes.data.results || feesRes.data || [])
      setFeeStructures(structuresRes.data.results || structuresRes.data || [])
    } catch (error) {
      notify.error('Failed to load finance data')
    } finally {
      setLoading(false)
    }
  }

  const handlePayNow = (fee) => {
    setSelectedFee(fee)
    setCheckoutOpen(true)
  }

  const handlePaymentSuccess = () => {
    setCheckoutOpen(false)
    setSelectedFee(null)
    fetchData() // Refresh data
  }

  const paymentColumns = [
    { id: 'student_name', label: 'Student', render: (row) => row.student_fee?.student_name || row.student_name || 'N/A' },
    { id: 'fee_name', label: 'Fee Type', render: (row) => row.student_fee?.fee_name || row.fee_name || 'N/A' },
    { id: 'amount', label: 'Amount', align: 'right', render: (row) => `₦${Number(row.amount).toLocaleString()}` },
    { id: 'payment_method', label: 'Method' },
    { id: 'reference_number', label: 'Reference' },
    { id: 'payment_date', label: 'Date' },
    { id: 'is_confirmed', label: 'Status', render: (row) => (
      <Chip
        label={row.is_confirmed ? 'Confirmed' : 'Pending'}
        size="small"
        color={row.is_confirmed ? 'success' : 'warning'}
      />
    )},
  ]

  const studentFeeColumns = [
    { id: 'student_name', label: 'Student', render: (row) => row.student_name || row.student?.user?.first_name || 'N/A' },
    { id: 'fee_name', label: 'Fee', render: (row) => row.fee_name || row.fee_structure?.name || 'N/A' },
    { id: 'amount_due', label: 'Due', align: 'right', render: (row) => `₦${Number(row.amount_due).toLocaleString()}` },
    { id: 'amount_paid', label: 'Paid', align: 'right', render: (row) => `₦${Number(row.amount_paid).toLocaleString()}` },
    { id: 'balance', label: 'Balance', align: 'right', render: (row) => (
      <Typography color={row.balance > 0 ? 'error' : 'success'} fontWeight="bold">
        ₦{Number(row.balance).toLocaleString()}
      </Typography>
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={row.status === 'COMPLETED' ? 'success' : row.status === 'PARTIAL' ? 'warning' : 'error'}
      />
    )},
  ]

  const feeStructureColumns = [
    { id: 'name', label: 'Fee Name' },
    { id: 'school_name', label: 'School', render: (row) => row.school_name || row.school?.name || 'N/A' },
    { id: 'fee_type', label: 'Type' },
    { id: 'amount', label: 'Amount', align: 'right', render: (row) => `₦${Number(row.amount).toLocaleString()}` },
    { id: 'academic_year', label: 'Year' },
    { id: 'term', label: 'Term' },
    { id: 'is_compulsory', label: 'Compulsory', render: (row) => row.is_compulsory ? 'Yes' : 'No' },
  ]

  if (loading) {
    return <Loading message="Loading finance data..." />
  }

  const totalCollected = payments.filter(p => p.is_confirmed).reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
  const totalPending = payments.filter(p => !p.is_confirmed).reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
  const totalDue = studentFees.filter(f => f.balance > 0).reduce((sum, f) => sum + parseFloat(f.balance || 0), 0)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Finance Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => { setDialogType('fee-structure'); setOpenDialog(true) }}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Fee Structure
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Collected" value={`₦${totalCollected.toLocaleString()}`} icon={<MoneyIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Payments" value={`₦${totalPending.toLocaleString()}`} icon={<FinanceIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Outstanding" value={`₦${totalDue.toLocaleString()}`} icon={<PaymentIcon />} color="#d32f2f" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Transactions" value={payments.length} icon={<TrendIcon />} color="#1a237e" />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Student Fees" />
          <Tab label="Payments" />
          <Tab label="Fee Structures" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {tabValue === 0 && (
        <DataTable
          columns={studentFeeColumns}
          data={studentFees}
          onView={(fee) => {
            if (fee.balance > 0) handlePayNow(fee)
          }}
        />
      )}
      {tabValue === 1 && (
        <DataTable
          columns={paymentColumns}
          data={payments}
          onView={(p) => console.log('View:', p)}
        />
      )}
      {tabValue === 2 && (
        <DataTable
          columns={feeStructureColumns}
          data={feeStructures}
          onEdit={(f) => console.log('Edit:', f)}
          onDelete={(f) => console.log('Delete:', f)}
        />
      )}

      {/* KoraPay Checkout Dialog */}
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

      {/* Add Fee Structure Dialog */}
      <Dialog open={openDialog && dialogType === 'fee-structure'} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Fee Structure</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Fee Name" value={formData.name || ''} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Fee Type</InputLabel>
                <Select value={formData.fee_type || ''} onChange={(e) => setFormData({ ...formData, fee_type: e.target.value })} label="Fee Type">
                  <MenuItem value="TUITION">Tuition Fee</MenuItem>
                  <MenuItem value="DEVELOPMENT">Development Levy</MenuItem>
                  <MenuItem value="SPORTS">Sports Fee</MenuItem>
                  <MenuItem value="LIBRARY">Library Fee</MenuItem>
                  <MenuItem value="LABORATORY">Laboratory Fee</MenuItem>
                  <MenuItem value="EXAMINATION">Examination Fee</MenuItem>
                  <MenuItem value="ICT">ICT Fee</MenuItem>
                  <MenuItem value="PTA">PTA Levy</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Amount (₦)" type="number" value={formData.amount || ''} onChange={(e) => setFormData({ ...formData, amount: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Academic Year" placeholder="2024/2025" value={formData.academic_year || ''} onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Term</InputLabel>
                <Select value={formData.term || ''} onChange={(e) => setFormData({ ...formData, term: e.target.value })} label="Term">
                  <MenuItem value="FIRST">First Term</MenuItem>
                  <MenuItem value="SECOND">Second Term</MenuItem>
                  <MenuItem value="THIRD">Third Term</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" sx={{ bgcolor: '#1a237e' }} onClick={() => { setOpenDialog(false); fetchData() }}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Finance
