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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Mail as MessageIcon,
  Campaign as CircularIcon,
  MarkEmailRead as ReadIcon,
  MarkEmailUnread as UnreadIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Communication() {
  const [messages, setMessages] = useState([])
  const [circulars, setCirculars] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openCircularDialog, setOpenCircularDialog] = useState(false)
  const [selectedMessage, setSelectedMessage] = useState(null)
  const [viewMode, setViewMode] = useState('messages')
  const [formData, setFormData] = useState({
    subject: '',
    sender: '',
    recipient: '',
    message: '',
    priority: 'NORMAL',
    category: 'GENERAL',
    date_sent: '',
  })

  useEffect(() => {
    fetchMessages()
    fetchCirculars()
  }, [])

  const fetchMessages = async () => {
    try {
      const response = await api.get('/communication/messages/')
      setMessages(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCirculars = async () => {
    try {
      const response = await api.get('/communication/circulars/')
      setCirculars(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching circulars:', error)
    }
  }

  const handleAdd = () => {
    setSelectedMessage(null)
    setFormData({
      subject: '',
      sender: '',
      recipient: '',
      message: '',
      priority: 'NORMAL',
      category: 'GENERAL',
      date_sent: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (message) => {
    setSelectedMessage(message)
    setFormData({
      subject: message.subject,
      sender: message.sender,
      recipient: message.recipient,
      message: message.message,
      priority: message.priority || 'NORMAL',
      category: message.category || 'GENERAL',
      date_sent: message.date_sent || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (message) => {
    setSelectedMessage(message)
    setOpenDeleteDialog(true)
  }

  const handleViewCircular = (circular) => {
    setSelectedMessage(circular)
    setOpenCircularDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedMessage) {
        await api.put(`/communication/messages/${selectedMessage.id}/`, formData)
      } else {
        await api.post('/communication/messages/', formData)
      }
      setOpenDialog(false)
      fetchMessages()
    } catch (error) {
      console.error('Error saving message:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/communication/messages/${selectedMessage.id}/`)
      setOpenDeleteDialog(false)
      fetchMessages()
    } catch (error) {
      console.error('Error deleting message:', error)
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Communication & Messaging</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={viewMode === 'messages' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('messages')}
            sx={viewMode === 'messages' ? { bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } } : {}}
          >
            Messages
          </Button>
          <Button
            variant={viewMode === 'circulars' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('circulars')}
            sx={viewMode === 'circulars' ? { bgcolor: '#f57c00', '&:hover': { bgcolor: '#e65100' } } : {}}
          >
            Circulars
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAdd}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            New Message
          </Button>
        </Box>
      </Box>

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
        <DataTable
          columns={columns}
          data={messages}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={(msg) => console.log('View:', msg)}
        />
      ) : (
        <DataTable
          columns={circularColumns}
          data={circulars}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleViewCircular}
        />
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedMessage ? 'Edit Message' : 'New Message'}</DialogTitle>
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
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {selectedMessage ? 'Update' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Circular View Dialog */}
      <Dialog open={openCircularDialog} onClose={() => setOpenCircularDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularIcon />
          Circular Details
        </DialogTitle>
        <DialogContent>
          {selectedMessage && (
            <Box>
              <Typography variant="h6" gutterBottom>{selectedMessage.subject}</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={selectedMessage.priority || 'NORMAL'} size="small" color={getPriorityColor(selectedMessage.priority)} />
                <Chip label={selectedMessage.category || 'GENERAL'} size="small" color={getCategoryColor(selectedMessage.category)} />
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                From: {selectedMessage.sender} | Date: {selectedMessage.date_sent}
              </Typography>
              <Typography variant="body1" sx={{ mt: 2 }}>
                {selectedMessage.message || selectedMessage.content || 'No content available.'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCircularDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Message"
        message={`Are you sure you want to delete "${selectedMessage?.subject}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Communication
