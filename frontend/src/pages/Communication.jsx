import { useState, useEffect, useCallback } from 'react'
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
  OutlinedInput,
  Checkbox,
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
  Search as SearchIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

const MESSAGE_TYPES = [
  { value: 'INTERNAL', label: 'Internal' },
  { value: 'CIRCULAR', label: 'Circular' },
  { value: 'ANNOUNCEMENT', label: 'Announcement' },
  { value: 'ALERT', label: 'Alert' },
  { value: 'REMINDER', label: 'Reminder' },
]

const PRIORITIES = [
  { value: 'LOW', label: 'Low' },
  { value: 'NORMAL', label: 'Normal' },
  { value: 'HIGH', label: 'High' },
  { value: 'URGENT', label: 'Urgent' },
]

const MESSAGE_TYPE_COLORS = {
  INTERNAL: 'default',
  CIRCULAR: 'warning',
  ANNOUNCEMENT: 'primary',
  ALERT: 'error',
  REMINDER: 'info',
}

const PRIORITY_COLORS = {
  LOW: 'default',
  NORMAL: 'info',
  HIGH: 'error',
  URGENT: 'error',
}

const TARGET_AUDIENCES = [
  'ALL_STAFF',
  'TEACHING_STAFF',
  'NON_TEACHING_STAFF',
  'ADMIN_STAFF',
  'STUDENTS',
  'PARENTS',
  'DEPARTMENT_HEADS',
]

function Communication() {
  const [messages, setMessages] = useState([])
  const [circulars, setCirculars] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [viewMode, setViewMode] = useState('messages')
  const [formData, setFormData] = useState({
    subject: '',
    body: '',
    message_type: 'INTERNAL',
    priority: 'NORMAL',
    recipients: [],
    attachment: null,
    title: '',
    content: '',
    target_audience: 'ALL_STAFF',
    effective_date: '',
    expiry_date: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [formErrors, setFormErrors] = useState({})
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({ priority: '', message_type: '', is_read: '' })
  const [showFilters, setShowFilters] = useState(false)

  const fetchUsers = useCallback(async () => {
    try {
      const res = await api.get('/users/users/')
      setUsers(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }, [])

  const fetchMessages = useCallback(async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.priority) params.append('priority', filters.priority)
      if (filters.message_type) params.append('message_type', filters.message_type)
      if (filters.is_read) params.append('is_read', filters.is_read)
      if (searchTerm) params.append('search', searchTerm)
      const query = params.toString()
      const res = await api.get('/communication/messages/' + (query ? '?' + query : ''))
      setMessages(res.data.results || res.data)
    } catch (error) { /* silent */ } finally { setLoading(false) }
  }, [filters, searchTerm])

  const fetchCirculars = useCallback(async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.priority) params.append('priority', filters.priority)
      if (searchTerm) params.append('search', searchTerm)
      const query = params.toString()
      const res = await api.get('/communication/circulars/' + (query ? '?' + query : ''))
      setCirculars(res.data.results || res.data)
    } catch (error) { /* silent */ } finally { setLoading(false) }
  }, [filters, searchTerm])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  useEffect(() => {
    if (viewMode === 'messages') fetchMessages()
    else fetchCirculars()
  }, [fetchMessages, fetchCirculars, viewMode])

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => setFilters({ priority: '', message_type: '', is_read: '' })
  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  const resetFormData = () => ({
    subject: '',
    body: '',
    message_type: 'INTERNAL',
    priority: 'NORMAL',
    recipients: [],
    attachment: null,
    title: '',
    content: '',
    target_audience: 'ALL_STAFF',
    effective_date: '',
    expiry_date: '',
  })

  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData(resetFormData())
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    if (viewMode === 'messages') {
      setFormData({
        subject: item.subject || '',
        body: item.body || '',
        message_type: item.message_type || 'INTERNAL',
        priority: item.priority || 'NORMAL',
        recipients: item.recipients ? item.recipients.map(r => (r && typeof r === 'object') ? r.id : r) : [],
        attachment: null,
        title: '',
        content: '',
        target_audience: 'ALL_STAFF',
        effective_date: '',
        expiry_date: '',
      })
    } else {
      setFormData({
        subject: '',
        body: '',
        message_type: 'INTERNAL',
        priority: item.priority || 'NORMAL',
        recipients: [],
        attachment: null,
        title: item.title || '',
        content: item.content || '',
        target_audience: item.target_audience || 'ALL_STAFF',
        effective_date: item.effective_date || '',
        expiry_date: item.expiry_date || '',
      })
    }
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const handleDelete = async () => {
    try {
      const endpoint = viewMode === 'messages' ? 'messages' : 'circulars'
      await api.delete('/communication/' + endpoint + '/' + selectedItem.id + '/')
      notify.success('Deleted successfully')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      if (viewMode === 'messages') fetchMessages()
      else fetchCirculars()
    } catch (error) {
      notify.error('Failed to delete')
    }
  }

  const buildMessagePayload = () => {
    const payload = new FormData()
    payload.append('subject', formData.subject)
    payload.append('body', formData.body)
    payload.append('message_type', formData.message_type)
    payload.append('priority', formData.priority)
    formData.recipients.forEach(id => payload.append('recipients', id))
    if (formData.attachment) payload.append('attachment', formData.attachment)
    return payload
  }

  const buildCircularPayload = () => {
    const payload = new FormData()
    payload.append('title', formData.title)
    payload.append('content', formData.content)
    payload.append('priority', formData.priority)
    payload.append('target_audience', formData.target_audience)
    if (formData.effective_date) payload.append('effective_date', formData.effective_date)
    if (formData.expiry_date) payload.append('expiry_date', formData.expiry_date)
    return payload
  }

  const validateForm = () => {
    const errors = {}
    if (viewMode === 'messages') {
      if (!formData.subject.trim()) errors.subject = 'Subject is required'
      if (!formData.body.trim()) errors.body = 'Body is required'
      if (formData.recipients.length === 0) errors.recipients = 'Select at least one recipient'
    } else {
      if (!formData.title.trim()) errors.title = 'Title is required'
      if (!formData.content.trim()) errors.content = 'Content is required'
      if (!formData.effective_date) errors.effective_date = 'Effective date is required'
      if (!formData.expiry_date) errors.expiry_date = 'Expiry date is required'
    }
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return
    setSubmitting(true)
    try {
      const endpoint = viewMode === 'messages' ? 'messages' : 'circulars'
      const payload = viewMode === 'messages' ? buildMessagePayload() : buildCircularPayload()
      if (selectedItem) {
        await api.put('/communication/' + endpoint + '/' + selectedItem.id + '/', payload)
        notify.success('Updated successfully')
      } else {
        await api.post('/communication/' + endpoint + '/', payload)
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
        if (firstKey) {
          const val = data[firstKey]
          msg = Array.isArray(val) ? firstKey + ': ' + val[0] : firstKey + ': ' + val
        }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const getMessageTypeColor = (type) => MESSAGE_TYPE_COLORS[type] || 'default'
  const getPriorityColor = (priority) => PRIORITY_COLORS[priority] || 'default'

  const resolveUserName = (sender) => {
    if (!sender) return '-'
    if (typeof sender === 'object') return sender.get_full_name || sender.username || '-'
    const user = users.find(u => u.id === sender)
    return user ? (user.get_full_name || user.username) : String(sender)
  }

  const resolveRecipientNames = (recipients) => {
    if (!recipients || recipients.length === 0) return '-'
    const names = recipients.map(r => {
      if (typeof r === 'object') return r.get_full_name || r.username
      const user = users.find(u => u.id === r)
      return user ? (user.get_full_name || user.username) : String(r)
    })
    return names.length > 2 ? names[0] + ', ' + names[1] + ' +' + (names.length - 2) : names.join(', ')
  }

  const columns = [
    { id: 'subject', label: 'Subject' },
    { id: 'sender', label: 'From', render: (row) => resolveUserName(row.sender) },
    { id: 'recipients', label: 'To', render: (row) => resolveRecipientNames(row.recipients) },
    { id: 'message_type', label: 'Type', render: (row) => (
      <Chip label={row.message_type || 'INTERNAL'} size="small" color={getMessageTypeColor(row.message_type)} />
    )},
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
    { id: 'is_read', label: 'Status', render: (row) => (
      <Chip
        icon={row.is_read ? <ReadIcon /> : <UnreadIcon />}
        label={row.is_read ? 'Read' : 'Unread'}
        size="small"
        color={row.is_read ? 'default' : 'primary'}
        variant={row.is_read ? 'outlined' : 'filled'}
      />
    )},
    { id: 'created_at', label: 'Date', render: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' },
  ]

  const circularColumns = [
    { id: 'title', label: 'Title' },
    { id: 'issued_by', label: 'Issued By', render: (row) => resolveUserName(row.issued_by) },
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
    { id: 'target_audience', label: 'Audience', render: (row) => (
      <Chip label={row.target_audience || 'ALL_STAFF'} size="small" variant="outlined" />
    )},
    { id: 'effective_date', label: 'Effective', render: (row) => row.effective_date || '-' },
    { id: 'expiry_date', label: 'Expires', render: (row) => row.expiry_date || '-' },
  ]

  if (loading) {
    return <Loading message="Loading communications..." />
  }

  const filteredMessages = searchTerm
    ? messages.filter(m => (m.subject && m.subject.toLowerCase().includes(searchTerm.toLowerCase())) || (m.body && m.body.toLowerCase().includes(searchTerm.toLowerCase())))
    : messages

  const filteredCirculars = searchTerm
    ? circulars.filter(c => (c.title && c.title.toLowerCase().includes(searchTerm.toLowerCase())) || (c.content && c.content.toLowerCase().includes(searchTerm.toLowerCase())))
    : circulars

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Communication & Messaging</Typography>
          <Typography variant="body2" color="text.secondary">
            {viewMode === 'messages' ? messages.length + ' messages' : circulars.length + ' circulars'}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} alignItems="center">
          <Button variant={viewMode === 'messages' ? 'contained' : 'outlined'} onClick={() => { setViewMode('messages'); clearFilters() }}
            sx={viewMode === 'messages' ? { bgcolor: '#C8102E', '&:hover': { bgcolor: '#a00d24' } } : {}}>
            Messages
          </Button>
          <Button variant={viewMode === 'circulars' ? 'contained' : 'outlined'} onClick={() => { setViewMode('circulars'); clearFilters() }}
            sx={viewMode === 'circulars' ? { bgcolor: '#C8102E', '&:hover': { bgcolor: '#a00d24' } } : {}}>
            Circulars
          </Button>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
            sx={{ bgcolor: '#C8102E', '&:hover': { bgcolor: '#a00d24' } }}>
            New {viewMode === 'messages' ? 'Message' : 'Circular'}
          </Button>
        </Stack>
      </Box>

      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder={viewMode === 'messages' ? 'Search messages...' : 'Search circulars...'}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }}
        />
      </Box>

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
                    {PRIORITIES.map(p => <MenuItem key={p.value} value={p.value}>{p.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Type</InputLabel>
                  <Select value={filters.message_type} onChange={(e) => handleFilterChange('message_type', e.target.value)} label="Type">
                    <MenuItem value="">All Types</MenuItem>
                    {MESSAGE_TYPES.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
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
                  <InputLabel>Priority</InputLabel>
                  <Select value={filters.priority} onChange={(e) => handleFilterChange('priority', e.target.value)} label="Priority">
                    <MenuItem value="">All Priorities</MenuItem>
                    {PRIORITIES.map(p => <MenuItem key={p.value} value={p.value}>{p.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </Paper>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Messages" value={messages.length} icon={<MessageIcon />} color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Unread" value={messages.filter(m => !m.is_read).length} icon={<UnreadIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Circulars" value={circulars.length} icon={<CircularIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Urgent" value={messages.filter(m => m.priority === 'URGENT').length + circulars.filter(c => c.priority === 'URGENT').length} icon={<MessageIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {viewMode === 'messages' ? (
        <DataTable columns={columns} data={filteredMessages} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      ) : (
        <DataTable columns={circularColumns} data={filteredCirculars} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}

      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {viewMode === 'messages'
            ? (selectedItem ? 'Edit Message' : 'New Message')
            : (selectedItem ? 'Edit Circular' : 'New Circular')}
        </DialogTitle>
        <DialogContent>
          {viewMode === 'messages' ? (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField fullWidth label="Subject" required value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  error={!!formErrors.subject} helperText={formErrors.subject} />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth error={!!formErrors.recipients}>
                  <InputLabel>Recipients</InputLabel>
                  <Select
                    multiple
                    value={formData.recipients}
                    onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
                    input={<OutlinedInput label="Recipients" />}
                    renderValue={(selected) => {
                      if (selected.length === 0) return <em>Select recipients</em>
                      return selected.map(id => {
                        const user = users.find(u => u.id === id)
                        return user ? (user.get_full_name || user.username) : id
                      }).join(', ')
                    }}
                  >
                    {users.map(user => (
                      <MenuItem key={user.id} value={user.id}>
                        <Checkbox checked={formData.recipients.indexOf(user.id) > -1} />
                        <InputLabel sx={{ ml: 1 }}>{user.get_full_name || user.username}</InputLabel>
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.recipients && <Typography variant="caption" color="error">{formErrors.recipients}</Typography>}
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Body" multiline rows={4} required value={formData.body}
                  onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                  error={!!formErrors.body} helperText={formErrors.body} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Message Type</InputLabel>
                  <Select value={formData.message_type}
                    onChange={(e) => setFormData({ ...formData, message_type: e.target.value })}
                    label="Message Type">
                    {MESSAGE_TYPES.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    label="Priority">
                    {PRIORITIES.map(p => <MenuItem key={p.value} value={p.value}>{p.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Button variant="outlined" component="label" fullWidth>
                  {formData.attachment ? formData.attachment.name : 'Attach File (optional)'}
                  <input type="file" hidden onChange={(e) => setFormData({ ...formData, attachment: e.target.files[0] || null })} />
                </Button>
              </Grid>
            </Grid>
          ) : (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField fullWidth label="Title" required value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  error={!!formErrors.title} helperText={formErrors.title} />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Content" multiline rows={4} required value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  error={!!formErrors.content} helperText={formErrors.content} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    label="Priority">
                    {PRIORITIES.map(p => <MenuItem key={p.value} value={p.value}>{p.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Target Audience</InputLabel>
                  <Select value={formData.target_audience}
                    onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                    label="Target Audience">
                    {TARGET_AUDIENCES.map(a => <MenuItem key={a} value={a}>{a.replace(/_/g, ' ')}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Effective Date" type="date" required
                  InputLabelProps={{ shrink: true }} value={formData.effective_date}
                  onChange={(e) => setFormData({ ...formData, effective_date: e.target.value })}
                  error={!!formErrors.effective_date} helperText={formErrors.effective_date} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Expiry Date" type="date" required
                  InputLabelProps={{ shrink: true }} value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  error={!!formErrors.expiry_date} helperText={formErrors.expiry_date} />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#C8102E', '&:hover': { bgcolor: '#a00d24' } }}>
            {submitting ? 'Sending...' : selectedItem ? 'Update' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {viewMode === 'messages' ? 'Message' : 'Circular'} Details
          {selectedItem?.priority && <Chip label={selectedItem.priority} size="small" sx={{ ml: 1 }} color={getPriorityColor(selectedItem.priority)} />}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Box>
              <Typography variant="h6" gutterBottom>{selectedItem.subject || selectedItem.title}</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                {selectedItem.message_type && <Chip label={selectedItem.message_type} size="small" color={getMessageTypeColor(selectedItem.message_type)} />}
                {selectedItem.target_audience && <Chip label={selectedItem.target_audience} size="small" variant="outlined" />}
                {selectedItem.is_read !== undefined && (
                  <Chip icon={selectedItem.is_read ? <ReadIcon /> : <UnreadIcon />}
                    label={selectedItem.is_read ? 'Read' : 'Unread'} size="small"
                    color={selectedItem.is_read ? 'default' : 'primary'} variant={selectedItem.is_read ? 'outlined' : 'filled'} />
                )}
              </Box>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body2" color="text.secondary" gutterBottom>
                From: {resolveUserName(selectedItem.sender || selectedItem.issued_by)}
                {viewMode === 'messages' && ' | To: ' + resolveRecipientNames(selectedItem.recipients)}
                {selectedItem.effective_date && ' | Effective: ' + selectedItem.effective_date}
                {selectedItem.expiry_date && ' | Expires: ' + selectedItem.expiry_date}
                {selectedItem.created_at && ' | Date: ' + new Date(selectedItem.created_at).toLocaleDateString()}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body1" sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
                {selectedItem.body || selectedItem.content || 'No content available.'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />} onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }} sx={{ bgcolor: '#C8102E' }}>Edit</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog open={openDeleteDialog} title={'Delete ' + (viewMode === 'messages' ? 'Message' : 'Circular')}
        message={'Are you sure you want to delete "' + (selectedItem?.subject || selectedItem?.title || '') + '"? This action cannot be undone.'}
        onConfirm={handleDelete} onCancel={() => setOpenDeleteDialog(false)} confirmText="Delete" severity="error" />
    </Box>
  )
}

export default Communication