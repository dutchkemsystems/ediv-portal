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
  Description as DocIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Registry() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [rejectDialog, setRejectDialog] = useState({ open: false, doc: null, reason: '' })
  const [formData, setFormData] = useState({
    title: '',
    document_type: 'CORRESPONDENCE',
    classification: 'INTERNAL',
  })

  // Filters
  const [filters, setFilters] = useState({ document_type: '', classification: '', status: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [filters])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.document_type) params.append('document_type', filters.document_type)
      if (filters.classification) params.append('classification', filters.classification)
      if (filters.status) params.append('status', filters.status)
      const query = params.toString()
      const response = await api.get(`/registry/documents/${query ? `?${query}` : ''}`)
      setDocuments(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    setFilters({ document_type: '', classification: '', status: '' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      title: item.title || '',
      document_type: item.document_type || 'CORRESPONDENCE',
      classification: item.classification || 'INTERNAL',
      content: item.content || '',
    })
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedItem) {
        await api.put(`/registry/documents/${selectedItem.id}/`, formData)
        notify.success('Document updated')
      } else {
        await api.post('/registry/documents/', formData)
        notify.success('Document created')
      }
      setOpenFormDialog(false)
      setSelectedItem(null)
      fetchDocuments()
    } catch (error) {
      notify.error(error.response?.data?.detail || 'Failed to save document')
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/registry/documents/${selectedItem.id}/`)
      notify.success('Document deleted')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      fetchDocuments()
    } catch (error) {
      notify.error('Failed to delete document')
    }
  }

  const handleApprove = async (doc) => {
    try {
      await api.post(`/registry/documents/${doc.id}/approve/`)
      notify.success(`Document ${doc.reference_number} approved`)
      fetchDocuments()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to approve document')
    }
  }

  const handleReject = async () => {
    try {
      await api.post(`/registry/documents/${rejectDialog.doc.id}/reject/`, {
        reason: rejectDialog.reason,
      })
      notify.success(`Document ${rejectDialog.doc.reference_number} rejected`)
      setRejectDialog({ open: false, doc: null, reason: '' })
      fetchDocuments()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to reject document')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'APPROVED': return 'success'
      case 'PENDING': return 'warning'
      case 'DRAFT': return 'default'
      case 'REJECTED': return 'error'
      case 'ARCHIVED': return 'info'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'reference_number', label: 'Reference Number' },
    { id: 'title', label: 'Title' },
    { id: 'document_type', label: 'Type', render: (row) => (
      <Chip label={row.document_type} size="small" />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
    { id: 'classification', label: 'Classification', render: (row) => (
      <Chip
        label={row.classification}
        size="small"
        color={
          row.classification === 'CONFIDENTIAL' ? 'error' :
          row.classification === 'RESTRICTED' ? 'warning' : 'default'
        }
      />
    )},
    { id: 'created_by_name', label: 'Created By' },
    { id: 'created_at', label: 'Created', render: (row) => new Date(row.created_at).toLocaleDateString() },
    { id: 'actions', label: 'Actions', render: (row) => (
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        {row.status === 'PENDING' && (
          <>
            <Button
              size="small"
              color="success"
              startIcon={<ApproveIcon />}
              onClick={() => handleApprove(row)}
              sx={{ minWidth: 0, px: 1 }}
            >
              Approve
            </Button>
            <Button
              size="small"
              color="error"
              startIcon={<RejectIcon />}
              onClick={() => setRejectDialog({ open: true, doc: row, reason: '' })}
              sx={{ minWidth: 0, px: 1 }}
            >
              Reject
            </Button>
          </>
        )}
      </Box>
    )},
  ]

  if (loading) {
    return <Loading message="Loading registry..." />
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>E-Registry Documents</Typography>
          <Typography variant="body2" color="text.secondary">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters {hasActiveFilters ? `(${Object.values(filters).filter(v => v).length})` : ''}
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setSelectedItem(null); setFormData({ title: '', document_type: 'CORRESPONDENCE', classification: 'INTERNAL' }); setOpenFormDialog(true) }}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            New Document
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(e, v) => { setTabValue(v); setShowFilters(false) }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}>
          <Tab label={`All (${documents.length})`} />
          <Tab label={`Pending (${documents.filter(d => d.status === 'PENDING').length})`} />
          <Tab label={`Approved (${documents.filter(d => d.status === 'APPROVED').length})`} />
        </Tabs>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Documents</Typography>
            {hasActiveFilters && <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Document Type</InputLabel>
                <Select value={filters.document_type} onChange={(e) => handleFilterChange('document_type', e.target.value)} label="Document Type">
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="CORRESPONDENCE">Correspondence</MenuItem>
                  <MenuItem value="MEMO">Memo</MenuItem>
                  <MenuItem value="CIRCULAR">Circular</MenuItem>
                  <MenuItem value="REPORT">Report</MenuItem>
                  <MenuItem value="MINUTES">Minutes</MenuItem>
                  <MenuItem value="POLICY">Policy</MenuItem>
                  <MenuItem value="CONTRACT">Contract</MenuItem>
                  <MenuItem value="LETTER">Letter</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Classification</InputLabel>
                <Select value={filters.classification} onChange={(e) => handleFilterChange('classification', e.target.value)} label="Classification">
                  <MenuItem value="">All Classifications</MenuItem>
                  <MenuItem value="PUBLIC">Public</MenuItem>
                  <MenuItem value="INTERNAL">Internal</MenuItem>
                  <MenuItem value="CONFIDENTIAL">Confidential</MenuItem>
                  <MenuItem value="RESTRICTED">Restricted</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="DRAFT">Draft</MenuItem>
                  <MenuItem value="PENDING">Pending</MenuItem>
                  <MenuItem value="APPROVED">Approved</MenuItem>
                  <MenuItem value="REJECTED">Rejected</MenuItem>
                  <MenuItem value="ARCHIVED">Archived</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Documents" value={documents.length} icon={<DocIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Approved" value={documents.filter(d => d.status === 'APPROVED').length} icon={<DocIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending" value={documents.filter(d => d.status === 'PENDING').length} icon={<DocIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Rejected" value={documents.filter(d => d.status === 'REJECTED').length} icon={<DocIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={
          tabValue === 0 ? documents :
          tabValue === 1 ? documents.filter(d => d.status === 'PENDING') :
          documents.filter(d => d.status === 'APPROVED')
        }
        onView={handleOpenView}
        onEdit={handleOpenEdit}
        onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }}
      />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{selectedItem ? 'Edit Document' : 'New Document'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Document Type</InputLabel>
                <Select
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  label="Document Type"
                >
                  <MenuItem value="CORRESPONDENCE">Correspondence</MenuItem>
                  <MenuItem value="MEMO">Memo</MenuItem>
                  <MenuItem value="CIRCULAR">Circular</MenuItem>
                  <MenuItem value="REPORT">Report</MenuItem>
                  <MenuItem value="MINUTES">Minutes</MenuItem>
                  <MenuItem value="POLICY">Policy</MenuItem>
                  <MenuItem value="CONTRACT">Contract</MenuItem>
                  <MenuItem value="LETTER">Letter</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Classification</InputLabel>
                <Select
                  value={formData.classification}
                  onChange={(e) => setFormData({ ...formData, classification: e.target.value })}
                  label="Classification"
                >
                  <MenuItem value="PUBLIC">Public</MenuItem>
                  <MenuItem value="INTERNAL">Internal</MenuItem>
                  <MenuItem value="CONFIDENTIAL">Confidential</MenuItem>
                  <MenuItem value="RESTRICTED">Restricted</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!formData.title}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Document Details
          {selectedItem?.status && <Chip label={selectedItem.status} size="small" sx={{ ml: 1 }} color={getStatusColor(selectedItem.status)} />}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Document Information</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Reference Number</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.reference_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Title</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.title}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Document Type</Typography>
                <Chip label={selectedItem.document_type} size="small" />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Classification</Typography>
                <Chip label={selectedItem.classification} size="small"
                  color={selectedItem.classification === 'CONFIDENTIAL' ? 'error' : selectedItem.classification === 'RESTRICTED' ? 'warning' : 'default'} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Created By</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.created_by_name || '-'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary">Created At</Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.created_at ? new Date(selectedItem.created_at).toLocaleString() : '-'}</Typography>
              </Grid>
              {selectedItem.content && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" color="text.secondary">Content</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500, whiteSpace: 'pre-wrap' }}>{selectedItem.content}</Typography>
                </Grid>
              )}
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
        title="Delete Document"
        message={`Are you sure you want to delete "${selectedItem?.title}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />

      {/* Reject Reason Dialog */}
      <Dialog open={rejectDialog.open} onClose={() => setRejectDialog({ open: false, doc: null, reason: '' })} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Document — {rejectDialog.doc?.reference_number}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Reason for rejection"
            value={rejectDialog.reason}
            onChange={(e) => setRejectDialog({ ...rejectDialog, reason: e.target.value })}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialog({ open: false, doc: null, reason: '' })}>Cancel</Button>
          <Button
            onClick={handleReject}
            variant="contained"
            color="error"
          >
            Reject
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Registry
