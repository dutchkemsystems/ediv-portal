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
  Divider,
  Paper,
  Stack,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Mail as MessageIcon,
  Campaign as CircularIcon,
  MarkEmailRead as ReadIcon,
  MarkEmailUnread as UnreadIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Communication() {
  const [messages, setMessages] = useState([])
  const [circulars, setCirculars] = useState([])
  const [loading, setLoading] = useState(true)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [viewMode, setViewMode] = useState('messages')
  const [formData, setFormData] = useState({ subject: '', sender: '', recipient: '', message: '', priority: 'NORMAL', category: 'GENERAL', date_sent: '' })
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [filters, setFilters] = useState({ priority: '', category: '', is_read: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchMessages()
    fetchCirculars()
  }, [])

  useEffect(() => {
    if (viewMode === 'messages') fetchMessages()
    if (viewMode === 'circulars') fetchCirculars()
  }, [filters, viewMode])

  const fetchMessages = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.priority) params.append('priority', filters.priority)
      if (filters.is_read) params.append('is_read', filters.is_read)
      const query = params.toString()
      const res = await api.get(`/communication/messages/${query ? `?${query}` : ''}`)
      setMessages(res.data.results || res.data)
    } catch (error) { /* silent */ } finally { setLoading(false) }
  }

  const fetchCirculars = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.category) params.append('category', filters.category)
      const query = params.toString()
      const res = await api.get(`/communication/circulars/${query ? `?${query}` : ''}`)
      setCirculars(res.data.results || res.data)
    } catch (error) { /* silent */ } finally { setLoading(false) }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => setFilters({ priority: '', category: '', is_read: '' })
  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData({ subject: '', sender: '', recipient: '', message: '', priority: 'NORMAL', category: 'GENERAL', date_sent: '' })
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      subject: item.subject || '',
      sender: item.sender || '',
      recipient: item.recipient || '',
      message: item.message || item.content || '',
      priority: item.priority || 'NORMAL',
      category: item.category || 'GENERAL',
      date_sent: item.date_sent || '',
    })
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const handleDelete = async () => {
    try {
      const endpoint = viewMode === 'messages' ? 'messages' : 'circulars'
      await api.delete(`/communication/${endpoint}/${selectedItem.id}/`)
      notify.success('Deleted successfully')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      if (viewMode === 'messages') fetchMessages()
      else fetchCirculars()
    } catch (error) {
      notify.error('Failed to delete')
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const endpoint = viewMode === 'messages' ? 'messages' : 'circulars'
      if (selectedItem) {
        await api.put(`/communication/${endpoint}/${selectedItem.id}/`, formData)
        notify.success('Updated successfully')
      } else {
        await api.post(`/communication/${endpoint}/`, formData)
        notify.success('Created successfully')
      }
      setOpenFormDialog(false)
      setSelectedItem(null)
      if (viewMode === 'messages') fetchMessages()
      else fetchCirculars()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        if (firstKey) { const val = data[firstKey]; msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}` }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'error'
      case 'NORMAL': return 'info'
      case 'LOW': return 'default'
      default: return 'default'
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'ANNOUNCEMENT': return 'primary'
      case 'URGENT': return 'error'
      case 'GENERAL': return 'default'
      case 'ACADEMIC': return 'success'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'subject', label: 'Subject' },
    { id: 'sender', label: 'From' },
    { id: 'recipient', label: 'To' },
    { id: 'read', label: 'Status', render: (row) => (
      <Chip
        icon={row.read ? <ReadIcon /> : <UnreadIcon />}
        label={row.read ? 'Read' : 'Unread'}
        size="small"
        color={row.read ? 'default' : 'primary'}
        variant={row.read ? 'outlined' : 'filled'}
      />
    )},
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category || 'GENERAL'} size="small" color={getCategoryColor(row.category)} />
    )},
    { id: 'date_sent', label: 'Date' },
  ]

  const circularColumns = [
    { id: 'subject', label: 'Subject' },
    { id: 'sender', label: 'From' },
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category || 'GENERAL'} size="small" color={getCategoryColor(row.category)} />
    )},
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
    { id: 'date_sent', label: 'Date' },
  ]

  if (loading) {
    return <Loading message="Loading communications..." />
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Communication & Messaging</Typography>
          <Typography variant="body2" color="text.secondary">
            {viewMode === 'messages' ? `${messages.length} messages` : `${circulars.length} circulars`}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant={viewMode === 'messages' ? 'contained' : 'outlined'} onClick={() => { setViewMode('messages'); setShowFilters(false) }}
            sx={viewMode === 'messages' ? { bgcolor: '#1a237e' } : {}}>
            Messages
          </Button>
          <Button variant={viewMode === 'circulars' ? 'contained' : 'outlined'} onClick={() => { setViewMode('circulars'); setShowFilters(false) }}
            sx={viewMode === 'circulars' ? { bgcolor: '#f57c00' } : {}}>
            Circulars
          </Button>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            New {viewMode === 'messages' ? 'Message' : 'Circular'}
          </Button>
        </Stack>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter {viewMode === 'messages' ? 'Messages' : 'Circulars'}</Typography>
            {hasActiveFilters && <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>}
          </Box>
          {viewMode === 'messages' ? (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Priority</InputLabel>
                  <Select value={filters.priority} onChange={(e) => handleFilterChange('priority', e.target.value)} label="Priority">
                    <MenuItem value="">All Priorities</MenuItem>
                    <MenuItem value="HIGH">High</MenuItem>
                    <MenuItem value="NORMAL">Normal</MenuItem>
                    <MenuItem value="LOW">Low</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select value={filters.is_read} onChange={(e) => handleFilterChange('is_read', e.target.value)} label="Status">
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="false">Unread</MenuItem>
                    <MenuItem value="true">Read</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select value={filters.category} onChange={(e) => handleFilterChange('category', e.target.value)} label="Category">
                    <MenuItem value="">All Categories</MenuItem>
                    <MenuItem value="ANNOUNCEMENT">Announcement</MenuItem>
                    <MenuItem value="URGENT">Urgent</MenuItem>
                    <MenuItem value="GENERAL">General</MenuItem>
                    <MenuItem value="ACADEMIC">Academic</MenuItem>
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
          <StatCard
            title="Total Messages"
            value={messages.length}
            icon={<MessageIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread"
            value={messages.filter(m => !m.read).length}
            icon={<UnreadIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Circulars"
            value={circulars.length}
            icon={<CircularIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Announcements"
            value={circulars.filter(c => c.category === 'ANNOUNCEMENT').length + messages.filter(m => m.category === 'ANNOUNCEMENT').length}
            icon={<MessageIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      {viewMode === 'messages' ? (
        <DataTable columns={columns} data={messages} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      ) : (
        <DataTable columns={circularColumns} data={circulars} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{selectedItem ? 'Edit Message' : 'New Message'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Sender"
                value={formData.sender}
                onChange={(e) => setFormData({ ...formData, sender: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Recipient"
                value={formData.recipient}
                onChange={(e) => setFormData({ ...formData, recipient: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message"
                multiline
                rows={4}
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  label="Priority"
                >
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="NORMAL">Normal</MenuItem>
                  <MenuItem value="LOW">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  label="Category"
                >
                  <MenuItem value="GENERAL">General</MenuItem>
                  <MenuItem value="ANNOUNCEMENT">Announcement</MenuItem>
                  <MenuItem value="URGENT">Urgent</MenuItem>
                  <MenuItem value="ACADEMIC">Academic</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Date Sent"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.date_sent}
                onChange={(e) => setFormData({ ...formData, date_sent: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {submitting ? 'Sending...' : selectedItem ? 'Update' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {viewMode === 'messages' ? 'Message' : 'Circular'} Details
          {selectedItem?.priority && <Chip label={selectedItem.priority} size="small" sx={{ ml: 1 }} color={getPriorityColor(selectedItem.priority)} />}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Box>
              <Typography variant="h6" gutterBottom>{selectedItem.subject}</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                {selectedItem.category && <Chip label={selectedItem.category} size="small" color={getCategoryColor(selectedItem.category)} />}
                {selectedItem.read !== undefined && (
                  <Chip icon={selectedItem.read ? <ReadIcon /> : <UnreadIcon />}
                    label={selectedItem.read ? 'Read' : 'Unread'} size="small"
                    color={selectedItem.read ? 'default' : 'primary'} variant={selectedItem.read ? 'outlined' : 'filled'} />
                )}
              </Box>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body2" color="text.secondary" gutterBottom>
                From: {selectedItem.sender} | To: {selectedItem.recipient || 'All'} | Date: {selectedItem.date_sent}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
                {selectedItem.message || selectedItem.content || 'No content available.'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />} onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }} sx={{ bgcolor: '#1a237e' }}>Edit</Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog open={openDeleteDialog} title="Delete Message"
        message={`Are you sure you want to delete "${selectedItem?.subject}"? This action cannot be undone.`}
        onConfirm={handleDelete} onCancel={() => setOpenDeleteDialog(false)} confirmText="Delete" severity="error" />
    </Box>
  )
}

export default Communication
