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
  Groups as AlumniIcon,
  EmojiEvents as EventIcon,
  AttachMoney as DonationIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import ConfirmDialog from '../components/common/ConfirmDialog'
import api from '../api/client'

function Alumni() {
  const [members, setMembers] = useState([])
  const [events, setEvents] = useState([])
  const [donations, setDonations] = useState([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false)
  const [selectedMember, setSelectedMember] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    graduation_year: '',
    school: '',
    profession: '',
    email: '',
    phone: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [membersRes, eventsRes, donationsRes] = await Promise.all([
        api.get('/alumni/members/'),
        api.get('/alumni/events/'),
        api.get('/alumni/donations/'),
      ])
      setMembers(membersRes.data.results || membersRes.data)
      setEvents(eventsRes.data.results || eventsRes.data)
      setDonations(donationsRes.data.results || donationsRes.data)
    } catch (error) {
      console.error('Error fetching alumni data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedMember(null)
    setFormData({
      name: '',
      graduation_year: '',
      school: '',
      profession: '',
      email: '',
      phone: '',
    })
    setOpenDialog(true)
  }

  const handleEdit = (member) => {
    setSelectedMember(member)
    setFormData({
      name: member.name,
      graduation_year: member.graduation_year || '',
      school: member.school || '',
      profession: member.profession || '',
      email: member.email || '',
      phone: member.phone || '',
    })
    setOpenDialog(true)
  }

  const handleDelete = (member) => {
    setSelectedMember(member)
    setOpenDeleteDialog(true)
  }

  const handleSubmit = async () => {
    try {
      if (selectedMember) {
        await api.put(`/alumni/members/${selectedMember.id}/`, formData)
      } else {
        await api.post('/alumni/members/', formData)
      }
      setOpenDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error saving alumni member:', error)
    }
  }

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/alumni/members/${selectedMember.id}/`)
      setOpenDeleteDialog(false)
      fetchData()
    } catch (error) {
      console.error('Error deleting alumni member:', error)
    }
  }

  const columns = [
    { id: 'name', label: 'Name' },
    { id: 'graduation_year', label: 'Graduation Year' },
    { id: 'school', label: 'School' },
    { id: 'profession', label: 'Profession' },
    { id: 'email', label: 'Email' },
    { id: 'phone', label: 'Phone' },
  ]

  if (loading) {
    return <Loading message="Loading alumni data..." />
  }

  const activeMembers = members.filter(m => m.is_active !== false)
  const totalDonations = donations.reduce((sum, d) => sum + (parseFloat(d.donation_amount) || 0), 0)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Alumni Network</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          Add Alumni
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Alumni"
            value={members.length}
            icon={<AlumniIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Members"
            value={activeMembers.length}
            icon={<PersonIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Events"
            value={events.length}
            icon={<EventIcon />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Donations"
            value={`₦${totalDonations.toLocaleString()}`}
            icon={<DonationIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <DataTable
        columns={columns}
        data={members}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={(member) => console.log('View:', member)}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedMember ? 'Edit Alumni' : 'Add Alumni Member'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Graduation Year"
                type="number"
                value={formData.graduation_year}
                onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
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
                label="Profession"
                value={formData.profession}
                onChange={(e) => setFormData({ ...formData, profession: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
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
            {selectedMember ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={openDeleteDialog}
        title="Delete Alumni"
        message={`Are you sure you want to delete ${selectedMember?.name}? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => setOpenDeleteDialog(false)}
        confirmText="Delete"
        severity="error"
      />
    </Box>
  )
}

export default Alumni
