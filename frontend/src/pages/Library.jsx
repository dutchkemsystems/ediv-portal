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
  MenuBook as BookIcon,
  CheckCircle as CheckCircleIcon,
  Handshake as LoanIcon,
  AssignmentLate as OverdueIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Library() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedBook, setSelectedBook] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    category: '',
    quantity: '',
    available: '',
    school: '',
    status: '',
  })

  useEffect(() => {
    fetchBooks()
    fetchStats()
  }, [])

  const fetchBooks = async () => {
    try {
      const response = await api.get('/library/books/')
      setBooks(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching books:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/library/books/')
      const data = response.data.results || response.data
      const totalAvailable = data.reduce((sum, b) => sum + (b.available || 0), 0)
      const totalQuantity = data.reduce((sum, b) => sum + (b.quantity || 0), 0)
      const totalOnLoan = totalQuantity - totalAvailable
      setStats({
        total: totalQuantity,
        available: totalAvailable,
        on_loan: totalOnLoan,
        overdue: data.filter((b) => b.status === 'OVERDUE').length,
      })
    } catch (error) {
      console.error('Error fetching library stats:', error)
    }
  }

  const handleAdd = () => {
    setSelectedBook(null)
    setFormData({
      title: '',
      author: '',
      isbn: '',
      category: '',
      quantity: '',
      available: '',
      school: '',
      status: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (book) => {
    setSelectedBook(book)
    setFormData({
      title: book.title || '',
      author: book.author || '',
      isbn: book.isbn || '',
      category: book.category || '',
      quantity: book.quantity || '',
      available: book.available || '',
      school: book.school || '',
      status: book.status || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (book) => {
    setSelectedBook(book)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedBook) {
        await api.put(`/library/books/${selectedBook.id}/`, formData)
      } else {
        await api.post('/library/books/', formData)
      }
      setOpenDialog(false)
      fetchBooks()
      fetchStats()
    } catch (error) {
      console.error('Error saving book:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/library/books/${selectedBook.id}/`)
      setOpenDeleteDialog(false)
      fetchBooks()
      fetchStats()
    } catch (error) {
      console.error('Error deleting book:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'AVAILABLE': return 'success'
      case 'ON_LOAN': return 'warning'
      case 'OVERDUE': return 'error'
      case 'LOST': return 'error'
      case 'DAMAGED': return 'warning'
      case 'ARCHIVED': return 'default'
      default: return 'default'
    }
  }

  const columns = [
    { id: 'title', label: 'Title' },
    { id: 'author', label: 'Author' },
    { id: 'isbn', label: 'ISBN' },
    { id: 'category', label: 'Category', render: (row) => (
      <Chip label={row.category} size="small" variant="outlined" />
    )},
    { id: 'quantity', label: 'Quantity', align: 'right' },
    { id: 'available', label: 'Available', align: 'right', render: (row) => (
      <Typography
        variant="body2"
        sx={{ color: row.available > 0 ? 'success.main' : 'error.main', fontWeight: 600 }}
      >
        {row.available}
      </Typography>
    )},
    { id: 'school', label: 'School' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status?.replace('_', ' ')} size="small" color={getStatusColor(row.status)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading library records..." />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Library Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Book
        </Button>
      </Box>

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Books"
            value={stats?.total ?? books.reduce((sum, b) => sum + (b.quantity || 0), 0)}
            icon={<BookIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Available"
            value={stats?.available ?? books.reduce((sum, b) => sum + (b.available || 0), 0)}
            icon={<CheckCircleIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="On Loan"
            value={stats?.on_loan ?? (books.reduce((sum, b) => sum + (b.quantity || 0), 0) - books.reduce((sum, b) => sum + (b.available || 0), 0))}
            icon={<LoanIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Overdue"
            value={stats?.overdue ?? books.filter((b) => b.status === 'OVERDUE').length}
            icon={<OverdueIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Table */}
      <DataTable
        columns={columns}
        data={books}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(book) => console.log('View:', book)}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedBook ? 'Edit Book' : 'Add New Book'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Author"
                value={formData.author}
                onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ISBN"
                value={formData.isbn}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
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
                  <MenuItem value="FICTION">Fiction</MenuItem>
                  <MenuItem value="NON_FICTION">Non-Fiction</MenuItem>
                  <MenuItem value="SCIENCE">Science</MenuItem>
                  <MenuItem value="MATHEMATICS">Mathematics</MenuItem>
                  <MenuItem value="ENGLISH">English</MenuItem>
                  <MenuItem value="SOCIAL_STUDIES">Social Studies</MenuItem>
                  <MenuItem value="TECHNOLOGY">Technology</MenuItem>
                  <MenuItem value="REFERENCE">Reference</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Available"
                type="number"
                value={formData.available}
                onChange={(e) => setFormData({ ...formData, available: e.target.value })}
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
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="AVAILABLE">Available</MenuItem>
                  <MenuItem value="ON_LOAN">On Loan</MenuItem>
                  <MenuItem value="OVERDUE">Overdue</MenuItem>
                  <MenuItem value="LOST">Lost</MenuItem>
                  <MenuItem value="DAMAGED">Damaged</MenuItem>
                  <MenuItem value="ARCHIVED">Archived</MenuItem>
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
            {selectedBook ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Book"
        message={`Are you sure you want to delete "${selectedBook?.title}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Library
