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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Stack,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  AccountTree as WorkflowIcon,
  Assignment as TaskIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

function Workflows() {
  const [workflows, setWorkflows] = useState([])
  const [tasks, setTasks] = useState([])
  const [instances, setInstances] = useState([])
  const [loading, setLoading] = useState(true)
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openTasksDialog, setOpenTasksDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState({ name: '', description: '', status: 'DRAFT', trigger_type: '', assigned_to: '', due_date: '' })
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [filters, setFilters] = useState({ status: '', trigger_type: '' })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchAll()
  }, [])

  useEffect(() => {
    fetchWorkflows()
  }, [filters])

  const fetchAll = async () => {
    try {
      setLoading(true)
      await Promise.all([fetchWorkflows(), fetchTasks(), fetchInstances()])
    } finally {
      setLoading(false)
    }
  }

  const fetchWorkflows = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.trigger_type) params.append('trigger_type', filters.trigger_type)
      const query = params.toString()
      const res = await api.get(`/workflows/workflows/${query ? `?${query}` : ''}`)
      setWorkflows(res.data.results || res.data)
    } catch (error) {
      notify.error('Failed to load workflows')
    }
  }

  const fetchTasks = async () => {
    try {
      const res = await api.get('/workflows/tasks/')
      setTasks(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const fetchInstances = async () => {
    try {
      const res = await api.get('/workflows/instances/')
      setInstances(res.data.results || res.data)
    } catch (error) { /* silent */ }
  }

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => setFilters({ status: '', trigger_type: '' })
  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  // Form handling
  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData({ name: '', description: '', status: 'DRAFT', trigger_type: '', assigned_to: '', due_date: '' })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    setFormData({ name: item.name || '', description: item.description || '', status: item.status || 'DRAFT', trigger_type: item.trigger_type || '', assigned_to: item.assigned_to || '', due_date: item.due_date || '' })
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const handleViewTasks = (workflow) => {
    setSelectedItem(workflow)
    setOpenTasksDialog(true)
  }

  const handleSubmit = async () => {
    if (!formData.name.trim()) { notify.warning('Workflow name is required'); return }
    setSubmitting(true)
    try {
      if (selectedItem) {
        await api.put(`/workflows/workflows/${selectedItem.id}/`, formData)
        notify.success('Workflow updated')
      } else {
        await api.post('/workflows/workflows/', formData)
        notify.success('Workflow created')
      }
      setOpenFormDialog(false)
      setSelectedItem(null)
      fetchWorkflows()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save workflow'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        if (firstKey) { const val = data[firstKey]; msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}` }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await api.delete(`/workflows/workflows/${selectedItem.id}/`)
      notify.success('Workflow deleted')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      fetchWorkflows()
    } catch (error) {
      notify.error('Failed to delete')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'DRAFT': return 'warning'
      case 'COMPLETED': return 'info'
      case 'CANCELLED': return 'error'
      default: return 'default'
    }
  }

  const getTaskStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'success'
      case 'IN_PROGRESS': return 'warning'
      case 'PENDING': return 'info'
      case 'CANCELLED': return 'error'
      default: return 'default'
    }
  }

  const getWorkflowTasks = (workflowId) => tasks.filter(t => t.workflow === workflowId || t.workflow_id === workflowId)

  const columns = [
    { id: 'name', label: 'Workflow Name', render: (row) => <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.name}</Typography> },
    { id: 'description', label: 'Description', render: (row) => <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>{row.description || '-'}</Typography> },
    { id: 'status', label: 'Status', render: (row) => <Chip label={row.status} size="small" color={getStatusColor(row.status)} /> },
    { id: 'trigger_type', label: 'Trigger Type' },
    { id: 'assigned_to', label: 'Assigned To' },
    { id: 'due_date', label: 'Due Date' },
  ]

  if (loading) return <Loading message="Loading workflows..." />

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Workflow & Task Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {workflows.length} workflow{workflows.length !== 1 ? 's' : ''}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<FilterIcon />} onClick={() => setShowFilters(!showFilters)} color={hasActiveFilters ? 'primary' : 'inherit'}>
            Filters {hasActiveFilters ? `(${Object.values(filters).filter(v => v).length})` : ''}
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            New Workflow
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={0} sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}>
          <Tab label={`Workflows (${workflows.length})`} />
        </Tabs>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter Workflows</Typography>
            {hasActiveFilters && <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)} label="Status">
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="DRAFT">Draft</MenuItem>
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="COMPLETED">Completed</MenuItem>
                  <MenuItem value="CANCELLED">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField fullWidth size="small" label="Trigger Type"
                value={filters.trigger_type} onChange={(e) => handleFilterChange('trigger_type', e.target.value)} />
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Workflows" value={workflows.length} icon={<WorkflowIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active" value={workflows.filter(w => w.status === 'ACTIVE').length} icon={<WorkflowIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Tasks" value={tasks.filter(t => t.status === 'PENDING' || t.status === 'IN_PROGRESS').length} icon={<TaskIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Completed" value={workflows.filter(w => w.status === 'COMPLETED').length + tasks.filter(t => t.status === 'COMPLETED').length} icon={<WorkflowIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable columns={columns} data={workflows} onView={handleViewTasks} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{selectedItem ? 'Edit Workflow' : 'New Workflow'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" required label="Workflow Name"
                value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} label="Status">
                  <MenuItem value="DRAFT">Draft</MenuItem>
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="COMPLETED">Completed</MenuItem>
                  <MenuItem value="CANCELLED">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth size="small" label="Description" multiline rows={3}
                value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" label="Trigger Type"
                value={formData.trigger_type} onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" label="Assigned To"
                value={formData.assigned_to} onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth size="small" label="Due Date" type="date" InputLabelProps={{ shrink: true }}
                value={formData.due_date} onChange={(e) => setFormData({ ...formData, due_date: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenFormDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {submitting ? 'Saving...' : selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ VIEW DETAILS DIALOG ============ */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Workflow Details
          {selectedItem?.status && <Chip label={selectedItem.status} size="small" sx={{ ml: 1 }} color={getStatusColor(selectedItem.status)} />}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}><Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Workflow Information</Typography></Grid>
              <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Name</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.name}</Typography></Grid>
              <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Trigger Type</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.trigger_type || '-'}</Typography></Grid>
              <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Assigned To</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.assigned_to || '-'}</Typography></Grid>
              <Grid item xs={12} sm={6}><Typography variant="caption" color="text.secondary">Due Date</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.due_date || '-'}</Typography></Grid>
              {selectedItem.description && <Grid item xs={12}><Divider sx={{ my: 1 }} /><Typography variant="caption" color="text.secondary">Description</Typography><Typography variant="body2" sx={{ fontWeight: 500, whiteSpace: 'pre-wrap' }}>{selectedItem.description}</Typography></Grid>}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />} onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }} sx={{ bgcolor: '#1a237e' }}>Edit</Button>
        </DialogActions>
      </Dialog>

      {/* ============ TASKS DIALOG ============ */}
      <Dialog open={openTasksDialog} onClose={() => setOpenTasksDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600 }}>
          <TaskIcon /> Tasks for {selectedItem?.name}
        </DialogTitle>
        <DialogContent>
          <List>
            {getWorkflowTasks(selectedItem?.id).length === 0 ? (
              <ListItem><ListItemText primary="No tasks found for this workflow" /></ListItem>
            ) : (
              getWorkflowTasks(selectedItem?.id).map((task, index) => (
                <ListItem key={task.id || index} divider>
                  <ListItemIcon><TaskIcon color={task.status === 'COMPLETED' ? 'success' : 'action'} /></ListItemIcon>
                  <ListItemText primary={task.title || task.name}
                    secondary={<Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip label={task.status} size="small" color={getTaskStatusColor(task.status)} />
                      {task.due_date && <Typography variant="caption" color="text.secondary">Due: {task.due_date}</Typography>}
                    </Box>} />
                </ListItem>
              ))
            )}
          </List>
        </DialogContent>
        <DialogActions><Button onClick={() => setOpenTasksDialog(false)}>Close</Button></DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog open={openDeleteDialog} title="Delete Workflow"
        message={`Are you sure you want to delete "${selectedItem?.name}"? This action cannot be undone.`}
        onConfirm={handleDelete} onCancel={() => setOpenDeleteDialog(false)} confirmText="Delete" severity="error" />
    </Box>
  )
}

export default Workflows
