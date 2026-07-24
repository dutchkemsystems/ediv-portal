import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
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
} from '@mui/material'
import {
  Add as AddIcon,
  FolderOpen as FileIcon,
  MoveUp as MoveIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Files() {
  const [files, setFiles] = useState([])
  const [movements, setMovements] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openMovementDialog, setOpenMovementDialog] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    file_type: 'CORRESPONDENCE',
    status: 'ACTIVE',
    classification: 'INTERNAL',
    priority: 'NORMAL',
  })
  const [moveData, setMoveData] = useState({
    to_holder_id: '',
    action: 'Forwarded',
    remarks: '',
    expected_return_date: '',
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
      notify.error('Failed to load files')
    } finally {
      setLoading(false)
    }
  }

  const fetchMovements = async () => {
    try {
      const response = await api.get('/files/movements/')
      setMovements(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load file movements')
    }
  }

  const handleAdd = () => {
    setSelectedFile(null)
    setFormData({
      title: '',
      file_type: 'CORRESPONDENCE',
      status: 'ACTIVE',
      classification: 'INTERNAL',
      priority: 'NORMAL',
    })
    setOpenDialog(true)
  }

  const handleMove = (file) => {
    setSelectedFile(file)
    setMoveData({ to_holder_id: '', action: 'Forwarded', remarks: '', expected_return_date: '' })
    setOpenMovementDialog(true)
  }

  const handleReceive = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/receive/`)
      notify.success('File received successfully')
      fetchFiles()
      fetchMovements()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to receive file')
    }
  }

  const handleClose = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/close/`)
      notify.success('File archived successfully')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to close file')
    }
  }

  const handleSubmitMove = async () => {
    try {
      await api.post(`/files/files/${selectedFile.id}/move/`, {
        to_holder_id: parseInt(moveData.to_holder_id),
        action: moveData.action,
        remarks: moveData.remarks,
        expected_return_date: moveData.expected_return_date || undefined,
      })
      notify.success('File moved successfully')
      setOpenMovementDialog(false)
      fetchFiles()
      fetchMovements()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to move file')
    }
  }

  const handleSubmit = async () => {
    try {
      await api.post('/files/files/', formData)
      notify.success('File created successfully')
      setOpenDialog(false)
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.detail || 'Failed to create file')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'PENDING': return 'warning'
      case 'IN_TRANSIT': return 'info'
      case 'ARCHIVED': return 'default'
      case 'CLOSED': return 'error'
      default: return 'default'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'error'
      case 'URGENT': return 'error'
      case 'NORMAL': return 'info'
      case 'LOW': return 'default'
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
    { id: 'classification', label: 'Classification' },
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
        onEdit={handleMove}
        onDelete={handleClose}
        onView={handleViewMovement}
      />

      {/* Create File Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New File</DialogTitle>
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
                <InputLabel>File Type</InputLabel>
                <Select
                  value={formData.file_type}
                  onChange={(e) => setFormData({ ...formData, file_type: e.target.value })}
                  label="File Type"
                >
                  <MenuItem value="CORRESPONDENCE">Correspondence</MenuItem>
                  <MenuItem value="MEMO">Memo</MenuItem>
                  <MenuItem value="CIRCULAR">Circular</MenuItem>
                  <MenuItem value="REPORT">Report</MenuItem>
                  <MenuItem value="MINUTES">Minutes</MenuItem>
                  <MenuItem value="POLICY">Policy</MenuItem>
                  <MenuItem value="CONTRACT">Contract</MenuItem>
                  <MenuItem value="INVOICE">Invoice</MenuItem>
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
            disabled={!formData.title}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Move File Dialog */}
      <Dialog open={openMovementDialog} onClose={() => setOpenMovementDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MoveIcon />
          Move File — {selectedFile?.file_number}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                type="number"
                label="Recipient User ID"
                value={moveData.to_holder_id}
                onChange={(e) => setMoveData({ ...moveData, to_holder_id: e.target.value })}
                helperText="Enter the user ID of the person to move this file to"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Action</InputLabel>
                <Select
                  value={moveData.action}
                  onChange={(e) => setMoveData({ ...moveData, action: e.target.value })}
                  label="Action"
                >
                  <MenuItem value="Forwarded">Forwarded</MenuItem>
                  <MenuItem value="Returned">Returned</MenuItem>
                  <MenuItem value="Reviewed">Reviewed</MenuItem>
                  <MenuItem value="Approved">Approved</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Remarks"
                multiline
                rows={2}
                value={moveData.remarks}
                onChange={(e) => setMoveData({ ...moveData, remarks: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="date"
                label="Expected Return Date"
                value={moveData.expected_return_date}
                onChange={(e) => setMoveData({ ...moveData, expected_return_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMovementDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitMove}
            variant="contained"
            disabled={!moveData.to_holder_id}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Move File
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Files
