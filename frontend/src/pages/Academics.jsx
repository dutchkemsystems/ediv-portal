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
  Tabs,
  Tab,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MenuBook as BookIcon,
  Class as ClassIcon,
  Assignment as ExamIcon,
  Grading as ReportIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Academics() {
  const [tab, setTab] = useState(0)
  const [classes, setClasses] = useState([])
  const [subjects, setSubjects] = useState([])
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    level: '',
    school: '',
    subject: '',
    term: '',
    academic_year: '',
  })

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [classRes, subjectRes, examRes] = await Promise.all([
        api.get('/academics/classes/').catch(() => ({ data: { results: [] } })),
        api.get('/academics/subjects/').catch(() => ({ data: { results: [] } })),
        api.get('/academics/exams/').catch(() => ({ data: { results: [] } })),
      ])
      setClasses(classRes.data.results || classRes.data)
      setSubjects(subjectRes.data.results || subjectRes.data)
      setExams(examRes.data.results || examRes.data)
    } catch (error) {
      console.error('Error fetching academics data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedItem(null)
    setFormData({
      name: '',
      code: '',
      level: '',
      school: '',
      subject: '',
      term: '',
      academic_year: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (item) => {
    setSelectedItem(item)
    setFormData({
      name: item.name || '',
      code: item.code || '',
      level: item.level || '',
      school: item.school || '',
      subject: item.subject || '',
      term: item.term || '',
      academic_year: item.academic_year || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (item) => {
    setSelectedItem(item)
    setOpenDeleteDialog(true)
  }

  const getEndpoint = () => {
    switch (tab) {
      case 0: return 'classes'
      case 1: return 'subjects'
      case 2: return 'exams'
      default: return 'classes'
    }
  }

  const handleSubmit = async () => {
    try {
      const endpoint = getEndpoint()
      if (selectedItem) {
        await api.put(`/academics/${endpoint}/${selectedItem.id}/`, formData)
      } else {
        await api.post(`/academics/${endpoint}/`, formData)
      }
      setOpenDialog(false)
      fetchAll()
    } catch (error) {
      console.error('Error saving record:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      const endpoint = getEndpoint()
      await api.delete(`/academics/${endpoint}/${selectedItem.id}/`)
      setOpenDeleteDialog(false)
      fetchAll()
    } catch (error) {
      console.error('Error deleting record:', error)
    }
  }

  const getDialogTitle = () => {
    const label = tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'
    return selectedItem ? `Edit ${label}` : `Add ${label}`
  }

  const getDeleteTitle = () => {
    const label = tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'
    return `Delete ${label}`
  }

  const getDeleteMessage = () => {
    return `Are you sure you want to delete "${selectedItem?.name || selectedItem?.title}"? This action cannot be undone.`
  }

  const classColumns = [
    { id: 'name', label: 'Class Name' },
    { id: 'code', label: 'Code' },
    { id: 'level', label: 'Level' },
    { id: 'school_name', label: 'School' },
    { id: 'subject_count', label: 'Subjects', align: 'right' },
    { id: 'student_count', label: 'Students', align: 'right' },
  ]

  const subjectColumns = [
    { id: 'name', label: 'Subject Name' },
    { id: 'code', label: 'Code' },
    { id: 'level', label: 'Level' },
    { id: 'teacher_name', label: 'Teacher' },
    { id: 'class_count', label: 'Classes', align: 'right' },
  ]

  const examColumns = [
    { id: 'name', label: 'Exam Name' },
    { id: 'subject_name', label: 'Subject' },
    { id: 'term', label: 'Term' },
    { id: 'academic_year', label: 'Academic Year' },
    { id: 'date', label: 'Date' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status || 'Scheduled'}
        size="small"
        color={row.status === 'COMPLETED' ? 'success' : row.status === 'IN_PROGRESS' ? 'warning' : 'primary'}
      />
    )},
  ]

  const activeExamCount = exams.filter((e) => e.status !== 'COMPLETED').length

  if (loading) {
    return <Loading message="Loading academics data..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Academics Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add {tab === 0 ? 'Class' : tab === 1 ? 'Subject' : 'Exam'}
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Classes"
            value={classes.length}
            icon={<ClassIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Subjects"
            value={subjects.length}
            icon={<BookIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Exams"
            value={activeExamCount}
            icon={<ExamIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Report Cards"
            value={exams.length}
            icon={<ReportIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}
        >
          <Tab label="Classes" />
          <Tab label="Subjects" />
          <Tab label="Exams" />
        </Tabs>
      </Box>

      {/* Table */}
      {tab === 0 && (
        <DataTable
          columns={classColumns}
          data={classes}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      {tab === 1 && (
        <DataTable
          columns={subjectColumns}
          data={subjects}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      {tab === 2 && (
        <DataTable
          columns={examColumns}
          data={exams}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{getDialogTitle()}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={tab === 2 ? 'Exam Name' : tab === 1 ? 'Subject Name' : 'Class Name'}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Level</InputLabel>
                <Select
                  value={formData.level}
                  onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                  label="Level"
                >
                  <MenuItem value="JSS1">JSS1</MenuItem>
                  <MenuItem value="JSS2">JSS2</MenuItem>
                  <MenuItem value="JSS3">JSS3</MenuItem>
                  <MenuItem value="SS1">SS1</MenuItem>
                  <MenuItem value="SS2">SS2</MenuItem>
                  <MenuItem value="SS3">SS3</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {tab !== 1 && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="School"
                  value={formData.school}
                  onChange={(e) => setFormData({ ...formData, school: e.target.value })}
                />
              </Grid>
            )}
            {tab === 2 && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Subject"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Term</InputLabel>
                    <Select
                      value={formData.term}
                      onChange={(e) => setFormData({ ...formData, term: e.target.value })}
                      label="Term"
                    >
                      <MenuItem value="FIRST">First Term</MenuItem>
                      <MenuItem value="SECOND">Second Term</MenuItem>
                      <MenuItem value="THIRD">Third Term</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Academic Year"
                    value={formData.academic_year}
                    onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    placeholder="e.g. 2025/2026"
                  />
                </Grid>
              </>
            )}
            {tab === 0 && (
              <>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Term</InputLabel>
                    <Select
                      value={formData.term}
                      onChange={(e) => setFormData({ ...formData, term: e.target.value })}
                      label="Term"
                    >
                      <MenuItem value="FIRST">First Term</MenuItem>
                      <MenuItem value="SECOND">Second Term</MenuItem>
                      <MenuItem value="THIRD">Third Term</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Academic Year"
                    value={formData.academic_year}
                    onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    placeholder="e.g. 2025/2026"
                  />
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
          >
            {selectedItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title={getDeleteTitle()}
        message={getDeleteMessage()}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Academics
