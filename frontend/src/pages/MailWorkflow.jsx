import React, { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Button, Paper, Grid, Tabs, Tab, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip, Alert, TextField,
  Dialog, DialogTitle, DialogContent, DialogActions, MenuItem, Container,
  Stepper, Step, StepLabel, IconButton, LinearProgress,
} from '@mui/material'
import {
  Mail as MailIcon, Forward as ForwardIcon, Archive as ArchiveIcon,
  Refresh as RefreshIcon, Add as AddIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const STATUS_COLORS = {
  RECEIVED: 'info', SCANNED: 'info', CLASSIFIED: 'primary', ASSIGNED: 'warning',
  UNDER_REVIEW: 'warning', IN_ACTION: 'secondary', RESPONDED: 'success',
  DISPATCHED: 'success', ARCHIVED: 'default',
}

const MAIL_STEPS = ['Received', 'Scanned', 'Classified', 'Assigned', 'Under Review', 'In Action', 'Responded', 'Dispatched', 'Archived']

function MailWorkflow() {
  const [tabValue, setTabValue] = useState(0)
  const [mails, setMails] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedMail, setSelectedMail] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [alert, setAlert] = useState(null)
  const [assignDialogOpen, setAssignDialogOpen] = useState(false)
  const [forwardDialogOpen, setForwardDialogOpen] = useState(false)
  const [staffList, setStaffList] = useState([])

  const [newMail, setNewMail] = useState({
    sender_name: '', sender_organization: '', subject: '',
    date_received: new Date().toISOString().split('T')[0], subject_category: 'LETTER',
    priority: 'NORMAL', classification: 'INTERNAL',
  })
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [assignForm, setAssignForm] = useState({ assigned_to_id: '', action_required: '', deadline: '' })
  const [forwardForm, setForwardForm] = useState({ to_person_id: '', action: 'Forwarded', remarks: '' })

  const fetchMails = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/mail-workflow/incoming-mail/')
      setMails(res.data.results || res.data)
    } catch {
      setAlert({ type: 'error', msg: 'Failed to load mails' })
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchStaff = useCallback(async () => {
    try {
      const res = await api.get('/users/school-staff/')
      setStaffList(res.data.results || res.data)
    } catch { /* silent */ }
  }, [])

  useEffect(() => { fetchMails(); fetchStaff() }, [fetchMails, fetchStaff])

  const handleCreateMail = async () => {
    try {
      await api.post('/mail-workflow/incoming-mail/', newMail)
      setAlert({ type: 'success', msg: 'Mail registered successfully' })
      setCreateDialogOpen(false)
      setNewMail({ sender_name: '', sender_organization: '', subject: '', date_received: new Date().toISOString().split('T')[0], subject_category: 'LETTER', priority: 'NORMAL', classification: 'INTERNAL' })
      fetchMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed to create mail' })
    }
  }

  const handleScan = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/scan/`, { scan_notes: 'Scanned', attachment_count: 0 })
      setAlert({ type: 'success', msg: 'Mail marked as scanned' })
      fetchMails()
      if (selectedMail?.id === mailId) setSelectedMail({ ...selectedMail, status: 'SCANNED' })
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleClassify = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/classify/`, { classification: 'INTERNAL', priority: 'NORMAL' })
      setAlert({ type: 'success', msg: 'Mail classified' })
      fetchMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleAssign = async () => {
    if (!selectedMail) return
    try {
      await api.post(`/mail-workflow/incoming-mail/${selectedMail.id}/assign/`, assignForm)
      setAlert({ type: 'success', msg: 'Mail assigned' })
      setAssignDialogOpen(false)
      setAssignForm({ assigned_to_id: '', action_required: '', deadline: '' })
      fetchMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleForward = async () => {
    if (!selectedMail) return
    try {
      await api.post(`/mail-workflow/incoming-mail/${selectedMail.id}/forward/`, forwardForm)
      setAlert({ type: 'success', msg: 'Mail forwarded' })
      setForwardDialogOpen(false)
      setForwardForm({ to_person_id: '', action: 'Forwarded', remarks: '' })
      fetchMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleArchive = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/archive/`)
      setAlert({ type: 'success', msg: 'Mail archived' })
      fetchMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const activeMails = mails.filter((m) => m.status !== 'ARCHIVED')
  const archivedMails = mails.filter((m) => m.status === 'ARCHIVED')
  const displayedMails = tabValue === 0 ? activeMails : archivedMails
  const activeStep = selectedMail ? MAIL_STEPS.indexOf(MAIL_STEPS.find((s) => s.toLowerCase().replace(' ', '_') === selectedMail.status) || 'Received') : 0

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Incoming Mail Workflow
      </Typography>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>
          {alert.msg}
        </Alert>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <StatCard title="Active Mails" value={activeMails.length} icon={<MailIcon />} color={lagosRed} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Archived" value={archivedMails.length} icon={<ArchiveIcon />} color="#2e7d32" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Total" value={mails.length} icon={<MailIcon />} color="#1565c0" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
            <Tab label={`Active (${activeMails.length})`} />
            <Tab label={`Archived (${archivedMails.length})`} />
          </Tabs>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 2, bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}>
            Register Mail
          </Button>
        </Box>

        {loading ? <LinearProgress /> : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Mail #</TableCell>
                  <TableCell>Sender</TableCell>
                  <TableCell>Subject</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayedMails.length === 0 ? (
                  <TableRow><TableCell colSpan={8} align="center">No mails</TableCell></TableRow>
                ) : displayedMails.map((mail) => (
                  <TableRow key={mail.id} hover sx={{ cursor: 'pointer' }}
                    onClick={() => { setSelectedMail(mail); setDetailOpen(true) }}>
                    <TableCell><strong>{mail.mail_number}</strong></TableCell>
                    <TableCell>{mail.sender_name}</TableCell>
                    <TableCell>{mail.subject}</TableCell>
                    <TableCell><Chip label={mail.subject_category} size="small" /></TableCell>
                    <TableCell><Chip label={mail.priority} size="small"
                      color={mail.priority === 'URGENT' ? 'error' : mail.priority === 'HIGH' ? 'warning' : 'default'} /></TableCell>
                    <TableCell><Chip label={mail.status} size="small" color={STATUS_COLORS[mail.status] || 'default'} /></TableCell>
                    <TableCell>{mail.date_received}</TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      {mail.status === 'RECEIVED' && <Button size="small" onClick={() => handleScan(mail.id)}>Scan</Button>}
                      {mail.status === 'SCANNED' && <Button size="small" onClick={() => handleClassify(mail.id)}>Classify</Button>}
                      {mail.status === 'CLASSIFIED' && <Button size="small" onClick={() => { setSelectedMail(mail); setAssignDialogOpen(true) }}>Assign</Button>}
                      <IconButton size="small" onClick={() => handleArchive(mail.id)}><ArchiveIcon fontSize="small" /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Mail Detail Dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedMail?.mail_number} — {selectedMail?.subject}</DialogTitle>
        <DialogContent>
          {selectedMail && (
            <Box>
              <Typography variant="body2" gutterBottom><strong>From:</strong> {selectedMail.sender_name} ({selectedMail.sender_organization})</Typography>
              <Typography variant="body2" gutterBottom><strong>Status:</strong> <Chip label={selectedMail.status} size="small" color={STATUS_COLORS[selectedMail.status]} /></Typography>
              <Typography variant="body2" gutterBottom><strong>Classification:</strong> {selectedMail.classification}</Typography>

              <Stepper activeStep={activeStep} sx={{ mt: 3, mb: 2 }}>
                {MAIL_STEPS.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
              </Stepper>

              <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                {selectedMail.status === 'RECEIVED' && <Button variant="outlined" onClick={() => { handleScan(selectedMail.id); setDetailOpen(false) }}>Scan</Button>}
                {selectedMail.status === 'SCANNED' && <Button variant="outlined" onClick={() => { handleClassify(selectedMail.id); setDetailOpen(false) }}>Classify</Button>}
                {['CLASSIFIED', 'ASSIGNED', 'UNDER_REVIEW'].includes(selectedMail.status) && (
                  <Button variant="outlined" onClick={() => setAssignDialogOpen(true)}>Assign</Button>
                )}
                <Button variant="outlined" startIcon={<ForwardIcon />} onClick={() => setForwardDialogOpen(true)}>Forward</Button>
                <Button variant="outlined" color="error" onClick={() => { handleArchive(selectedMail.id); setDetailOpen(false) }}>Archive</Button>
              </Box>

              {selectedMail.movements?.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Movement History</Typography>
                  <Table size="small">
                    <TableHead><TableRow><TableCell>From</TableCell><TableCell>To</TableCell><TableCell>Action</TableCell><TableCell>Date</TableCell></TableRow></TableHead>
                    <TableBody>
                      {selectedMail.movements.map((m) => (
                        <TableRow key={m.id}>
                          <TableCell>{m.from_person_name}</TableCell>
                          <TableCell>{m.to_person_name}</TableCell>
                          <TableCell>{m.action}</TableCell>
                          <TableCell>{new Date(m.movement_date).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Register Mail Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Register Incoming Mail</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}><TextField fullWidth label="Sender Name" value={newMail.sender_name} onChange={(e) => setNewMail({ ...newMail, sender_name: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Sender Organization" value={newMail.sender_organization} onChange={(e) => setNewMail({ ...newMail, sender_organization: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Subject" value={newMail.subject} onChange={(e) => setNewMail({ ...newMail, subject: e.target.value })} /></Grid>
            <Grid item xs={6}><TextField fullWidth type="date" label="Date Received" value={newMail.date_received} onChange={(e) => setNewMail({ ...newMail, date_received: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Category" value={newMail.subject_category} onChange={(e) => setNewMail({ ...newMail, subject_category: e.target.value })}>
                {['LETTER', 'MEMO', 'CIRCULAR', 'INVITE', 'COMPLAINT', 'OTHER'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Priority" value={newMail.priority} onChange={(e) => setNewMail({ ...newMail, priority: e.target.value })}>
                {['LOW', 'NORMAL', 'HIGH', 'URGENT'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Classification" value={newMail.classification} onChange={(e) => setNewMail({ ...newMail, classification: e.target.value })}>
                {['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateMail} sx={{ bgcolor: lagosRed }}>Register</Button>
        </DialogActions>
      </Dialog>

      {/* Assign Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Mail</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField select fullWidth label="Assign To" value={assignForm.assigned_to_id} onChange={(e) => setAssignForm({ ...assignForm, assigned_to_id: e.target.value })}>
                {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12}><TextField fullWidth label="Action Required" multiline rows={3} value={assignForm.action_required} onChange={(e) => setAssignForm({ ...assignForm, action_required: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField type="date" fullWidth label="Deadline" value={assignForm.deadline} onChange={(e) => setAssignForm({ ...assignForm, deadline: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAssign}>Assign</Button>
        </DialogActions>
      </Dialog>

      {/* Forward Dialog */}
      <Dialog open={forwardDialogOpen} onClose={() => setForwardDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Forward Mail</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField select fullWidth label="Forward To" value={forwardForm.to_person_id} onChange={(e) => setForwardForm({ ...forwardForm, to_person_id: e.target.value })}>
                {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12}><TextField fullWidth label="Remarks" multiline rows={3} value={forwardForm.remarks} onChange={(e) => setForwardForm({ ...forwardForm, remarks: e.target.value })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setForwardDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleForward} startIcon={<ForwardIcon />}>Forward</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default MailWorkflow
