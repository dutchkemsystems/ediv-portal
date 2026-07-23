import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Grid,
  Chip,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'
import DataTable from '../components/common/DataTable'
import ConfirmDialog from '../components/common/ConfirmDialog'
import { notify } from '../utils/notifications'

const emptyGrant = {
  name: '',
  funding_source: '',
  amount: '',
  purpose: '',
  status: 'PENDING',
  start_date: '',
  end_date: '',
  school: '',
  department: '',
  notes: '',
}

function Grants() {
  const [grants, setGrants] = useState([])
  const [schools, setSchools] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [selectedGrant, setSelectedGrant] = useState(null)
  const [form, setForm] = useState(emptyGrant)
  const [isEdit, setIsEdit] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [grantsRes, schoolsRes, deptRes] = await Promise.all([
        api.get('/finance/budgets/').catch(() => ({ data: { results: [] } })),
        api.get('/schools/schools/').catch(() => ({ data: { results: [] } })),
        api.get('/departments/departments/').catch(() => ({ data: { results: [] } })),
      ])
      setGrants(grantsRes.data.results || grantsRes.data || [])
      setSchools(schoolsRes.data.results || schoolsRes.data || [])
      setDepartments(deptRes.data.results || deptRes.data || [])
    } catch (err) {
      console.error('Failed to fetch grants data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleOpen = (grant = null) => {
    if (grant) {
      setForm({ ...emptyGrant, ...grant })
      setIsEdit(true)
    } else {
      setForm(emptyGrant)
      setIsEdit(false)
    }
    setDialogOpen(true)
  }

  const handleClose = () => { setDialogOpen(false); setSelectedGrant(null) }

  const handleSave = async () => {
    try {
      if (isEdit && form.id) {
        await api.put(`/finance/budgets/${form.id}/`, form)
        notify.success('Grant updated successfully')
      } else {
        await api.post('/finance/budgets/', form)
        notify.success('Grant created successfully')
      }
      handleClose()
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to save grant')
    }
  }

  const handleDelete = async () => {
    if (!selectedGrant) return
    try {
      await api.delete(`/finance/budgets/${selectedGrant.id}/`)
      notify.success('Grant deleted successfully')
      setConfirmOpen(false)
      setSelectedGrant(null)
      fetchData()
    } catch (err) {
      notify.error('Failed to delete grant')
    }
  }

  const statusColor = (status) => {
    const colors = { APPROVED: 'success', PENDING: 'warning', REJECTED: 'error', ACTIVE: 'info' }
    return colors[status] || 'default'
  }

  const totalGrants = grants.length
  const approvedGrants = grants.filter(g => g.is_approved || g.status === 'APPROVED').length
  const totalValue = grants.reduce((sum, g) => sum + (parseFloat(g.allocated_amount || g.amount || 0)), 0)
  const pendingGrants = grants.filter(g => !g.is_approved && g.status !== 'APPROVED').length

  const columns = [
    { key: 'name', label: 'Grant Name' },
    { key: 'funding_source', label: 'Funding Source' },
    {
      key: 'allocated_amount',
      label: 'Amount',
      render: (row) => `₦${(parseFloat(row.allocated_amount || row.amount || 0)).toLocaleString()}`
    },
    { key: 'description', label: 'Purpose' },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <Chip label={row.status || 'PENDING'} color={statusColor(row.status)} size="small" />
    },
    {
      key: 'academic_year',
      label: 'Year',
      render: (row) => row.academic_year || '-'
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>Grants Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()}>
          Add Grant
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Grants" value={totalGrants} icon="📊" color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Approved" value={approvedGrants} icon="✅" color="#00843D" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Value" value={`₦${totalValue.toLocaleString()}`} icon="💰" color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending" value={pendingGrants} icon="⏳" color="#F9A825" />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={grants}
        loading={loading}
        onEdit={(g) => handleOpen(g)}
        onDelete={(g) => { setSelectedGrant(g); setConfirmOpen(true) }}
        searchable
      />

      <Dialog open={dialogOpen} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{isEdit ? 'Edit Grant' : 'Add New Grant'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Grant Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Funding Source" value={form.funding_source} onChange={e => setForm({ ...form, funding_source: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Amount (₦)" type="number" value={form.amount || form.allocated_amount} onChange={e => setForm({ ...form, amount: e.target.value, allocated_amount: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth select label="Status" value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                {['PENDING', 'APPROVED', 'ACTIVE', 'REJECTED', 'COMPLETED'].map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Purpose / Description" multiline rows={3} value={form.purpose || form.description} onChange={e => setForm({ ...form, purpose: e.target.value, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Start Date" type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="End Date" type="date" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Notes" multiline rows={2} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>{isEdit ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete Grant"
        message={`Are you sure you want to delete "${selectedGrant?.name}"?`}
        onConfirm={handleDelete}
        onCancel={() => { setConfirmOpen(false); setSelectedGrant(null) }}
      />
    </Box>
  )
}

export default Grants
