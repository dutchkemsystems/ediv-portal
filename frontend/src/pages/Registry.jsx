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
} from '@mui/material'
import {
  Add as AddIcon,
  Description as DocIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Registry() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)
  const [openDialog, setOpenDialog] = useState(false)
  const [rejectDialog, setRejectDialog] = useState({ open: false, doc: null, reason: '' })
  const [formData, setFormData] = useState({
    title: '',
    document_type: 'CORRESPONDENCE',
    classification: 'INTERNAL',
  })

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/registry/documents/')
      setDocuments(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      await api.post('/registry/documents/', formData)
      notify.success('Document created successfully')
      setOpenDialog(false)
      fetchDocuments()
    } catch (error) {
      notify.error(error.response?.data?.detail || 'Failed to create document')
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">E-Registry Documents</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          New Document
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Documents"
            value={documents.length}
            icon={<DocIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Approved"
            value={documents.filter(d => d.status === 'APPROVED').length}
            icon={<DocIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending"
            value={documents.filter(d => d.status === 'PENDING').length}
            icon={<DocIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Rejected"
            value={documents.filter(d => d.status === 'REJECTED').length}
            icon={<DocIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="All Documents" />
          <Tab label="Pending Action" />
          <Tab label="Approved" />
        </Tabs>
      </Box>

      {/* Table */}
      <DataTable
        columns={columns}
        data={
          tabValue === 0 ? documents :
          tabValue === 1 ? documents.filter(d => d.status === 'PENDING') :
          documents.filter(d => d.status === 'APPROVED')
        }
        onView={(d) => console.log('View:', d)}
      />

      {/* Create Document Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Document</DialogTitle>
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
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.title}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

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
