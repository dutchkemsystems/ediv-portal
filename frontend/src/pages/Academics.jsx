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
  Divider,
  Paper,
  Stack,
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  MenuBook as BookIcon,
  Class as ClassIcon,
  Assignment as ExamIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'
import { notify } from '../utils/notifications'

const emptyClassForm = {
  name: '',
  level: '',
  section: '',
  capacity: 40,
  school: '',
  class_teacher: '',
  academic_year: '',
  term: '',
  is_active: true,
}

const emptySubjectForm = {
  name: '',
  code: '',
  description: '',
  category: 'GENERAL',
  is_compulsory: false,
  applicable_levels: [],
}

const emptyExamForm = {
  name: '',
  exam_type: 'CA1',
  school: '',
  academic_year: '',
  term: '',
  start_date: '',
  end_date: '',
  total_marks: 100,
  pass_marks: 40,
  is_active: true,
}

function Academics() {
  const [tab, setTab] = useState(0)
  const [classes, setClasses] = useState([])
  const [subjects, setSubjects] = useState([])
  const [exams, setExams] = useState([])
  const [schools, setSchools] = useState([])
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)

  // Dialogs
  const [openFormDialog, setOpenFormDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [openViewDialog, setOpenViewDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState(emptyClassForm)
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // Filters
  const [classFilters, setClassFilters] = useState({
    school: '',
    level: '',
    term: '',
    academic_year: '',
    is_active: '',
  })
  const [subjectFilters, setSubjectFilters] = useState({
    category: '',
    is_compulsory: '',
  })
  const [examFilters, setExamFilters] = useState({
    school: '',
    exam_type: '',
    term: '',
    academic_year: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchAll()
    fetchSchools()
    fetchStaff()
  }, [])

  useEffect(() => {
    if (tab === 0) fetchClasses()
    if (tab === 1) fetchSubjects()
    if (tab === 2) fetchExams()
  }, [classFilters, subjectFilters, examFilters])

  const fetchAll = async () => {
    try {
      setLoading(true)
      await Promise.all([fetchClasses(), fetchSubjects(), fetchExams()])
    } finally {
      setLoading(false)
    }
  }

  const fetchClasses = async () => {
    try {
      const params = new URLSearchParams()
      if (classFilters.school) params.append('school', classFilters.school)
      if (classFilters.level) params.append('level', classFilters.level)
      if (classFilters.term) params.append('term', classFilters.term)
      if (classFilters.academic_year) params.append('academic_year', classFilters.academic_year)
      if (classFilters.is_active) params.append('is_active', classFilters.is_active)
      const query = params.toString()
      const response = await api.get(`/academics/classes/${query ? `?${query}` : ''}`)
      setClasses(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load classes')
    }
  }

  const fetchSubjects = async () => {
    try {
      const params = new URLSearchParams()
      if (subjectFilters.category) params.append('category', subjectFilters.category)
      if (subjectFilters.is_compulsory) params.append('is_compulsory', subjectFilters.is_compulsory)
      const query = params.toString()
      const response = await api.get(`/academics/subjects/${query ? `?${query}` : ''}`)
      setSubjects(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load subjects')
    }
  }

  const fetchExams = async () => {
    try {
      const params = new URLSearchParams()
      if (examFilters.school) params.append('school', examFilters.school)
      if (examFilters.exam_type) params.append('exam_type', examFilters.exam_type)
      if (examFilters.term) params.append('term', examFilters.term)
      if (examFilters.academic_year) params.append('academic_year', examFilters.academic_year)
      const query = params.toString()
      const response = await api.get(`/academics/exams/${query ? `?${query}` : ''}`)
      setExams(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load exams')
    }
  }

  const fetchSchools = async () => {
    try {
      const response = await api.get('/schools/schools/')
      setSchools(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const fetchStaff = async () => {
    try {
      const response = await api.get('/staff/staff/')
      setStaff(response.data.results || response.data)
    } catch (error) {
      // silent
    }
  }

  const handleFilterChange = (field, value) => {
    if (tab === 0) setClassFilters(prev => ({ ...prev, [field]: value }))
    if (tab === 1) setSubjectFilters(prev => ({ ...prev, [field]: value }))
    if (tab === 2) setExamFilters(prev => ({ ...prev, [field]: value }))
  }

  const clearFilters = () => {
    if (tab === 0) setClassFilters({ school: '', level: '', term: '', academic_year: '', is_active: '' })
    if (tab === 1) setSubjectFilters({ category: '', is_compulsory: '' })
    if (tab === 2) setExamFilters({ school: '', exam_type: '', term: '', academic_year: '' })
  }

  const getActiveFilters = () => {
    if (tab === 0) return classFilters
    if (tab === 1) return subjectFilters
    return examFilters
  }

  const hasActiveFilters = Object.values(getActiveFilters()).some(v => v !== '')

  // Form handling
  const getEmptyForm = () => {
    if (tab === 0) return emptyClassForm
    if (tab === 1) return emptySubjectForm
    return emptyExamForm
  }

  const handleOpenCreate = () => {
    setSelectedItem(null)
    setFormData(getEmptyForm())
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenEdit = (item) => {
    setSelectedItem(item)
    if (tab === 0) {
      setFormData({
        name: item.name || '',
        level: item.level || '',
        section: item.section || '',
        capacity: item.capacity || 40,
        school: item.school || '',
        class_teacher: item.class_teacher || '',
        academic_year: item.academic_year || '',
        term: item.term || '',
        is_active: item.is_active !== false,
      })
    } else if (tab === 1) {
      setFormData({
        name: item.name || '',
        code: item.code || '',
        description: item.description || '',
        category: item.category || 'GENERAL',
        is_compulsory: item.is_compulsory || false,
        applicable_levels: item.applicable_levels || [],
      })
    } else {
      setFormData({
        name: item.name || '',
        exam_type: item.exam_type || 'CA1',
        school: item.school || '',
        academic_year: item.academic_year || '',
        term: item.term || '',
        start_date: item.start_date || '',
        end_date: item.end_date || '',
        total_marks: item.total_marks || 100,
        pass_marks: item.pass_marks || 40,
        is_active: item.is_active !== false,
      })
    }
    setFormErrors({})
    setOpenFormDialog(true)
  }

  const handleOpenView = (item) => {
    setSelectedItem(item)
    setOpenViewDialog(true)
  }

  const validateForm = () => {
    const errors = {}
    if (tab === 0) {
      if (!formData.name.trim()) errors.name = 'Class name is required'
      if (!formData.level) errors.level = 'Level is required'
      if (!formData.school) errors.school = 'School is required'
      if (!formData.academic_year.trim()) errors.academic_year = 'Academic year is required'
      if (!formData.term) errors.term = 'Term is required'
    } else if (tab === 1) {
      if (!formData.name.trim()) errors.name = 'Subject name is required'
      if (!formData.code.trim()) errors.code = 'Subject code is required'
    } else {
      if (!formData.name.trim()) errors.name = 'Exam name is required'
      if (!formData.school) errors.school = 'School is required'
      if (!formData.academic_year.trim()) errors.academic_year = 'Academic year is required'
      if (!formData.term) errors.term = 'Term is required'
      if (!formData.start_date) errors.start_date = 'Start date is required'
      if (!formData.end_date) errors.end_date = 'End date is required'
    }
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      notify.warning('Please fill in all required fields')
      return
    }
    setSubmitting(true)
    try {
      const endpoint = tab === 0 ? 'classes' : tab === 1 ? 'subjects' : 'exams'
      const payload = { ...formData }
      if (tab === 0) {
        payload.school = formData.school || null
        payload.class_teacher = formData.class_teacher || null
      }
      if (tab === 2) {
        payload.school = formData.school || null
      }

      if (selectedItem) {
        await api.put(`/academics/${endpoint}/${selectedItem.id}/`, payload)
        notify.success(`${tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'} updated successfully`)
      } else {
        await api.post(`/academics/${endpoint}/`, payload)
        notify.success(`${tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'} created successfully`)
      }
      setOpenFormDialog(false)
      setFormErrors({})
      if (tab === 0) fetchClasses()
      if (tab === 1) fetchSubjects()
      if (tab === 2) fetchExams()
    } catch (error) {
      const data = error.response?.data
      let msg = 'Failed to save'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        if (firstKey) {
          const val = data[firstKey]
          msg = Array.isArray(val) ? `${firstKey}: ${val[0]}` : `${firstKey}: ${val}`
        }
      }
      notify.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      const endpoint = tab === 0 ? 'classes' : tab === 1 ? 'subjects' : 'exams'
      await api.delete(`/academics/${endpoint}/${selectedItem.id}/`)
      notify.success('Deleted successfully')
      setOpenDeleteDialog(false)
      setSelectedItem(null)
      if (tab === 0) fetchClasses()
      if (tab === 1) fetchSubjects()
      if (tab === 2) fetchExams()
    } catch (error) {
      notify.error('Failed to delete')
    }
  }

  // Columns
  const classColumns = [
    {
      id: 'name',
      label: 'Class Name',
      render: (row) => (
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.name}</Typography>
          <Typography variant="caption" color="text.secondary">{row.level}</Typography>
        </Box>
      ),
    },
    { id: 'school_name', label: 'School' },
    { id: 'section', label: 'Section', render: (row) => row.section || '-' },
    { id: 'academic_year', label: 'Year' },
    { id: 'term', label: 'Term', render: (row) => row.term?.replace('FIRST', '1st').replace('SECOND', '2nd').replace('THIRD', '3rd') || '-' },
    {
      id: 'current_enrollment',
      label: 'Students',
      align: 'right',
      render: (row) => (
        <Chip label={row.current_enrollment || 0} size="small" sx={{ fontWeight: 600 }} />
      ),
    },
    {
      id: 'capacity',
      label: 'Capacity',
      align: 'right',
      render: (row) => row.capacity || 40,
    },
    {
      id: 'is_active',
      label: 'Status',
      render: (row) => (
        <Chip label={row.is_active !== false ? 'Active' : 'Inactive'} size="small" color={row.is_active !== false ? 'success' : 'default'} />
      ),
    },
  ]

  const subjectColumns = [
    {
      id: 'name',
      label: 'Subject Name',
      render: (row) => (
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.name}</Typography>
          <Typography variant="caption" color="text.secondary">{row.code}</Typography>
        </Box>
      ),
    },
    { id: 'category', label: 'Category', render: (row) => {
      const colors = { SCIENCE: 'primary', ARTS: 'secondary', COMMERCIAL: 'info', TECHNICAL: 'warning', GENERAL: 'default' }
      return <Chip label={row.category} size="small" color={colors[row.category] || 'default'} />
    }},
    {
      id: 'is_compulsory',
      label: 'Compulsory',
      render: (row) => (
        <Chip label={row.is_compulsory ? 'Yes' : 'No'} size="small" color={row.is_compulsory ? 'warning' : 'default'} />
      ),
    },
  ]

  const examColumns = [
    {
      id: 'name',
      label: 'Exam Name',
      render: (row) => (
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.name}</Typography>
          <Typography variant="caption" color="text.secondary">{row.exam_type}</Typography>
        </Box>
      ),
    },
    { id: 'school_name', label: 'School' },
    { id: 'term', label: 'Term', render: (row) => row.term?.replace('FIRST', '1st').replace('SECOND', '2nd').replace('THIRD', '3rd') || '-' },
    { id: 'academic_year', label: 'Year' },
    { id: 'start_date', label: 'Start' },
    { id: 'end_date', label: 'End' },
    {
      id: 'is_active',
      label: 'Status',
      render: (row) => (
        <Chip label={row.is_active !== false ? 'Active' : 'Inactive'} size="small" color={row.is_active !== false ? 'success' : 'default'} />
      ),
    },
  ]

  const getDialogTitle = () => {
    const label = tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'
    return selectedItem ? `Edit ${label}` : `Add ${label}`
  }

  const getFilterLabel = () => {
    const label = tab === 0 ? 'Classes' : tab === 1 ? 'Subjects' : 'Exams'
    return label
  }

  if (loading) {
    return <Loading message="Loading academics data..." />
  }

  const activeExamCount = exams.filter(e => e.is_active !== false).length
  const totalEnrollment = classes.reduce((sum, c) => sum + (c.current_enrollment || 0), 0)

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Academics Management</Typography>
          <Typography variant="body2" color="text.secondary">
            {tab === 0 ? `${classes.length} classes` : tab === 1 ? `${subjects.length} subjects` : `${exams.length} exams`}
            {hasActiveFilters ? ' (filtered)' : ''}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
            color={hasActiveFilters ? 'primary' : 'inherit'}
          >
            Filters {hasActiveFilters ? `(${Object.values(getActiveFilters()).filter(v => v).length})` : ''}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreate}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            Add {tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'}
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 2 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => { setTab(v); setShowFilters(false) }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}
        >
          <Tab label={`Classes (${classes.length})`} icon={<ClassIcon />} iconPosition="start" />
          <Tab label={`Subjects (${subjects.length})`} icon={<BookIcon />} iconPosition="start" />
          <Tab label={`Exams (${exams.length})`} icon={<ExamIcon />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <FilterIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">Filter {getFilterLabel()}</Typography>
            {hasActiveFilters && (
              <Button size="small" startIcon={<ClearIcon />} onClick={clearFilters}>Clear All</Button>
            )}
          </Box>

          {/* Class Filters */}
          {tab === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={2.4}>
                <FormControl fullWidth size="small">
                  <InputLabel>School</InputLabel>
                  <Select value={classFilters.school} onChange={(e) => handleFilterChange('school', e.target.value)} label="School">
                    <MenuItem value="">All Schools</MenuItem>
                    {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Level</InputLabel>
                  <Select value={classFilters.level} onChange={(e) => handleFilterChange('level', e.target.value)} label="Level">
                    <MenuItem value="">All Levels</MenuItem>
                    <MenuItem value="JSS1">JSS1</MenuItem>
                    <MenuItem value="JSS2">JSS2</MenuItem>
                    <MenuItem value="JSS3">JSS3</MenuItem>
                    <MenuItem value="SS1">SS1</MenuItem>
                    <MenuItem value="SS2">SS2</MenuItem>
                    <MenuItem value="SS3">SS3</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Term</InputLabel>
                  <Select value={classFilters.term} onChange={(e) => handleFilterChange('term', e.target.value)} label="Term">
                    <MenuItem value="">All Terms</MenuItem>
                    <MenuItem value="FIRST">First Term</MenuItem>
                    <MenuItem value="SECOND">Second Term</MenuItem>
                    <MenuItem value="THIRD">Third Term</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <TextField fullWidth size="small" label="Academic Year" placeholder="e.g. 2025/2026"
                  value={classFilters.academic_year} onChange={(e) => handleFilterChange('academic_year', e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6} md={2.4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select value={classFilters.is_active} onChange={(e) => handleFilterChange('is_active', e.target.value)} label="Status">
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="true">Active</MenuItem>
                    <MenuItem value="false">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {/* Subject Filters */}
          {tab === 1 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select value={subjectFilters.category} onChange={(e) => handleFilterChange('category', e.target.value)} label="Category">
                    <MenuItem value="">All Categories</MenuItem>
                    <MenuItem value="SCIENCE">Science</MenuItem>
                    <MenuItem value="ARTS">Arts</MenuItem>
                    <MenuItem value="COMMERCIAL">Commercial</MenuItem>
                    <MenuItem value="TECHNICAL">Technical</MenuItem>
                    <MenuItem value="GENERAL">General</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Compulsory</InputLabel>
                  <Select value={subjectFilters.is_compulsory} onChange={(e) => handleFilterChange('is_compulsory', e.target.value)} label="Compulsory">
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="true">Compulsory</MenuItem>
                    <MenuItem value="false">Optional</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {/* Exam Filters */}
          {tab === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>School</InputLabel>
                  <Select value={examFilters.school} onChange={(e) => handleFilterChange('school', e.target.value)} label="School">
                    <MenuItem value="">All Schools</MenuItem>
                    {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Exam Type</InputLabel>
                  <Select value={examFilters.exam_type} onChange={(e) => handleFilterChange('exam_type', e.target.value)} label="Exam Type">
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="CA1">CA1</MenuItem>
                    <MenuItem value="CA2">CA2</MenuItem>
                    <MenuItem value="CA3">CA3</MenuItem>
                    <MenuItem value="MIDTERM">Mid-Term</MenuItem>
                    <MenuItem value="FINAL">Final</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Term</InputLabel>
                  <Select value={examFilters.term} onChange={(e) => handleFilterChange('term', e.target.value)} label="Term">
                    <MenuItem value="">All Terms</MenuItem>
                    <MenuItem value="FIRST">First Term</MenuItem>
                    <MenuItem value="SECOND">Second Term</MenuItem>
                    <MenuItem value="THIRD">Third Term</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField fullWidth size="small" label="Academic Year" placeholder="e.g. 2025/2026"
                  value={examFilters.academic_year} onChange={(e) => handleFilterChange('academic_year', e.target.value)} />
              </Grid>
            </Grid>
          )}
        </Paper>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Classes" value={classes.length} icon={<ClassIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Subjects" value={subjects.length} icon={<BookIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Exams" value={activeExamCount} icon={<ExamIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Enrollment" value={totalEnrollment} icon={<PeopleIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Tables */}
      {tab === 0 && (
        <DataTable columns={classColumns} data={classes} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}
      {tab === 1 && (
        <DataTable columns={subjectColumns} data={subjects} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}
      {tab === 2 && (
        <DataTable columns={examColumns} data={exams} onView={handleOpenView} onEdit={handleOpenEdit} onDelete={(item) => { setSelectedItem(item); setOpenDeleteDialog(true) }} />
      )}

      {/* ============ CREATE / EDIT DIALOG ============ */}
      <Dialog open={openFormDialog} onClose={() => setOpenFormDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>{getDialogTitle()}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            {/* Class Form */}
            {tab === 0 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Class Name"
                    value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    error={!!formErrors.name} helperText={formErrors.name} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small" required error={!!formErrors.level}>
                    <InputLabel>Level *</InputLabel>
                    <Select value={formData.level} onChange={(e) => setFormData({ ...formData, level: e.target.value })} label="Level *">
                      <MenuItem value="JSS1">JSS1</MenuItem>
                      <MenuItem value="JSS2">JSS2</MenuItem>
                      <MenuItem value="JSS3">JSS3</MenuItem>
                      <MenuItem value="SS1">SS1</MenuItem>
                      <MenuItem value="SS2">SS2</MenuItem>
                      <MenuItem value="SS3">SS3</MenuItem>
                    </Select>
                    {formErrors.level && <Typography variant="caption" color="error">{formErrors.level}</Typography>}
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" label="Section" placeholder="e.g. A, B, Gold"
                    value={formData.section} onChange={(e) => setFormData({ ...formData, section: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" label="Capacity" type="number"
                    value={formData.capacity} onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) || 40 })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small" required error={!!formErrors.school}>
                    <InputLabel>School *</InputLabel>
                    <Select value={formData.school} onChange={(e) => setFormData({ ...formData, school: e.target.value })} label="School *">
                      {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                    </Select>
                    {formErrors.school && <Typography variant="caption" color="error">{formErrors.school}</Typography>}
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Class Teacher</InputLabel>
                    <Select value={formData.class_teacher} onChange={(e) => setFormData({ ...formData, class_teacher: e.target.value })} label="Class Teacher">
                      <MenuItem value="">None</MenuItem>
                      {staff.filter(s => s.category === 'TEACHING').map(s => (
                        <MenuItem key={s.id} value={s.id}>{s.full_name} ({s.staff_id})</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Academic Year" placeholder="e.g. 2025/2026"
                    value={formData.academic_year} onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    error={!!formErrors.academic_year} helperText={formErrors.academic_year} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small" required error={!!formErrors.term}>
                    <InputLabel>Term *</InputLabel>
                    <Select value={formData.term} onChange={(e) => setFormData({ ...formData, term: e.target.value })} label="Term *">
                      <MenuItem value="FIRST">First Term</MenuItem>
                      <MenuItem value="SECOND">Second Term</MenuItem>
                      <MenuItem value="THIRD">Third Term</MenuItem>
                    </Select>
                    {formErrors.term && <Typography variant="caption" color="error">{formErrors.term}</Typography>}
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Switch checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />}
                    label="Active"
                  />
                </Grid>
              </>
            )}

            {/* Subject Form */}
            {tab === 1 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Subject Name"
                    value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    error={!!formErrors.name} helperText={formErrors.name} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Subject Code" placeholder="e.g. MTH, ENG"
                    value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    error={!!formErrors.code} helperText={formErrors.code} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Category</InputLabel>
                    <Select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} label="Category">
                      <MenuItem value="SCIENCE">Science</MenuItem>
                      <MenuItem value="ARTS">Arts</MenuItem>
                      <MenuItem value="COMMERCIAL">Commercial</MenuItem>
                      <MenuItem value="TECHNICAL">Technical</MenuItem>
                      <MenuItem value="GENERAL">General</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={formData.is_compulsory} onChange={(e) => setFormData({ ...formData, is_compulsory: e.target.checked })} />}
                    label="Compulsory"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth size="small" label="Description" multiline rows={2}
                    value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
                </Grid>
              </>
            )}

            {/* Exam Form */}
            {tab === 2 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Exam Name"
                    value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    error={!!formErrors.name} helperText={formErrors.name} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Exam Type</InputLabel>
                    <Select value={formData.exam_type} onChange={(e) => setFormData({ ...formData, exam_type: e.target.value })} label="Exam Type">
                      <MenuItem value="CA1">CA1</MenuItem>
                      <MenuItem value="CA2">CA2</MenuItem>
                      <MenuItem value="CA3">CA3</MenuItem>
                      <MenuItem value="MIDTERM">Mid-Term</MenuItem>
                      <MenuItem value="FINAL">Final</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small" required error={!!formErrors.school}>
                    <InputLabel>School *</InputLabel>
                    <Select value={formData.school} onChange={(e) => setFormData({ ...formData, school: e.target.value })} label="School *">
                      {schools.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                    </Select>
                    {formErrors.school && <Typography variant="caption" color="error">{formErrors.school}</Typography>}
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Academic Year" placeholder="e.g. 2025/2026"
                    value={formData.academic_year} onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    error={!!formErrors.academic_year} helperText={formErrors.academic_year} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small" required error={!!formErrors.term}>
                    <InputLabel>Term *</InputLabel>
                    <Select value={formData.term} onChange={(e) => setFormData({ ...formData, term: e.target.value })} label="Term *">
                      <MenuItem value="FIRST">First Term</MenuItem>
                      <MenuItem value="SECOND">Second Term</MenuItem>
                      <MenuItem value="THIRD">Third Term</MenuItem>
                    </Select>
                    {formErrors.term && <Typography variant="caption" color="error">{formErrors.term}</Typography>}
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="Start Date" type="date" InputLabelProps={{ shrink: true }}
                    value={formData.start_date} onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    error={!!formErrors.start_date} helperText={formErrors.start_date} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" required label="End Date" type="date" InputLabelProps={{ shrink: true }}
                    value={formData.end_date} onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    error={!!formErrors.end_date} helperText={formErrors.end_date} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" label="Total Marks" type="number"
                    value={formData.total_marks} onChange={(e) => setFormData({ ...formData, total_marks: parseInt(e.target.value) || 100 })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth size="small" label="Pass Marks" type="number"
                    value={formData.pass_marks} onChange={(e) => setFormData({ ...formData, pass_marks: parseInt(e.target.value) || 40 })} />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Switch checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />}
                    label="Active"
                  />
                </Grid>
              </>
            )}
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
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'} Details
          {selectedItem && (
            <Chip
              label={selectedItem.is_active !== false ? 'Active' : 'Inactive'}
              size="small"
              sx={{ ml: 1, bgcolor: selectedItem.is_active !== false ? '#E8F5E9' : '#FFF3E0', color: selectedItem.is_active !== false ? '#2E7D32' : '#E65100' }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              {/* Class Details */}
              {tab === 0 && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Class Information</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Class Name</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Level</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.level}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Section</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.section || '-'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">School</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.school_name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Class Teacher</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.class_teacher_name || 'Not assigned'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Capacity</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.capacity || 40}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Enrollment</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.current_enrollment || 0} students</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Academic Year</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.academic_year}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Term</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.term?.replace('FIRST', 'First Term').replace('SECOND', 'Second Term').replace('THIRD', 'Third Term')}</Typography>
                  </Grid>
                </>
              )}

              {/* Subject Details */}
              {tab === 1 && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Subject Information</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Subject Name</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Code</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.code}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Category</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.category}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Compulsory</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.is_compulsory ? 'Yes' : 'No'}</Typography>
                  </Grid>
                  {selectedItem.description && (
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Description</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.description}</Typography>
                    </Grid>
                  )}
                </>
              )}

              {/* Exam Details */}
              {tab === 2 && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ color: '#1a237e', mb: 1 }}>Exam Information</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Exam Name</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Type</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.exam_type}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">School</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.school_name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Academic Year</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.academic_year}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Term</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.term?.replace('FIRST', 'First Term').replace('SECOND', 'Second Term').replace('THIRD', 'Third Term')}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Total Marks</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.total_marks}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Pass Marks</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.pass_marks}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">Start Date</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.start_date}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="caption" color="text.secondary">End Date</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedItem.end_date}</Typography>
                  </Grid>
                </>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />}
            onClick={() => { setOpenViewDialog(false); handleOpenEdit(selectedItem) }}
            sx={{ bgcolor: '#1a237e' }}>
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* ============ DELETE CONFIRMATION ============ */}
      <ConfirmDialog
        open={openDeleteDialog}
        title={`Delete ${tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'}`}
        message={`Are you sure you want to delete "${selectedItem?.name}"? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Academics
