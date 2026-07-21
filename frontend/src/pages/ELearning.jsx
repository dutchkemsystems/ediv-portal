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
  Visibility as ViewIcon,
  School as SchoolIcon,
  MenuBook as CourseIcon,
  Quiz as QuizIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function ELearning() {
  const [courses, setCourses] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructor: '',
    subject: '',
    duration: '',
    status: 'draft',
    difficulty_level: 'beginner',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [coursesRes, enrollmentsRes, quizzesRes] = await Promise.all([
        api.get('/e-learning/courses/'),
        api.get('/e-learning/enrollments/'),
        api.get('/e-learning/quizzes/'),
      ])
      setCourses(coursesRes.data.results || coursesRes.data)
      setEnrollments(enrollmentsRes.data.results || enrollmentsRes.data)
      setQuizzes(quizzesRes.data.results || quizzesRes.data)
    } catch (error) {
      console.error('Error fetching e-learning data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedCourse(null)
    setFormData({
      title: '',
      description: '',
      instructor: '',
      subject: '',
      duration: '',
      status: 'draft',
      difficulty_level: 'beginner',
    })
    setOpenDialog(true)
  }

  const handleEdit = (course) => {
    setSelectedCourse(course)
    setFormData({
      title: course.title,
      description: course.description,
      instructor: course.instructor,
      subject: course.subject,
      duration: course.duration || '',
      status: course.status,
      difficulty_level: course.difficulty_level,
    })
    setOpenDialog(true)
  }

  const handleDelete = (course) => {
    setSelectedCourse(course)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedCourse) {
        await api.put(`/e-learning/courses/${selectedCourse.id}/`, formData)
      } else {
        await api.post('/e-learning/courses/', formData)
      }
      setOpenDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error saving course:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/e-learning/courses/${selectedCourse.id}/`)
      setOpenDeleteDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error deleting course:', error)
    }
  }

  const columns = [
    { id: 'title', label: 'Course Title' },
    { id: 'instructor', label: 'Instructor' },
    { id: 'subject', label: 'Subject' },
    { id: 'duration', label: 'Duration' },
    { id: 'difficulty_level', label: 'Difficulty', render: (row) => (
      <Chip
        label={row.difficulty_level}
        size="small"
        color={row.difficulty_level === 'advanced' ? 'error' : row.difficulty_level === 'intermediate' ? 'warning' : 'success'}
      />
    )},
    { id: 'enrollment_count', label: 'Enrolled', align: 'right' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip
        label={row.status}
        size="small"
        color={row.status === 'active' ? 'success' : row.status === 'published' ? 'primary' : 'default'}
      />
    )},
  ]

  if (loading) {
    return <Loading message="Loading e-learning data..." />
  }

  const activeCourses = courses.filter(c => c.status === 'active')
  const totalEnrolled = courses.reduce((sum, c) => sum + (c.enrollment_count || 0), 0)
  const completedCount = courses.filter(c => c.status === 'completed').length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">E-Learning Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Course
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Courses"
            value={courses.length}
            icon={<CourseIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Courses"
            value={activeCourses.length}
            icon={<CourseIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Enrolled Students"
            value={totalEnrolled}
            icon={<PeopleIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={completedCount}
            icon={<QuizIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={courses}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(course) => console.log('View:', course)}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedCourse ? 'Edit Course' : 'Add New Course'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Course Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
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
                label="Instructor"
                value={formData.instructor}
                onChange={(e) => setFormData({ ...formData, instructor: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Subject"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Duration"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                placeholder="e.g. 8 weeks"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={formData.difficulty_level}
                  onChange={(e) => setFormData({ ...formData, difficulty_level: e.target.value })}
                  label="Difficulty Level"
                >
                  <MenuItem value="beginner">Beginner</MenuItem>
                  <MenuItem value="intermediate">Intermediate</MenuItem>
                  <MenuItem value="advanced">Advanced</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="published">Published</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
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
            {selectedCourse ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Course"
        message={`Are you sure you want to delete "${selectedCourse?.title}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default ELearning
