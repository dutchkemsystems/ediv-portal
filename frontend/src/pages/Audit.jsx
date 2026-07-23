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
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Alert,
} from '@mui/material'
import { Add as AddIcon, Security as SecurityIcon } from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'
import DataTable from '../components/common/DataTable'
import ConfirmDialog from '../components/common/ConfirmDialog'
import { notify } from '../utils/notifications'

const lagosRed = '#C8102E'

function Audit() {
  const [tabValue, setTabValue] = useState(0)
  const [logs, setLogs] = useState([])
  const [violations, setViolations] = useState([])
  const [complianceItems, setComplianceItems] = useState([])
  const [complianceRecords, setComplianceRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)
  const [isEdit, setIsEdit] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  const emptyViolation = {
    title: '', description: '', severity: 'MEDIUM', status: 'OPEN',
    category: 'ADMINISTRATIVE', incident_date: '', evidence: '', corrective_action: '',
  }

  const emptyCompliance = {
    category: 'FINANCIAL', title: '', description: '', frequency: 'Annual',
    is_mandatory: true, reference_document: '',
  }

  const [form, setForm] = useState(emptyViolation)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [logsRes, violationsRes, itemsRes, recordsRes] = await Promise.all([
        api.get('/audit/logs/').catch(() => ({ data: { results: [] } })),
        api.get('/audit/violations/').catch(() => ({ data: { results: [] } })),
        api.get('/audit/compliance-items/').catch(() => ({ data: { results: [] } })),
        api.get('/audit/compliance-records/').catch(() => ({ data: { results: [] } })),
      ])
      setLogs(logsRes.data.results || logsRes.data || [])
      setViolations(violationsRes.data.results || violationsRes.data || [])
      setComplianceItems(itemsRes.data.results || itemsRes.data || [])
      setComplianceRecords(recordsRes.data.results || recordsRes.data || [])
    } catch (err) {
      console.error('Failed to fetch audit data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleOpen = (type, item = null) => {
    setDialogType(type)
    if (item) {
      setForm({ ...emptyViolation, ...item })
      setIsEdit(true)
    } else {
      setForm(type === 'violation' ? emptyViolation : emptyCompliance)
      setIsEdit(false)
    }
    setDialogOpen(true)
  }

  const handleClose = () => { setDialogOpen(false); setSelectedItem(null) }

  const handleSave = async () => {
    try {
      const endpoint = dialogType === 'violation' ? '/audit/violations/' : '/audit/compliance-items/'
      if (isEdit && form.id) {
        await api.put(`${endpoint}${form.id}/`, form)
        notify.success(`${dialogType} updated successfully`)
      } else {
        await api.post(endpoint, form)
        notify.success(`${dialogType} created successfully`)
      }
      handleClose()
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to save')
    }
  }

  const handleDelete = async () => {
    if (!selectedItem) return
    try {
      const endpoint = dialogType === 'violation' ? '/audit/violations/' : '/audit/compliance-items/'
      await api.delete(`${endpoint}${selectedItem.id}/`)
      notify.success('Deleted successfully')
      setConfirmOpen(false)
      setSelectedItem(null)
      fetchData()
    } catch (err) {
      notify.error('Failed to delete')
    }
  }

  const severityColor = (s) => ({ LOW: 'info', MEDIUM: 'warning', HIGH: 'error', CRITICAL: 'error' }[s] || 'default')
  const statusColor = (s) => ({ OPEN: 'warning', INVESTIGATING: 'info', RESOLVED: 'success', ESCALATED: 'error', CLOSED: 'default', COMPLIANT: 'success', NON_COMPLIANT: 'error', PENDING_REVIEW: 'warning' }[s] || 'default')

  const logColumns = [
    { key: 'user_name', label: 'User' },
    { key: 'action', label: 'Action', render: (r) => <Chip label={r.action} size="small" color="primary" /> },
    { key: 'module', label: 'Module' },
    { key: 'object_repr', label: 'Object' },
    { key: 'created_at', label: 'Timestamp', render: (r) => new Date(r.created_at).toLocaleString() },
  ]

  const violationColumns = [
    { key: 'title', label: 'Title' },
    { key: 'severity', label: 'Severity', render: (r) => <Chip label={r.severity} size="small" color={severityColor(r.severity)} /> },
    { key: 'status', label: 'Status', render: (r) => <Chip label={r.status} size="small" color={statusColor(r.status)} /> },
    { key: 'category', label: 'Category' },
    { key: 'school_name', label: 'School' },
    { key: 'incident_date', label: 'Date' },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <SecurityIcon sx={{ color: lagosRed, fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 600 }}>Audit & Compliance</Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Audit Logs" value={logs.length} icon="📋" color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Violations" value={violations.filter(v => v.status !== 'CLOSED' && v.status !== 'RESOLVED').length} icon="⚠️" color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Compliance Items" value={complianceItems.length} icon="✅" color="#00843D" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Reviews" value={complianceRecords.filter(r => r.status === 'PENDING_REVIEW').length} icon="🔍" color="#F9A825" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Audit Logs" />
          <Tab label="Violations" />
          <Tab label="Compliance Items" />
          <Tab label="Compliance Records" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <DataTable columns={logColumns} data={logs} loading={loading} searchable />
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('violation')}>
                Report Violation
              </Button>
            </Box>
            <DataTable
              columns={violationColumns}
              data={violations}
              loading={loading}
              onEdit={(v) => handleOpen('violation', v)}
              onDelete={(v) => { setSelectedItem(v); setDialogType('violation'); setConfirmOpen(true) }}
              searchable
            />
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('compliance')}>
                Add Compliance Item
              </Button>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Title</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Frequency</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Mandatory</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Active</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {complianceItems.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell><Chip label={item.category} size="small" /></TableCell>
                      <TableCell>{item.title}</TableCell>
                      <TableCell>{item.frequency}</TableCell>
                      <TableCell><Chip label={item.is_mandatory ? 'Yes' : 'No'} size="small" color={item.is_mandatory ? 'error' : 'default'} /></TableCell>
                      <TableCell><Chip label={item.is_active ? 'Active' : 'Inactive'} size="small" color={item.is_active ? 'success' : 'default'} /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {tabValue === 3 && (
          <Box sx={{ p: 3 }}>
            <DataTable
              columns={[
                { key: 'item_title', label: 'Item' },
                { key: 'school_name', label: 'School' },
                { key: 'status', label: 'Status', render: (r) => <Chip label={r.status} size="small" color={statusColor(r.status)} /> },
                { key: 'due_date', label: 'Due Date' },
                { key: 'academic_year', label: 'Year' },
              ]}
              data={complianceRecords}
              loading={loading}
              searchable
            />
          </Box>
        )}
      </Paper>

      {/* Dialog */}
      <Dialog open={dialogOpen} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{isEdit ? 'Edit' : 'Add New'} {dialogType === 'violation' ? 'Violation' : 'Compliance Item'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {dialogType === 'violation' ? (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Severity" value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value })}>
                    {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Status" value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                    {['OPEN', 'INVESTIGATING', 'RESOLVED', 'ESCALATED', 'CLOSED'].map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                    {['FINANCIAL', 'ACADEMIC', 'ADMINISTRATIVE', 'REGULATORY', 'SAFETY', 'DATA_PROTECTION', 'PROCUREMENT', 'HR'].map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Incident Date" type="date" value={form.incident_date} onChange={e => setForm({ ...form, incident_date: e.target.value })} InputLabelProps={{ shrink: true }} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Description" multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Evidence" multiline rows={2} value={form.evidence} onChange={e => setForm({ ...form, evidence: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Corrective Action" multiline rows={2} value={form.corrective_action} onChange={e => setForm({ ...form, corrective_action: e.target.value })} />
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                    {['FINANCIAL', 'ACADEMIC', 'ADMINISTRATIVE', 'REGULATORY', 'SAFETY', 'DATA_PROTECTION', 'PROCUREMENT', 'HR'].map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Frequency" value={form.frequency} onChange={e => setForm({ ...form, frequency: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Reference Document" value={form.reference_document} onChange={e => setForm({ ...form, reference_document: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Description" multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>{isEdit ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete Item"
        message={`Are you sure you want to delete "${selectedItem?.title}"?`}
        onConfirm={handleDelete}
        onCancel={() => { setConfirmOpen(false); setSelectedItem(null) }}
      />
    </Box>
  )
}

export default Audit
