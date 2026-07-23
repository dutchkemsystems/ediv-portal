import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Grid,
  Chip,
  Card,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material'
import { Add as AddIcon, Domain as DepartmentIcon } from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'
import DataTable from '../components/common/DataTable'
import ConfirmDialog from '../components/common/ConfirmDialog'
import { notify } from '../utils/notifications'

const lagosRed = '#C8102E'

const departments = [
  { name: 'Administration & HR', code: 'ADMIN_HR', category: 'CORE', units: ['Recruitment', 'Payroll', 'Training', 'Staff Welfare'] },
  { name: 'Finance', code: 'FIN', category: 'CORE', units: ['Budget', 'Accounts', 'Revenue'] },
  { name: 'Internal Audit', code: 'AUDIT', category: 'CORE', units: ['Compliance Audit', 'Operational Audit'] },
  { name: 'Quality Assurance', code: 'QA', category: 'CORE', units: ['Standards & Inspection', 'Curriculum Review'] },
  { name: 'Co-Curricular Activities', code: 'CC', category: 'CORE', units: ['Sports', 'Clubs & Societies', 'Debate & Quiz'] },
  { name: 'EMIS', code: 'EMIS', category: 'CORE', units: ['Data Collection', 'Analytics & Reporting', 'ICT Support'] },
  { name: 'Planning, Research & Statistics', code: 'PLAN', category: 'CORE', units: ['Strategic Planning', 'Research', 'Statistics'] },
  { name: 'Procurement', code: 'PROC', category: 'CORE', units: ['Tender & Contracts', 'Supply Chain'] },
  { name: 'Public Affairs', code: 'PA', category: 'CORE', units: ['Media & Publicity', 'Community Engagement'] },
  { name: 'Schools Administration', code: 'SA', category: 'CORE', units: ['School Inspection', 'Enrolment & Placement', 'School Records'] },
  { name: 'French Unit', code: 'FRENCH', category: 'SUPPORT', units: ['French Instruction', 'French Examinations'] },
  { name: 'Registry', code: 'REG', category: 'CORE', units: ['Records Management', 'Correspondence'] },
]

function Departments() {
  const [tabValue, setTabValue] = useState(0)
  const [deptData, setDeptData] = useState([])
  const [units, setUnits] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)
  const [isEdit, setIsEdit] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  const emptyDept = { name: '', code: '', category: 'CORE', description: '', is_active: true }
  const emptyUnit = { department: '', name: '', code: '', description: '' }
  const [form, setForm] = useState(emptyDept)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [deptRes, unitRes] = await Promise.all([
        api.get('/departments/departments/').catch(() => ({ data: { results: [] } })),
        api.get('/departments/units/').catch(() => ({ data: { results: [] } })),
      ])
      setDeptData(deptRes.data.results || deptRes.data || [])
      setUnits(unitRes.data.results || unitRes.data || [])
    } catch (err) {
      console.error('Failed to fetch departments:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleOpen = (type, item = null) => {
    setDialogType(type)
    if (item) {
      setForm(type === 'department' ? { ...emptyDept, ...item } : { ...emptyUnit, ...item })
      setIsEdit(true)
    } else {
      setForm(type === 'department' ? emptyDept : emptyUnit)
      setIsEdit(false)
    }
    setDialogOpen(true)
  }

  const handleClose = () => { setDialogOpen(false); setSelectedItem(null) }

  const handleSave = async () => {
    try {
      const endpoint = dialogType === 'department' ? '/departments/departments/' : '/departments/units/'
      if (isEdit && form.id) {
        await api.put(`${endpoint}${form.id}/`, form)
        notify.success(`${dialogType} updated successfully`)
      } else {
        await api.post(endpoint, form)
        notify.success(`${dialogType} created successfully`)
      }
      handleClose()
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to save')
    }
  }

  const handleDelete = async () => {
    if (!selectedItem) return
    try {
      const endpoint = dialogType === 'department' ? '/departments/departments/' : '/departments/units/'
      await api.delete(`${endpoint}${selectedItem.id}/`)
      notify.success('Deleted successfully')
      setConfirmOpen(false)
      setSelectedItem(null)
      fetchData()
    } catch (err) {
      notify.error('Failed to delete')
    }
  }

  const coreDepts = departments.filter(d => d.category === 'CORE')
  const supportDepts = departments.filter(d => d.category === 'SUPPORT')

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <DepartmentIcon sx={{ color: lagosRed, fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 600 }}>Department Management</Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Departments" value={departments.length} icon="🏛️" color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Core Departments" value={coreDepts.length} icon="⚙️" color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Support Units" value={supportDepts.length} icon="🤝" color="#00843D" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Units" value={departments.reduce((sum, d) => sum + d.units.length, 0)} icon="📦" color="#6A1B9A" />
        </Grid>
      </Grid>

      {/* Department Overview Cards */}
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Head Office Departments</Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {coreDepts.map((dept) => (
          <Grid item xs={12} sm={6} md={4} key={dept.code}>
            <Card sx={{ height: '100%', borderLeft: `4px solid ${lagosRed}` }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', mb: 1 }}>{dept.name}</Typography>
                <Chip label={dept.code} size="small" sx={{ mb: 1, bgcolor: lagosRed, color: 'white' }} />
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Units:</Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {dept.units.map((unit) => (
                    <Chip key={unit} label={unit} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {supportDepts.length > 0 && (
        <>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Support Units</Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {supportDepts.map((dept) => (
              <Grid item xs={12} sm={6} md={4} key={dept.code}>
                <Card sx={{ height: '100%', borderLeft: `4px solid #00843D` }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', mb: 1 }}>{dept.name}</Typography>
                    <Chip label={dept.code} size="small" sx={{ mb: 1, bgcolor: '#00843D', color: 'white' }} />
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Units:</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {dept.units.map((unit) => (
                        <Chip key={unit} label={unit} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* API Data */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Departments (API)" />
          <Tab label="Units (API)" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('department')}>
                Add Department
              </Button>
            </Box>
            <DataTable
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'code', label: 'Code' },
                { key: 'category', label: 'Category', render: (r) => <Chip label={r.category} size="small" color={r.category === 'CORE' ? 'primary' : 'secondary'} /> },
                { key: 'is_active', label: 'Status', render: (r) => <Chip label={r.is_active ? 'Active' : 'Inactive'} size="small" color={r.is_active ? 'success' : 'default'} /> },
              ]}
              data={deptData}
              loading={loading}
              onEdit={(d) => handleOpen('department', d)}
              onDelete={(d) => { setSelectedItem(d); setDialogType('department'); setConfirmOpen(true) }}
              searchable
            />
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('unit')}>
                Add Unit
              </Button>
            </Box>
            <DataTable
              columns={[
                { key: 'name', label: 'Name' },
                { key: 'code', label: 'Code' },
                { key: 'is_active', label: 'Status', render: (r) => <Chip label={r.is_active ? 'Active' : 'Inactive'} size="small" color={r.is_active ? 'success' : 'default'} /> },
              ]}
              data={units}
              loading={loading}
              onEdit={(u) => handleOpen('unit', u)}
              onDelete={(u) => { setSelectedItem(u); setDialogType('unit'); setConfirmOpen(true) }}
              searchable
            />
          </Box>
        )}
      </Paper>

      {/* Dialog */}
      <Dialog open={dialogOpen} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{isEdit ? 'Edit' : 'Add New'} {dialogType === 'department' ? 'Department' : 'Unit'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {dialogType === 'department' ? (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Department Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Code" value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                    <MenuItem value="CORE">Core</MenuItem>
                    <MenuItem value="SUPPORT">Support</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Description" multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Unit Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Code" value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Description" multiline rows={2} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>{isEdit ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete Item"
        message="Are you sure you want to delete this item?"
        onConfirm={handleDelete}
        onCancel={() => { setConfirmOpen(false); setSelectedItem(null) }}
      />
    </Box>
  )
}

export default Departments
