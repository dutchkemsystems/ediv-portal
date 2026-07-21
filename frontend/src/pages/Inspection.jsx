import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
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
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Inspection() {
  const [inspections, setInspections] = useState([])
  const [checklists, setChecklists] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedInspection, setSelectedInspection] = useState(null)
  const [formData, setFormData] = useState({
    school: '',
    inspector: '',
    inspection_date: '',
    inspection_type: '',
    score: '',
    status: '',
    findings: '',
    recommendations: '',
  })

  useEffect(() => {
    fetchInspections()
    fetchChecklists()
  }, [])

  const fetchInspections = async () => {
    try {
      const response = await api.get('/inspection/inspections/')
      setInspections(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching inspections:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchChecklists = async () => {
    try {
      const response = await api.get('/inspection/checklists/')
      setChecklists(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching checklists:', error)
    }
  }

  const handleAdd = () => {
    setSelectedInspection(null)
    setFormData({
      school: '',
      inspector: '',
      inspection_date: '',
      inspection_type: '',
      score: '',
      status: '',
      findings: '',
      recommendations: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (inspection) => {
    setSelectedInspection(inspection)
    setFormData({
      school: inspection.school,
      inspector: inspection.inspector,
      inspection_date: inspection.inspection_date || '',
      inspection_type: inspection.inspection_type,
      score: inspection.score || '',
      status: inspection.status,
      findings: inspection.findings || '',
      recommendations: inspection.recommendations || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (inspection) => {
    setSelectedInspection(inspection)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedInspection) {
        await api.put(`/inspection/inspections/${selectedInspection.id}/`, formData)
      } else {
        await api.post('/inspection/inspections/', formData)
      }
      setOpenDialog(false)
      fetchInspections()
    } catch (error) {
      console.error('Error saving inspection:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/inspection/inspections/${selectedInspection.id}/`)
      setOpenDeleteDialog(false)
      fetchInspections()
    } catch (error) {
      console.error('Error deleting inspection:', error)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'PASSED': return 'success'
      case 'PENDING': return 'warning'
      case 'FAILED': return 'error'
      case 'FOLLOW_UP': return 'info'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'school', label: 'School' },
    { id: 'inspector', label: 'Inspector' },
    { id: 'inspection_date', label: 'Date' },
    { id: 'inspection_type', label: 'Type' },
    { id: 'score', label: 'Score', align: 'right' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={statusColor(row.status)} />
    )},
    { id: 'findings', label: 'Findings', render: (row) => (
      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
        {row.findings || '-'}
      </Typography>
    )},
  ]

  if (loading) {
    return <Loading message="Loading inspection data..." />
  }

  const now = new Date()
  const thisMonth = inspections.filter(i => {
    if (!i.inspection_date) return false
    const d = new Date(i.inspection_date)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
  const passed = inspections.filter(i => i.status === 'PASSED').length
  const pendingFollowUp = inspections.filter(i => i.status === 'FOLLOW_UP').length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Inspection Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Inspection
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Inspections"
            value={inspections.length}
            icon={<AssessmentIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="This Month"
            value={thisMonth}
            icon={<AssessmentIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Passed"
            value={passed}
            icon={<AssessmentIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Follow-up"
            value={pendingFollowUp}
            icon={<AssessmentIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={inspections}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedInspection ? 'Edit Inspection' : 'Add New Inspection'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="School"
                value={formData.school}
                onChange={(e) => setFormData({ ...formData, school: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Inspector"
                value={formData.inspector}
                onChange={(e) => setFormData({ ...formData, inspector: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Inspection Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={formData.inspection_date}
                onChange={(e) => setFormData({ ...formData, inspection_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Inspection Type</InputLabel>
                <Select
                  value={formData.inspection_type}
                  onChange={(e) => setFormData({ ...formData, inspection_type: e.target.value })}
                  label="Inspection Type"
                >
                  <MenuItem value="ROUTINE">Routine</MenuItem>
                  <MenuItem value="SURPRISE">Surprise</MenuItem>
                  <MenuItem value="COMPREHENSIVE">Comprehensive</MenuItem>
                  <MenuItem value="FOLLOW_UP">Follow-up</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Score"
                type="number"
                value={formData.score}
                onChange={(e) => setFormData({ ...formData, score: e.target.value })}
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
                  <MenuItem value="PENDING">Pending</MenuItem>
                  <MenuItem value="PASSED">Passed</MenuItem>
                  <MenuItem value="FAILED">Failed</MenuItem>
                  <MenuItem value="FOLLOW_UP">Follow-up</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Findings"
                multiline
                rows={3}
                value={formData.findings}
                onChange={(e) => setFormData({ ...formData, findings: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Recommendations"
                multiline
                rows={3}
                value={formData.recommendations}
                onChange={(e) => setFormData({ ...formData, recommendations: e.target.value })}
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
            {selectedInspection ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Inspection"
        message={`Are you sure you want to delete this inspection record? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Inspection
