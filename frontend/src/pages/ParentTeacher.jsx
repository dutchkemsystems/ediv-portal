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
import { Add as AddIcon, Handshake as PTIcon } from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'
import DataTable from '../components/common/DataTable'
import ConfirmDialog from '../components/common/ConfirmDialog'
import { notify } from '../utils/notifications'

const lagosRed = '#C8102E'

function ParentTeacher() {
  const [tabValue, setTabValue] = useState(0)
  const [meetings, setMeetings] = useState([])
  const [messages, setMessages] = useState([])
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)
  const [isEdit, setIsEdit] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  const emptyMeeting = {
    title: '', meeting_type: 'PARENT_TEACHER', description: '', school: '',
    scheduled_date: '', scheduled_time: '10:00', duration_minutes: 60, venue: '',
    status: 'SCHEDULED', is_mandatory: false, minutes: '', decisions: '', follow_up_actions: '',
  }

  const emptyMessage = {
    recipient: '', student: '', category: 'GENERAL', subject: '', body: '', is_urgent: false,
  }

  const [form, setForm] = useState(emptyMeeting)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [meetingsRes, messagesRes, reportsRes] = await Promise.all([
        api.get('/parent-teacher/meetings/').catch(() => ({ data: { results: [] } })),
        api.get('/parent-teacher/messages/').catch(() => ({ data: { results: [] } })),
        api.get('/parent-teacher/reports/').catch(() => ({ data: { results: [] } })),
      ])
      setMeetings(meetingsRes.data.results || meetingsRes.data || [])
      setMessages(messagesRes.data.results || messagesRes.data || [])
      setReports(reportsRes.data.results || reportsRes.data || [])
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleOpen = (type, item = null) => {
    setDialogType(type)
    if (item) {
      setForm({ ...emptyMeeting, ...item })
      setIsEdit(true)
    } else {
      setForm(type === 'meeting' ? emptyMeeting : emptyMessage)
      setIsEdit(false)
    }
    setDialogOpen(true)
  }

  const handleClose = () => { setDialogOpen(false); setSelectedItem(null) }

  const handleSave = async () => {
    try {
      const endpoint = dialogType === 'meeting' ? '/parent-teacher/meetings/' : '/parent-teacher/messages/'
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
      const endpoint = dialogType === 'meeting' ? '/parent-teacher/meetings/' : '/parent-teacher/messages/'
      await api.delete(`${endpoint}${selectedItem.id}/`)
      notify.success('Deleted successfully')
      setConfirmOpen(false)
      setSelectedItem(null)
      fetchData()
    } catch (err) {
      notify.error('Failed to delete')
    }
  }

  const statusColor = (s) => ({ SCHEDULED: 'info', CONFIRMED: 'success', COMPLETED: 'default', CANCELLED: 'error', RESCHEDULED: 'warning' }[s] || 'default')

  const meetingColumns = [
    { key: 'title', label: 'Title' },
    { key: 'meeting_type', label: 'Type' },
    { key: 'school_name', label: 'School' },
    { key: 'scheduled_date', label: 'Date' },
    { key: 'scheduled_time', label: 'Time' },
    { key: 'venue', label: 'Venue' },
    { key: 'status', label: 'Status', render: (r) => <Chip label={r.status} size="small" color={statusColor(r.status)} /> },
  ]

  const messageColumns = [
    { key: 'sender_name', label: 'From' },
    { key: 'student_name', label: 'Student' },
    { key: 'category', label: 'Category', render: (r) => <Chip label={r.category} size="small" /> },
    { key: 'subject', label: 'Subject' },
    { key: 'is_urgent', label: 'Priority', render: (r) => r.is_urgent ? <Chip label="URGENT" size="small" color="error" /> : null },
    { key: 'is_read', label: 'Status', render: (r) => <Chip label={r.is_read ? 'Read' : 'Unread'} size="small" color={r.is_read ? 'default' : 'info'} /> },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <PTIcon sx={{ color: lagosRed, fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 600 }}>Parent-Teacher Collaboration</Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="PTA Meetings" value={meetings.length} icon="📅" color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Messages" value={messages.length} icon="💬" color="#00843D" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Unread Messages" value={messages.filter(m => !m.is_read).length} icon="📩" color="#C8102E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Shared Reports" value={reports.length} icon="📄" color="#6A1B9A" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="PTA Meetings" />
          <Tab label="Messages" />
          <Tab label="Shared Reports" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('meeting')}>
                Schedule Meeting
              </Button>
            </Box>
            <DataTable
              columns={meetingColumns}
              data={meetings}
              loading={loading}
              onEdit={(m) => handleOpen('meeting', m)}
              onDelete={(m) => { setSelectedItem(m); setDialogType('meeting'); setConfirmOpen(true) }}
              searchable
            />
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen('message')}>
                Send Message
              </Button>
            </Box>
            <DataTable
              columns={messageColumns}
              data={messages}
              loading={loading}
              onEdit={(m) => handleOpen('message', m)}
              onDelete={(m) => { setSelectedItem(m); setDialogType('message'); setConfirmOpen(true) }}
              searchable
            />
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Student</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Report Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Academic Year</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Read</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reports.map((r) => (
                    <TableRow key={r.id} hover>
                      <TableCell>{r.student_name}</TableCell>
                      <TableCell><Chip label={r.report_type} size="small" /></TableCell>
                      <TableCell>{r.academic_year}</TableCell>
                      <TableCell><Chip label={r.is_read ? 'Yes' : 'No'} size="small" color={r.is_read ? 'success' : 'warning'} /></TableCell>
                      <TableCell>{r.created_at}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>

      {/* Dialog */}
      <Dialog open={dialogOpen} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{isEdit ? 'Edit' : 'Add New'} {dialogType === 'meeting' ? 'PTA Meeting' : 'Message'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {dialogType === 'meeting' ? (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Meeting Type" value={form.meeting_type} onChange={e => setForm({ ...form, meeting_type: e.target.value })}>
                    {['PARENT_TEACHER', 'PROGRESS_REVIEW', 'DISCIPLINARY', 'ACADEMIC_SUPPORT', 'CAREER_GUIDANCE', 'GENERAL'].map(t => <MenuItem key={t} value={t}>{t.replace(/_/g, ' ')}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Date" type="date" value={form.scheduled_date} onChange={e => setForm({ ...form, scheduled_date: e.target.value })} InputLabelProps={{ shrink: true }} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Time" type="time" value={form.scheduled_time} onChange={e => setForm({ ...form, scheduled_time: e.target.value })} InputLabelProps={{ shrink: true }} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Duration (minutes)" type="number" value={form.duration_minutes} onChange={e => setForm({ ...form, duration_minutes: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Venue" value={form.venue} onChange={e => setForm({ ...form, venue: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Description" multiline rows={2} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Minutes" multiline rows={3} value={form.minutes} onChange={e => setForm({ ...form, minutes: e.target.value })} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Decisions" multiline rows={2} value={form.decisions} onChange={e => setForm({ ...form, decisions: e.target.value })} />
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Subject" value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth select label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                    {['ACADEMIC', 'BEHAVIOR', 'ATTENDANCE', 'EVENTS', 'FEES', 'GENERAL', 'URGENT'].map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="Message" multiline rows={4} value={form.body} onChange={e => setForm({ ...form, body: e.target.value })} />
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

export default ParentTeacher
