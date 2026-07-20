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
  AccountTree as WorkflowIcon,
  Assignment as TaskIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Workflows() {
  const [workflows, setWorkflows] = useState([])
  const [tasks, setTasks] = useState([])
  const [instances, setInstances] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openTasksDialog, setOpenTasksDialog] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'DRAFT',
    trigger_type: '',
    assigned_to: '',
    due_date: '',
  })

  useEffect(() => {
    fetchWorkflows()
    fetchTasks()
    fetchInstances()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await api.get('/workflows/workflows/')
      setWorkflows(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTasks = async () => {
    try {
      const response = await api.get('/workflows/tasks/')
      setTasks(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching tasks:', error)
    }
  }

  const fetchInstances = async () => {
    try {
      const response = await api.get('/workflows/instances/')
      setInstances(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching instances:', error)
    }
  }

  const handleAdd = () => {
    setSelectedWorkflow(null)
    setFormData({
      name: '',
      description: '',
      status: 'DRAFT',
      trigger_type: '',
      assigned_to: '',
      due_date: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (workflow) => {
    setSelectedWorkflow(workflow)
    setFormData({
      name: workflow.name,
      description: workflow.description,
      status: workflow.status,
      trigger_type: workflow.trigger_type || '',
      assigned_to: workflow.assigned_to || '',
      due_date: workflow.due_date || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (workflow) => {
    setSelectedWorkflow(workflow)
    setOpenDeleteDialog(true)
  }

  const handleViewTasks = (workflow) => {
    setSelectedWorkflow(workflow)
    setOpenTasksDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedWorkflow) {
        await api.put(`/workflows/workflows/${selectedWorkflow.id}/`, formData)
      } else {
        await api.post('/workflows/workflows/', formData)
      }
      setOpenDialog(false)
      fetchWorkflows()
    } catch (error) {
      console.error('Error saving workflow:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/workflows/workflows/${selectedWorkflow.id}/`)
      setOpenDeleteDialog(false)
      fetchWorkflows()
    } catch (error) {
      console.error('Error deleting workflow:', error)
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

  const getWorkflowTasks = (workflowId) => {
    return tasks.filter(t => t.workflow === workflowId || t.workflow_id === workflowId)
  }

  const columns = [
    { id: 'name', label: 'Workflow Name' },
    { id: 'description', label: 'Description', render: (row) => (
      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
        {row.description || '-'}
      </Typography>
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
    { id: 'trigger_type', label: 'Trigger Type' },
    { id: 'assigned_to', label: 'Assigned To' },
    { id: 'due_date', label: 'Due Date' },
  ]

  if (loading) {
    return <Loading message="Loading workflows..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Workflow & Task Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          New Workflow
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Workflows"
            value={workflows.length}
            icon={<WorkflowIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Workflows"
            value={workflows.filter(w => w.status === 'ACTIVE').length}
            icon={<WorkflowIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Tasks"
            value={tasks.filter(t => t.status === 'PENDING' || t.status === 'IN_PROGRESS').length}
            icon={<TaskIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={workflows.filter(w => w.status === 'COMPLETED').length + tasks.filter(t => t.status === 'COMPLETED').length}
            icon={<WorkflowIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={workflows}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleViewTasks}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedWorkflow ? 'Edit Workflow' : 'New Workflow'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Workflow Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="DRAFT">Draft</MenuItem>
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="COMPLETED">Completed</MenuItem>
                  <MenuItem value="CANCELLED">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Trigger Type"
                value={formData.trigger_type}
                onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Assigned To"
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Due Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
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
            {selectedWorkflow ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Tasks Dialog */}
      <Dialog open={openTasksDialog} onClose={() => setOpenTasksDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TaskIcon />
          Tasks for {selectedWorkflow?.name}
        </DialogTitle>
        <DialogContent>
          {selectedWorkflow && (
            <List>
              {getWorkflowTasks(selectedWorkflow.id).length === 0 ? (
                <ListItem>
                  <ListItemText primary="No tasks found for this workflow" />
                </ListItem>
              ) : (
                getWorkflowTasks(selectedWorkflow.id).map((task, index) => (
                  <ListItem key={task.id || index} divider>
                    <ListItemIcon>
                      <TaskIcon color={task.status === 'COMPLETED' ? 'success' : 'action'} />
                    </ListItemIcon>
                    <ListItemText
                      primary={task.title || task.name}
                      secondary={
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                          <Chip label={task.status} size="small" color={getTaskStatusColor(task.status)} />
                          {task.due_date && (
                            <Typography variant="caption" color="text.secondary">
                              Due: {task.due_date}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))
              )}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTasksDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Workflow"
        message={`Are you sure you want to delete workflow "${selectedWorkflow?.name}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Workflows
