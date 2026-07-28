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
  FolderOpen as FileIcon,
  History as HistoryIcon,
  MoveUp as MoveIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Files() {
  const [files, setFiles] = useState([])
  const [movements, setMovements] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openMovementDialog, setOpenMovementDialog] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [formData, setFormData] = useState({
    file_number: '',
    title: '',
    file_type: '',
    status: 'ACTIVE',
    current_holder: '',
    priority: 'NORMAL',
  })

  useEffect(() => {
    fetchFiles()
    fetchMovements()
  }, [])

  const fetchFiles = async () => {
    try {
      const response = await api.get('/files/files/')
      setFiles(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching files:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchMovements = async () => {
    try {
      const response = await api.get('/files/movements/')
      setMovements(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching movements:', error)
    }
  }

  const handleAdd = () => {
    setSelectedFile(null)
    setFormData({
      file_number: '',
      title: '',
      file_type: '',
      status: 'ACTIVE',
      current_holder: '',
      priority: 'NORMAL',
    })
    setOpenDialog(true)
  }

  const handleEdit = (file) => {
    setSelectedFile(file)
    setFormData({
      file_number: file.file_number,
      title: file.title,
      file_type: file.file_type,
      status: file.status,
      current_holder: file.current_holder,
      priority: file.priority || 'NORMAL',
    })
    setOpenDialog(true)
  }

  const handleDelete = (file) => {
    setSelectedFile(file)
    setOpenDeleteDialog(true)
  }

  const handleViewMovement = (file) => {
    setSelectedFile(file)
    setOpenMovementDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedFile) {
        await api.put(`/files/files/${selectedFile.id}/`, formData)
      } else {
        await api.post('/files/files/', formData)
      }
      setOpenDialog(false)
      fetchFiles()
    } catch (error) {
      console.error('Error saving file:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/files/files/${selectedFile.id}/`)
      setOpenDeleteDialog(false)
      fetchFiles()
    } catch (error) {
      console.error('Error deleting file:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'PENDING': return 'warning'
      case 'ARCHIVED': return 'default'
      case 'CONFIDENTIAL': return 'error'
      default: return 'default'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'error'
      case 'NORMAL': return 'warning'
      case 'LOW': return 'info'
      case 'URGENT': return 'error'
      default: return 'default'
    }
  }

  const getFileMovements = (fileId) => {
    return movements.filter(m => m.file === fileId || m.file_id === fileId)
  }

  const columns = [
    { id: 'file_number', label: 'File Number' },
    { id: 'title', label: 'Title' },
    { id: 'file_type', label: 'Type' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
    { id: 'current_holder_name', label: 'Current Holder' },
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading files..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">E-Registry File Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          New File
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Files"
            value={files.length}
            icon={<FileIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Files"
            value={files.filter(f => f.status === 'ACTIVE').length}
            icon={<FileIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Files"
            value={files.filter(f => f.status === 'PENDING').length}
            icon={<FileIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Archived Files"
            value={files.filter(f => f.status === 'ARCHIVED').length}
            icon={<FileIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={files}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleViewMovement}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedFile ? 'Edit File' : 'New File'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="File Number"
                value={formData.file_number}
                onChange={(e) => setFormData({ ...formData, file_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>File Type</InputLabel>
                <Select
                  value={formData.file_type || ''}
                  onChange={(e) => setFormData({ ...formData, file_type: e.target.value })}
                  label="File Type"
                >
                  <MenuItem value="LETTER">Letter</MenuItem>
                  <MenuItem value="MEMO">Memo</MenuItem>
                  <MenuItem value="REPORT">Report</MenuItem>
                  <MenuItem value="FORM">Form</MenuItem>
                  <MenuItem value="CONTRACT">Contract</MenuItem>
                  <MenuItem value="POLICY">Policy</MenuItem>
                  <MenuItem value="APPLICATION">Application</MenuItem>
                  <MenuItem value="INVOICE">Invoice</MenuItem>
                  <MenuItem value="RECEIPT">Receipt</MenuItem>
                  <MenuItem value="MINUTES">Minutes</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="PENDING">Pending</MenuItem>
                  <MenuItem value="ARCHIVED">Archived</MenuItem>
                  <MenuItem value="IN_TRANSIT">In Transit</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Current Holder (User ID)"
                value={formData.current_holder}
                onChange={(e) => setFormData({ ...formData, current_holder: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  label="Priority"
                >
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="NORMAL">Normal</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="URGENT">Urgent</MenuItem>
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
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {selectedFile ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Movement History Dialog */}
      <Dialog open={openMovementDialog} onClose={() => setOpenMovementDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HistoryIcon />
          File Movement History - {selectedFile?.file_number}
        </DialogTitle>
        <DialogContent>
          {selectedFile && (
            <List>
              {getFileMovements(selectedFile.id).length === 0 ? (
                <ListItem>
                  <ListItemText primary="No movement history recorded" />
                </ListItem>
              ) : (
                getFileMovements(selectedFile.id).map((movement, index) => (
                  <ListItem key={movement.id || index} divider>
                    <ListItemIcon>
                      <MoveIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${movement.from_holder_name || movement.from_holder || 'Origin'} → ${movement.to_holder_name || movement.to_holder || 'Destination'}`}
                      secondary={movement.movement_date || movement.created_at || 'No date'}
                    />
                  </ListItem>
                ))
              )}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMovementDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete File"
        message={`Are you sure you want to delete file ${selectedFile?.file_number}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Files
