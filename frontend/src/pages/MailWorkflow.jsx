import React, { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Button, Paper, Grid, Tabs, Tab, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip, Alert, TextField,
  Dialog, DialogTitle, DialogContent, DialogActions, MenuItem, Container,
  Stepper, Step, StepLabel, IconButton, LinearProgress, FormControl,
  InputLabel, Select,
} from '@mui/material'
import {
  Mail as MailIcon, Forward as ForwardIcon, Archive as ArchiveIcon,
  Refresh as RefreshIcon, Add as AddIcon, Send as SendIcon,
  School as SchoolIcon, Hub as HubIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const INCOMING_STATUS_COLORS = {
  RECEIVED: 'info', SCANNED: 'info', CLASSIFIED: 'primary', ASSIGNED: 'warning',
  UNDER_REVIEW: 'warning', IN_ACTION: 'secondary', RESPONDED: 'success',
  DISPATCHED: 'success', ARCHIVED: 'default',
}

const OUTGOING_STATUS_COLORS = {
  DRAFT: 'default', PENDING_APPROVAL: 'warning', APPROVED: 'success',
  REJECTED: 'error', DISPATCHED: 'info', DELIVERED: 'success', ARCHIVED: 'default',
}

const HQ_STATUS_COLORS = {
  DRAFT: 'default', SUBMITTED: 'info', RECEIVED_AT_HQ: 'info',
  UNDER_REVIEW: 'warning', APPROVED: 'success', REJECTED: 'error',
  ACTION_REQUIRED: 'warning', COMPLETED: 'success', ARCHIVED: 'default',
}

const INCOMING_STEPS = ['Received', 'Scanned', 'Classified', 'Assigned', 'Under Review', 'In Action', 'Responded', 'Dispatched', 'Archived']
const OUTGOING_STEPS = ['Draft', 'Pending Approval', 'Approved', 'Dispatched', 'Delivered', 'Archived']
const HQ_STEPS = ['Draft', 'Submitted', 'Received at HQ', 'Under Review', 'Approved', 'Completed', 'Archived']

function MailWorkflow() {
  const [tabValue, setTabValue] = useState(0)
  const [incomingMails, setIncomingMails] = useState([])
  const [outgoingMails, setOutgoingMails] = useState([])
  const [hqCorrespondences, setHqCorrespondences] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedMail, setSelectedMail] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [alert, setAlert] = useState(null)
  const [assignDialogOpen, setAssignDialogOpen] = useState(false)
  const [forwardDialogOpen, setForwardDialogOpen] = useState(false)
  const [staffList, setStaffList] = useState([])
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [createTab, setCreateTab] = useState(0)

  const [newIncomingMail, setNewIncomingMail] = useState({
    sender_name: '', sender_organization: '', subject: '',
    date_received: new Date().toISOString().split('T')[0], subject_category: 'LETTER',
    priority: 'NORMAL', classification: 'CONFIDENTIAL',
  })
  const [newOutgoingMail, setNewOutgoingMail] = useState({
    subject: '', recipient_name: '', recipient_organization: '',
    recipient_address: '', priority: 'NORMAL', classification: 'CONFIDENTIAL', content: '',
  })
  const [newHqCorrespondence, setNewHqCorrespondence] = useState({
    direction: 'SCHOOL_TO_HQ', subject: '', content: '',
    priority: 'NORMAL', classification: 'CONFIDENTIAL', requires_response: false,
  })

  const [assignForm, setAssignForm] = useState({ assigned_to_id: '', action_required: '', deadline: '' })
  const [forwardForm, setForwardForm] = useState({ to_person_id: '', action: 'FORWARDED', remarks: '' })

  const fetchIncomingMails = useCallback(async () => {
    try {
      const res = await api.get('/mail-workflow/incoming-mail/')
      setIncomingMails(res.data.results || res.data)
    } catch { /* silent */ }
  }, [])

  const fetchOutgoingMails = useCallback(async () => {
    try {
      const res = await api.get('/mail-workflow/outgoing-mail/')
      setOutgoingMails(res.data.results || res.data)
    } catch { /* silent */ }
  }, [])

  const fetchHqCorrespondences = useCallback(async () => {
    try {
      const res = await api.get('/mail-workflow/school-hq/')
      setHqCorrespondences(res.data.results || res.data)
    } catch { /* silent */ }
  }, [])

  const fetchStaff = useCallback(async () => {
    try {
      const res = await api.get('/users/school-staff/')
      setStaffList(res.data.results || res.data)
    } catch { /* silent */ }
  }, [])

  const fetchAll = useCallback(async () => {
    setLoading(true)
    await Promise.all([fetchIncomingMails(), fetchOutgoingMails(), fetchHqCorrespondences()])
    setLoading(false)
  }, [fetchIncomingMails, fetchOutgoingMails, fetchHqCorrespondences])

  useEffect(() => { fetchAll(); fetchStaff() }, [fetchAll, fetchStaff])

  // --- Incoming Mail Actions ---
  const handleCreateIncomingMail = async () => {
    try {
      await api.post('/mail-workflow/incoming-mail/', newIncomingMail)
      setAlert({ type: 'success', msg: 'Incoming mail registered' })
      setCreateDialogOpen(false)
      setNewIncomingMail({ sender_name: '', sender_organization: '', subject: '', date_received: new Date().toISOString().split('T')[0], subject_category: 'LETTER', priority: 'NORMAL', classification: 'CONFIDENTIAL' })
      fetchIncomingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleScan = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/scan/`, { scan_notes: 'Scanned', attachment_count: 0 })
      setAlert({ type: 'success', msg: 'Mail scanned' })
      fetchIncomingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleClassify = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/classify/`, { classification: 'CONFIDENTIAL', priority: 'NORMAL' })
      setAlert({ type: 'success', msg: 'Mail classified' })
      fetchIncomingMails()
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
      fetchIncomingMails()
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
      setForwardForm({ to_person_id: '', action: 'FORWARDED', remarks: '' })
      fetchIncomingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleArchiveIncoming = async (mailId) => {
    try {
      await api.post(`/mail-workflow/incoming-mail/${mailId}/archive/`)
      setAlert({ type: 'success', msg: 'Mail archived' })
      fetchIncomingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  // --- Outgoing Mail Actions ---
  const handleCreateOutgoingMail = async () => {
    try {
      await api.post('/mail-workflow/outgoing-mail/', newOutgoingMail)
      setAlert({ type: 'success', msg: 'Outgoing mail created' })
      setCreateDialogOpen(false)
      setNewOutgoingMail({ subject: '', recipient_name: '', recipient_organization: '', recipient_address: '', priority: 'NORMAL', classification: 'CONFIDENTIAL', content: '' })
      fetchOutgoingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleOutgoingAction = async (mailId, action) => {
    try {
      await api.post(`/mail-workflow/outgoing-mail/${mailId}/${action}/`)
      setAlert({ type: 'success', msg: `Mail ${action}d` })
      fetchOutgoingMails()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  // --- HQ Correspondence Actions ---
  const handleCreateHqCorrespondence = async () => {
    try {
      await api.post('/mail-workflow/school-hq/', newHqCorrespondence)
      setAlert({ type: 'success', msg: 'Correspondence created' })
      setCreateDialogOpen(false)
      setNewHqCorrespondence({ direction: 'SCHOOL_TO_HQ', subject: '', content: '', priority: 'NORMAL', classification: 'CONFIDENTIAL', requires_response: false })
      fetchHqCorrespondences()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleHqAction = async (corrId, action) => {
    try {
      await api.post(`/mail-workflow/school-hq/${corrId}/${action}/`)
      setAlert({ type: 'success', msg: `Correspondence ${action}` })
      fetchHqCorrespondences()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const activeIncoming = incomingMails.filter(m => m.status !== 'ARCHIVED')
  const archivedIncoming = incomingMails.filter(m => m.status === 'ARCHIVED')
  const activeOutgoing = outgoingMails.filter(m => !['DELIVERED', 'ARCHIVED'].includes(m.status))
  const activeHq = hqCorrespondences.filter(c => !['COMPLETED', 'ARCHIVED'].includes(c.status))

  const getIncomingActiveStep = (mail) => {
    if (!mail) return 0
    const statusMap = { RECEIVED: 0, SCANNED: 1, CLASSIFIED: 2, ASSIGNED: 3, UNDER_REVIEW: 4, IN_ACTION: 5, RESPONDED: 6, DISPATCHED: 7, ARCHIVED: 8 }
    return statusMap[mail.status] ?? 0
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Mail Workflow</Typography>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>{alert.msg}</Alert>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <StatCard title="Incoming Mail" value={activeIncoming.length} icon={<MailIcon />} color={lagosRed} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Outgoing Mail" value={activeOutgoing.length} icon={<SendIcon />} color="#1565c0" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="HQ Correspondence" value={activeHq.length} icon={<HubIcon />} color="#2e7d32" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
            <Tab label={`Incoming (${activeIncoming.length})`} />
            <Tab label={`Outgoing (${activeOutgoing.length})`} />
            <Tab label={`HQ Correspondence (${activeHq.length})`} />
          </Tabs>
          <Box>
            <IconButton onClick={fetchAll} sx={{ mr: 1 }}><RefreshIcon /></IconButton>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 2, bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}>
              New Mail
            </Button>
          </Box>
        </Box>

        {loading ? <LinearProgress /> : (
          <TableContainer>
            <Table>
              {/* Tab 0: Incoming Mail */}
              {tabValue === 0 && (
                <>
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
                    {activeIncoming.length === 0 ? (
                      <TableRow><TableCell colSpan={8} align="center">No incoming mails</TableCell></TableRow>
                    ) : activeIncoming.map((mail) => (
                      <TableRow key={mail.id} hover sx={{ cursor: 'pointer' }}
                        onClick={() => { setSelectedMail(mail); setDetailOpen(true) }}>
                        <TableCell><strong>{mail.mail_number}</strong></TableCell>
                        <TableCell>{mail.sender_name}</TableCell>
                        <TableCell>{mail.subject}</TableCell>
                        <TableCell><Chip label={mail.subject_category} size="small" /></TableCell>
                        <TableCell><Chip label={mail.priority} size="small"
                          color={mail.priority === 'URGENT' ? 'error' : mail.priority === 'HIGH' ? 'warning' : 'default'} /></TableCell>
                        <TableCell><Chip label={mail.status} size="small" color={INCOMING_STATUS_COLORS[mail.status] || 'default'} /></TableCell>
                        <TableCell>{mail.date_received}</TableCell>
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          {mail.status === 'RECEIVED' && <Button size="small" onClick={() => handleScan(mail.id)}>Scan</Button>}
                          {mail.status === 'SCANNED' && <Button size="small" onClick={() => handleClassify(mail.id)}>Classify</Button>}
                          {['CLASSIFIED', 'ASSIGNED', 'UNDER_REVIEW'].includes(mail.status) && (
                            <Button size="small" onClick={() => { setSelectedMail(mail); setAssignDialogOpen(true) }}>Assign</Button>
                          )}
                          <IconButton size="small" onClick={() => handleArchiveIncoming(mail.id)}><ArchiveIcon fontSize="small" /></IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </>
              )}

              {/* Tab 1: Outgoing Mail */}
              {tabValue === 1 && (
                <>
                  <TableHead>
                    <TableRow>
                      <TableCell>Mail #</TableCell>
                      <TableCell>Subject</TableCell>
                      <TableCell>Recipient</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Classification</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeOutgoing.length === 0 ? (
                      <TableRow><TableCell colSpan={7} align="center">No outgoing mails</TableCell></TableRow>
                    ) : activeOutgoing.map((mail) => (
                      <TableRow key={mail.id} hover sx={{ cursor: 'pointer' }}
                        onClick={() => { setSelectedMail(mail); setDetailOpen(true) }}>
                        <TableCell><strong>{mail.mail_number}</strong></TableCell>
                        <TableCell>{mail.subject}</TableCell>
                        <TableCell>{mail.recipient_name}</TableCell>
                        <TableCell><Chip label={mail.priority} size="small"
                          color={mail.priority === 'URGENT' ? 'error' : mail.priority === 'HIGH' ? 'warning' : 'default'} /></TableCell>
                        <TableCell><Chip label={mail.classification} size="small" /></TableCell>
                        <TableCell><Chip label={mail.status} size="small" color={OUTGOING_STATUS_COLORS[mail.status] || 'default'} /></TableCell>
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          {mail.status === 'DRAFT' && <Button size="small" onClick={() => handleOutgoingAction(mail.id, 'submit')}>Submit</Button>}
                          {mail.status === 'PENDING_APPROVAL' && (
                            <>
                              <Button size="small" color="success" onClick={() => handleOutgoingAction(mail.id, 'approve')}>Approve</Button>
                              <Button size="small" color="error" onClick={() => handleOutgoingAction(mail.id, 'reject')}>Reject</Button>
                            </>
                          )}
                          {mail.status === 'APPROVED' && <Button size="small" onClick={() => handleOutgoingAction(mail.id, 'dispatch')}>Dispatch</Button>}
                          {mail.status === 'DISPATCHED' && <Button size="small" onClick={() => handleOutgoingAction(mail.id, 'deliver')}>Deliver</Button>}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </>
              )}

              {/* Tab 2: HQ Correspondence */}
              {tabValue === 2 && (
                <>
                  <TableHead>
                    <TableRow>
                      <TableCell>Reference</TableCell>
                      <TableCell>Direction</TableCell>
                      <TableCell>Subject</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeHq.length === 0 ? (
                      <TableRow><TableCell colSpan={6} align="center">No HQ correspondences</TableCell></TableRow>
                    ) : activeHq.map((corr) => (
                      <TableRow key={corr.id} hover sx={{ cursor: 'pointer' }}
                        onClick={() => { setSelectedMail(corr); setDetailOpen(true) }}>
                        <TableCell><strong>{corr.reference_number}</strong></TableCell>
                        <TableCell><Chip label={corr.direction === 'SCHOOL_TO_HQ' ? 'School → HQ' : 'HQ → School'} size="small" color={corr.direction === 'SCHOOL_TO_HQ' ? 'primary' : 'secondary'} /></TableCell>
                        <TableCell>{corr.subject}</TableCell>
                        <TableCell><Chip label={corr.priority} size="small"
                          color={corr.priority === 'URGENT' ? 'error' : corr.priority === 'HIGH' ? 'warning' : 'default'} /></TableCell>
                        <TableCell><Chip label={corr.status} size="small" color={HQ_STATUS_COLORS[corr.status] || 'default'} /></TableCell>
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          {corr.status === 'DRAFT' && <Button size="small" onClick={() => handleHqAction(corr.id, 'submit')}>Submit</Button>}
                          {corr.status === 'SUBMITTED' && corr.direction === 'SCHOOL_TO_HQ' && (
                            <Button size="small" onClick={() => handleHqAction(corr.id, 'receive')}>Receive at HQ</Button>
                          )}
                          {corr.status === 'RECEIVED_AT_HQ' && (
                            <Button size="small" onClick={() => handleHqAction(corr.id, 'respond')}>Respond</Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </>
              )}
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Mail Detail Dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedMail?.mail_number || selectedMail?.reference_number} — {selectedMail?.subject}</DialogTitle>
        <DialogContent>
          {selectedMail && (
            <Box>
              {selectedMail.sender_name && (
                <Typography variant="body2" gutterBottom><strong>From:</strong> {selectedMail.sender_name} ({selectedMail.sender_organization})</Typography>
              )}
              {selectedMail.recipient_name && (
                <Typography variant="body2" gutterBottom><strong>To:</strong> {selectedMail.recipient_name}</Typography>
              )}
              {selectedMail.direction && (
                <Typography variant="body2" gutterBottom><strong>Direction:</strong> {selectedMail.direction === 'SCHOOL_TO_HQ' ? 'School → HQ' : 'HQ → School'}</Typography>
              )}
              <Typography variant="body2" gutterBottom><strong>Status:</strong> <Chip label={selectedMail.status} size="small" /></Typography>
              <Typography variant="body2" gutterBottom><strong>Classification:</strong> {selectedMail.classification}</Typography>

              <Stepper activeStep={selectedMail.mail_number ? getIncomingActiveStep(selectedMail) : 0} sx={{ mt: 3, mb: 2 }}>
                {(selectedMail.mail_number ? INCOMING_STEPS : selectedMail.direction ? HQ_STEPS : OUTGOING_STEPS).map((label) => (
                  <Step key={label}><StepLabel>{label}</StepLabel></Step>
                ))}
              </Stepper>

              {selectedMail.movements?.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Movement History</Typography>
                  <Table size="small">
                    <TableHead><TableRow><TableCell>From</TableCell><TableCell>To</TableCell><TableCell>Action</TableCell><TableCell>Date</TableCell></TableRow></TableHead>
                    <TableBody>
                      {selectedMail.movements.map((m) => (
                        <TableRow key={m.id}>
                          <TableCell>{m.from_person_name || m.from_holder_name}</TableCell>
                          <TableCell>{m.to_person_name || m.to_holder_name || '—'}</TableCell>
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

      {/* Create Mail Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Mail / Correspondence</DialogTitle>
        <DialogContent>
          <Tabs value={createTab} onChange={(_, v) => setCreateTab(v)} sx={{ mb: 2 }}>
            <Tab label="Incoming" />
            <Tab label="Outgoing" />
            <Tab label="HQ Correspondence" />
          </Tabs>

          {/* Incoming Mail Form */}
          {createTab === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12}><TextField fullWidth label="Sender Name" value={newIncomingMail.sender_name} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, sender_name: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Sender Organization" value={newIncomingMail.sender_organization} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, sender_organization: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Subject" value={newIncomingMail.subject} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, subject: e.target.value })} /></Grid>
              <Grid item xs={6}><TextField fullWidth type="date" label="Date Received" value={newIncomingMail.date_received} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, date_received: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select value={newIncomingMail.subject_category} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, subject_category: e.target.value })} label="Category">
                    {['LETTER', 'MEMO', 'CIRCULAR', 'INVITE', 'COMPLAINT', 'OTHER'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select value={newIncomingMail.priority} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, priority: e.target.value })} label="Priority">
                    {['LOW', 'NORMAL', 'HIGH', 'URGENT'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Classification</InputLabel>
                  <Select value={newIncomingMail.classification} onChange={(e) => setNewIncomingMail({ ...newIncomingMail, classification: e.target.value })} label="Classification">
                    {['PUBLIC', 'CONFIDENTIAL', 'RESTRICTED', 'TOP_SECRET'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {/* Outgoing Mail Form */}
          {createTab === 1 && (
            <Grid container spacing={2}>
              <Grid item xs={12}><TextField fullWidth label="Subject" value={newOutgoingMail.subject} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, subject: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Recipient Name" value={newOutgoingMail.recipient_name} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, recipient_name: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Recipient Organization" value={newOutgoingMail.recipient_organization} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, recipient_organization: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Recipient Address" value={newOutgoingMail.recipient_address} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, recipient_address: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Content" multiline rows={3} value={newOutgoingMail.content} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, content: e.target.value })} /></Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select value={newOutgoingMail.priority} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, priority: e.target.value })} label="Priority">
                    {['LOW', 'NORMAL', 'HIGH', 'URGENT'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Classification</InputLabel>
                  <Select value={newOutgoingMail.classification} onChange={(e) => setNewOutgoingMail({ ...newOutgoingMail, classification: e.target.value })} label="Classification">
                    {['PUBLIC', 'CONFIDENTIAL', 'RESTRICTED', 'TOP_SECRET'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {/* HQ Correspondence Form */}
          {createTab === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Direction</InputLabel>
                  <Select value={newHqCorrespondence.direction} onChange={(e) => setNewHqCorrespondence({ ...newHqCorrespondence, direction: e.target.value })} label="Direction">
                    <MenuItem value="SCHOOL_TO_HQ">School → HQ</MenuItem>
                    <MenuItem value="HQ_TO_SCHOOL">HQ → School</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}><TextField fullWidth label="Subject" value={newHqCorrespondence.subject} onChange={(e) => setNewHqCorrespondence({ ...newHqCorrespondence, subject: e.target.value })} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Content" multiline rows={3} value={newHqCorrespondence.content} onChange={(e) => setNewHqCorrespondence({ ...newHqCorrespondence, content: e.target.value })} /></Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select value={newHqCorrespondence.priority} onChange={(e) => setNewHqCorrespondence({ ...newHqCorrespondence, priority: e.target.value })} label="Priority">
                    {['LOW', 'NORMAL', 'HIGH', 'URGENT'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Classification</InputLabel>
                  <Select value={newHqCorrespondence.classification} onChange={(e) => setNewHqCorrespondence({ ...newHqCorrespondence, classification: e.target.value })} label="Classification">
                    {['PUBLIC', 'CONFIDENTIAL', 'RESTRICTED', 'TOP_SECRET'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createTab === 0 ? handleCreateIncomingMail : createTab === 1 ? handleCreateOutgoingMail : handleCreateHqCorrespondence}
            sx={{ bgcolor: lagosRed }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Assign Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Mail</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Assign To</InputLabel>
                <Select value={assignForm.assigned_to_id} onChange={(e) => setAssignForm({ ...assignForm, assigned_to_id: e.target.value })} label="Assign To">
                  {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
                </Select>
              </FormControl>
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
              <FormControl fullWidth>
                <InputLabel>Forward To</InputLabel>
                <Select value={forwardForm.to_person_id} onChange={(e) => setForwardForm({ ...forwardForm, to_person_id: e.target.value })} label="Forward To">
                  {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
                </Select>
              </FormControl>
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
