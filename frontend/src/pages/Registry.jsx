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
  Description as FileIcon,
  MoveToInbox as MovementIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import api from '../api/client'

function Registry() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)
  const [openDialog, setOpenDialog] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    file_type: '',
    classification: 'INTERNAL',
    priority: 'NORMAL',
  })

  useEffect(() => {
    fetchFiles()
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

  const handleSubmit = async () => {
    try {
      await api.post('/files/files/', formData)
      setOpenDialog(false)
      fetchFiles()
    } catch (error) {
      console.error('Error creating file:', error)
    }
  }

  const columns = [
    { id: 'file_number', label: 'File Number' },
    { id: 'title', label: 'Title' },
    { id: 'file_type', label: 'Type', render: (row) => (
      <Chip label={row.file_type} size="small" />
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={
          row.status === 'ACTIVE' ? 'success' :
          row.status === 'PENDING' ? 'warning' :
          row.status === 'IN_TRANSIT' ? 'info' : 'default'
        }
      />
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
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip
        label={row.priority}
        size="small"
        color={
          row.priority === 'URGENT' ? 'error' :
          row.priority === 'HIGH' ? 'warning' :
          row.priority === 'NORMAL' ? 'info' : 'default'
        }
      />
    )},
    { id: 'current_holder_name', label: 'Current Holder' },
    { id: 'created_at', label: 'Created', render: (row) => new Date(row.created_at).toLocaleDateString() },
  ]

  if (loading) {
    return <Loading message="Loading registry..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">E-Registry</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Create File
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
            title="In Transit"
            value={files.filter(f => f.status === 'IN_TRANSIT').length}
            icon={<MovementIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="All Files" />
          <Tab label="My Files" />
          <Tab label="Pending Action" />
        </Tabs>
      </Box>

      {/* Table */}
      <DataTable
        columns={columns}
        data={files}
        onEdit={(f) => console.log('Edit:', f)}
        onView={(f) => console.log('View:', f)}
      />

      {/* Create File Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New File</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="File Title"
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
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Registry
