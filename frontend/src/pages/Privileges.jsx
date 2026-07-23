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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Alert,
} from '@mui/material'
import { Add as AddIcon, Security as SecurityIcon } from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'
import { notify } from '../utils/notifications'

const allRoles = [
  { value: 'SYSADMIN', label: 'System Administrator', category: 'Head Office' },
  { value: 'TG', label: 'Tutor General', category: 'Head Office' },
  { value: 'PS', label: 'Permanent Secretary', category: 'Head Office' },
  { value: 'HR', label: 'Admin & HR Head', category: 'Head Office' },
  { value: 'FIN', label: 'Finance Director', category: 'Head Office' },
  { value: 'AUDIT', label: 'Internal Audit', category: 'Head Office' },
  { value: 'QA', label: 'Quality Assurance', category: 'Head Office' },
  { value: 'CC', label: 'Co-Curricular', category: 'Head Office' },
  { value: 'EMIS', label: 'EMIS', category: 'Head Office' },
  { value: 'PLAN', label: 'Planning & Statistics', category: 'Head Office' },
  { value: 'PROC', label: 'Procurement', category: 'Head Office' },
  { value: 'PA', label: 'Public Affairs', category: 'Head Office' },
  { value: 'SA', label: 'Schools Administration', category: 'Head Office' },
  { value: 'FRENCH', label: 'French Unit', category: 'Support' },
  { value: 'REG', label: 'Registry', category: 'Head Office' },
  { value: 'PRI', label: 'Principal', category: 'School' },
  { value: 'VP', label: 'Vice Principal', category: 'School' },
  { value: 'TCH', label: 'Teacher', category: 'School' },
  { value: 'STD', label: 'Student', category: 'School' },
  { value: 'PAR', label: 'Parent', category: 'External' },
  { value: 'REG_OFF', label: 'Registry Officer', category: 'Head Office' },
  { value: 'SA_OFF', label: 'Schools Admin Officer', category: 'Head Office' },
]

const modules = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'schools', label: 'Schools' },
  { key: 'staff', label: 'Staff Management' },
  { key: 'students', label: 'Students' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'academics', label: 'Academics' },
  { key: 'finance', label: 'Finance' },
  { key: 'grants', label: 'Grants' },
  { key: 'hr', label: 'HR & Recruitment' },
  { key: 'registry', label: 'E-Registry' },
  { key: 'files', label: 'Files' },
  { key: 'workflows', label: 'Workflows' },
  { key: 'communication', label: 'Communication' },
  { key: 'notifications', label: 'Notifications' },
  { key: 'timetable', label: 'Timetable' },
  { key: 'transport', label: 'Transport' },
  { key: 'assets', label: 'Assets' },
  { key: 'discipline', label: 'Discipline' },
  { key: 'library', label: 'Library' },
  { key: 'e_learning', label: 'E-Learning' },
  { key: 'wellness', label: 'Wellness' },
  { key: 'alumni', label: 'Alumni' },
  { key: 'infrastructure', label: 'Infrastructure' },
  { key: 'inspection', label: 'Inspection' },
  { key: 'french', label: 'French Unit' },
  { key: 'co_curricular', label: 'Co-Curricular' },
  { key: 'cpd', label: 'CPD' },
  { key: 'reports', label: 'Reports' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'privileges', label: 'Privileges' },
]

const defaultAccess = {
  SYSADMIN: modules.map(m => m.key),
  TG: modules.map(m => m.key),
  PS: modules.map(m => m.key),
  HR: ['dashboard', 'staff', 'hr', 'grants', 'reports', 'notifications'],
  FIN: ['dashboard', 'finance', 'grants', 'reports', 'notifications'],
  AUDIT: ['dashboard', 'finance', 'grants', 'reports', 'notifications'],
  QA: ['dashboard', 'reports', 'notifications', 'inspection'],
  CC: ['dashboard', 'co_curricular', 'reports', 'notifications'],
  EMIS: ['dashboard', 'reports', 'analytics', 'notifications'],
  PLAN: ['dashboard', 'reports', 'analytics', 'notifications'],
  REG: ['dashboard', 'registry', 'files', 'workflows', 'notifications'],
  PROC: ['dashboard', 'reports', 'notifications'],
  PA: ['dashboard', 'communication', 'reports', 'notifications'],
  SA: ['dashboard', 'schools', 'reports', 'notifications'],
  FRENCH: ['dashboard', 'french', 'reports', 'notifications'],
  REG_OFF: ['dashboard', 'registry', 'files', 'workflows', 'notifications'],
  SA_OFF: ['dashboard', 'schools', 'students', 'reports', 'notifications'],
  PRI: ['dashboard', 'schools', 'students', 'staff', 'academics', 'attendance', 'timetable', 'reports', 'discipline', 'library', 'notifications'],
  VP: ['dashboard', 'students', 'staff', 'academics', 'attendance', 'timetable', 'reports', 'discipline', 'notifications'],
  TCH: ['dashboard', 'students', 'academics', 'attendance', 'timetable', 'e_learning', 'discipline', 'notifications'],
  STD: ['dashboard', 'academics', 'attendance', 'library', 'e_learning', 'notifications'],
  PAR: ['dashboard', 'students', 'finance', 'communication', 'notifications'],
}

function Privileges() {
  const [tabValue, setTabValue] = useState(0)
  const [roleAccess, setRoleAccess] = useState(defaultAccess)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState('SYSADMIN')

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get('/users/users/')
        setUsers(res.data.results || res.data || [])
      } catch (err) {
        console.error('Failed to fetch users')
      } finally {
        setLoading(false)
      }
    }
    fetchUsers()
  }, [])

  const handleToggleModule = (role, module) => {
    setRoleAccess(prev => {
      const current = prev[role] || []
      const updated = current.includes(module)
        ? current.filter(m => m !== module)
        : [...current, module]
      return { ...prev, [role]: updated }
    })
  }

  const handleSelectAll = (role) => {
    setRoleAccess(prev => ({ ...prev, [role]: modules.map(m => m.key) }))
  }

  const handleDeselectAll = (role) => {
    setRoleAccess(prev => ({ ...prev, [role]: [] }))
  }

  const usersByRole = (role) => users.filter(u => u.role === role)

  const headOfficeRoles = allRoles.filter(r => r.category === 'Head Office')
  const schoolRoles = allRoles.filter(r => r.category === 'School')
  const otherRoles = allRoles.filter(r => r.category === 'Support' || r.category === 'External')

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <SecurityIcon sx={{ color: '#C8102E', fontSize: 32 }} />
          <Typography variant="h5" sx={{ fontWeight: 600 }}>Privileges & Access Control</Typography>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Roles" value={allRoles.length} icon="👥" color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Head Office Roles" value={headOfficeRoles.length} icon="🏛️" color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="School Roles" value={schoolRoles.length} icon="🏫" color="#00843D" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Users" value={users.length} icon="👤" color="#F9A825" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Role Access Matrix" />
          <Tab label="Users by Role" />
          <Tab label="Role Definitions" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Configure which modules each role can access. Changes are saved locally and can be deployed to the backend.
            </Alert>
            <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
              {allRoles.slice(0, 8).map(role => (
                <Chip
                  key={role.value}
                  label={`${role.label} (${(roleAccess[role.value] || []).length})`}
                  onClick={() => setSelectedRole(role.value)}
                  color={selectedRole === role.value ? 'primary' : 'default'}
                  variant={selectedRole === role.value ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button size="small" onClick={() => handleSelectAll(selectedRole)}>Select All</Button>
              <Button size="small" onClick={() => handleDeselectAll(selectedRole)}>Deselect All</Button>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Module</TableCell>
                    <TableCell align="center" sx={{ fontWeight: 600 }}>Access</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {modules.map(mod => (
                    <TableRow key={mod.key} hover>
                      <TableCell>{mod.label}</TableCell>
                      <TableCell align="center">
                        <Switch
                          checked={(roleAccess[selectedRole] || []).includes(mod.key)}
                          onChange={() => handleToggleModule(selectedRole, mod.key)}
                          color="primary"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Role</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Users</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Count</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allRoles.map(role => {
                    const roleUsers = usersByRole(role.value)
                    return (
                      <TableRow key={role.value} hover>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>{role.label}</Typography>
                          <Typography variant="caption" color="text.secondary">{role.value}</Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={role.category} size="small" color={role.category === 'Head Office' ? 'primary' : role.category === 'School' ? 'secondary' : 'default'} />
                        </TableCell>
                        <TableCell>
                          {roleUsers.slice(0, 3).map(u => (
                            <Typography key={u.id} variant="caption" display="block">{u.first_name} {u.last_name}</Typography>
                          ))}
                          {roleUsers.length > 3 && <Typography variant="caption" color="text.secondary">+{roleUsers.length - 3} more</Typography>}
                        </TableCell>
                        <TableCell>
                          <Chip label={roleUsers.length} size="small" />
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Role Code</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Role Name</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Modules Access</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allRoles.map(role => (
                    <TableRow key={role.value} hover>
                      <TableCell>
                        <Chip label={role.value} size="small" sx={{ bgcolor: '#C8102E', color: 'white', fontWeight: 600 }} />
                      </TableCell>
                      <TableCell>{role.label}</TableCell>
                      <TableCell>{role.category}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {(roleAccess[role.value] || []).slice(0, 5).map(m => (
                            <Chip key={m} label={m} size="small" variant="outlined" />
                          ))}
                          {(roleAccess[role.value] || []).length > 5 && (
                            <Chip label={`+${(roleAccess[role.value] || []).length - 5}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default Privileges
