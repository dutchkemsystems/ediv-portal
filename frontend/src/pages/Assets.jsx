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
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Inventory as InventoryIcon,
  Build as BuildIcon,
  SwapHoriz as SwapIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Assets() {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    asset_tag: '',
    category: '',
    condition: '',
    location: '',
    school: '',
    purchase_date: '',
    value: '',
    status: '',
  })

  useEffect(() => {
    fetchAssets()
    fetchStats()
  }, [])

  const fetchAssets = async () => {
    try {
      const response = await api.get('/assets/assets/')
      setAssets(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching assets:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/assets/assets/')
      const data = response.data.results || response.data
      setStats({
        total: data.length,
        active: data.filter((a) => a.status === 'ACTIVE').length,
        maintenance: data.filter((a) => a.status === 'MAINTENANCE').length,
        pending_transfers: data.filter((a) => a.status === 'PENDING_TRANSFER').length,
      })
    } catch (error) {
      console.error('Error fetching asset stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedAsset(null)
    setFormData({
      name: '',
      asset_tag: '',
      category: '',
      condition: '',
      location: '',
      school: '',
      purchase_date: '',
      value: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (asset) => {
    setSelectedAsset(asset)
    setFormData({
      name: asset.name || '',
      asset_tag: asset.asset_tag || '',
      category: asset.category || '',
      condition: asset.condition || '',
      location: asset.location || '',
      school: asset.school || '',
      purchase_date: asset.purchase_date || '',
      value: asset.value || '',
      status: asset.status || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (asset) => {
    setSelectedAsset(asset)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedAsset) {
        await api.put(`/assets/assets/${selectedAsset.id}/`, formData)
      } else {
        await api.post('/assets/assets/', formData)
      }
      setOpenDialog(false)
      fetchAssets()
      fetchStats()
    } catch (error) {
      console.error('Error saving asset:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/assets/assets/${selectedAsset.id}/`)
      setOpenDeleteDialog(false)
      fetchAssets()
      fetchStats()
    } catch (error) {
      console.error('Error deleting asset:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success'
      case 'MAINTENANCE': return 'warning'
      case 'PENDING_TRANSFER': return 'info'
      case 'RETIRED': return 'default'
      case 'LOST': return 'error'
      default: return 'default'
    }
  }

  const getConditionColor = (condition) => {
    switch (condition) {
      case 'EXCELLENT': return 'success'
      case 'GOOD': return 'primary'
      case 'FAIR': return 'warning'
      case 'POOR': return 'error'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'name', label: 'Asset Name' },
    { id: 'asset_tag', label: 'Asset Tag' },
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category} size="small" variant="outlined" />
    )},
    { id: 'condition', label: 'Condition', render: (row) => (
      <Chip label={row.condition} size="small" color={getConditionColor(row.condition)} />
    )},
    { id: 'location', label: 'Location' },
    { id: 'value', label: 'Value', align: 'right', render: (row) => (
      row.value ? `₦${Number(row.value).toLocaleString()}` : '-'
    )},
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status?.replace('_', ' ')} size="small" color={getStatusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading assets..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Asset Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Asset
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Assets"
            value={stats?.total ?? assets.length}
            icon={<InventoryIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active"
            value={stats?.active ?? assets.filter((a) => a.status === 'ACTIVE').length}
            icon={<InventoryIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Under Maintenance"
            value={stats?.maintenance ?? assets.filter((a) => a.status === 'MAINTENANCE').length}
            icon={<BuildIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Transfers"
            value={stats?.pending_transfers ?? assets.filter((a) => a.status === 'PENDING_TRANSFER').length}
            icon={<SwapIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={assets}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(asset) => console.log('View:', asset)}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedAsset ? 'Edit Asset' : 'Add New Asset'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Asset Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Asset Tag"
                value={formData.asset_tag}
                onChange={(e) => setFormData({ ...formData, asset_tag: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  label="Category"
                >
                  <MenuItem value="FURNITURE">Furniture</MenuItem>
                  <MenuItem value="COMPUTER">Computer</MenuItem>
                  <MenuItem value="LABORATORY">Laboratory</MenuItem>
                  <MenuItem value="SPORTS">Sports Equipment</MenuItem>
                  <MenuItem value="LIBRARY">Library</MenuItem>
                  <MenuItem value="VEHICLE">Vehicle</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Condition</InputLabel>
                <Select
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                  label="Condition"
                >
                  <MenuItem value="EXCELLENT">Excellent</MenuItem>
                  <MenuItem value="GOOD">Good</MenuItem>
                  <MenuItem value="FAIR">Fair</MenuItem>
                  <MenuItem value="POOR">Poor</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </Grid>
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
                label="Purchase Date"
                type="date"
                value={formData.purchase_date}
                onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Value (₦)"
                type="number"
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
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
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="MAINTENANCE">Under Maintenance</MenuItem>
                  <MenuItem value="PENDING_TRANSFER">Pending Transfer</MenuItem>
                  <MenuItem value="RETIRED">Retired</MenuItem>
                  <MenuItem value="LOST">Lost</MenuItem>
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
            {selectedAsset ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Asset"
        message={`Are you sure you want to delete "${selectedAsset?.name}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Assets
