import React, { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Button, Paper, Grid, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Alert, TextField, Dialog,
  DialogTitle, DialogContent, DialogActions, MenuItem, Container, Tabs,
  Tab, LinearProgress, Stepper, Step, StepLabel,
} from '@mui/material'
import {
  Description as MemoIcon, CheckCircle as ApproveIcon,
  Cancel as RejectIcon, Share as CirculateIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const STATUS_COLORS = {
  DRAFT: 'default', REGISTERED: 'info', UNDER_APPROVAL: 'warning',
  CIRCULATING: 'primary', ACKNOWLEDGED: 'success', IN_ACTION: 'secondary',
  REPORTED: 'success', ARCHIVED: 'default',
}

const MEMO_STEPS = ['Draft', 'Registered', 'Under Approval', 'Circulating', 'Acknowledged', 'In Action', 'Reported', 'Archived']

function MemoWorkflow() {
  const [tabValue, setTabValue] = useState(0)
  const [memos, setMemos] = useState([])
  const [loading, setLoading] = useState(true)
  const [alert, setAlert] = useState(null)
  const [selectedMemo, setSelectedMemo] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [staffList, setStaffList] = useState([])
  const [circulateDialogOpen, setCirculateDialogOpen] = useState(false)
  const [selectedRecipients, setSelectedRecipients] = useState([])
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newMemo, setNewMemo] = useState({ title: '', content: '', document_type: 'MEMO', classification: 'INTERNAL' })

  const fetchMemos = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/registry/memos/')
      setMemos(res.data.results || res.data)
    } catch {
      setAlert({ type: 'error', msg: 'Failed to load memos' })
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

  useEffect(() => { fetchMemos(); fetchStaff() }, [fetchMemos, fetchStaff])

  const handleCreateMemo = async () => {
    try {
      const docRes = await api.post('/registry/documents/', {
        title: newMemo.title, content: newMemo.content,
        document_type: newMemo.document_type, classification: newMemo.classification,
      })
      await api.post('/registry/memos/', {
        document: docRes.data.id, workflow_type: newMemo.document_type === 'CIRCULAR' ? 'CIRCULAR' : 'MEMO',
      })
      setAlert({ type: 'success', msg: 'Memo created' })
      setCreateDialogOpen(false)
      setNewMemo({ title: '', content: '', document_type: 'MEMO', classification: 'INTERNAL' })
      fetchMemos()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleApprove = async (memoId) => {
    try {
      await api.post(`/registry/memos/${memoId}/approve/`, { comments: 'Approved' })
      setAlert({ type: 'success', msg: 'Memo approved' })
      fetchMemos()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleReject = async (memoId) => {
    try {
      await api.post(`/registry/memos/${memoId}/reject/`, { comments: 'Needs revision' })
      setAlert({ type: 'warning', msg: 'Memo rejected' })
      fetchMemos()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleCirculate = async () => {
    if (!selectedMemo) return
    try {
      await api.post(`/registry/memos/${selectedMemo.id}/circulate/`, { recipient_ids: selectedRecipients })
      setAlert({ type: 'success', msg: `Circulated to ${selectedRecipients.length} recipients` })
      setCirculateDialogOpen(false)
      setSelectedRecipients([])
      fetchMemos()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const handleArchive = async (memoId) => {
    try {
      await api.post(`/registry/memos/${memoId}/archive/`)
      setAlert({ type: 'success', msg: 'Memo archived' })
      fetchMemos()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Failed' })
    }
  }

  const activeMemos = memos.filter((m) => m.status !== 'ARCHIVED')
  const archivedMemos = memos.filter((m) => m.status === 'ARCHIVED')
  const displayedMemos = tabValue === 0 ? activeMemos : archivedMemos
  const activeStep = selectedMemo ? MEMO_STEPS.findIndex((s) => s.toLowerCase().replace(' ', '_') === selectedMemo.status) : 0

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Memo & Circular Workflow
      </Typography>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>
          {alert.msg}
        </Alert>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <StatCard title="Active Memos" value={activeMemos.length} icon={<MemoIcon />} color={lagosRed} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Under Approval" value={memos.filter((m) => m.status === 'UNDER_APPROVAL').length} icon={<ApproveIcon />} color="#ed6c02" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Circulating" value={memos.filter((m) => m.status === 'CIRCULATING').length} icon={<CirculateIcon />} color="#1976d2" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
            <Tab label={`Active (${activeMemos.length})`} />
            <Tab label={`Archived (${archivedMemos.length})`} />
          </Tabs>
          <Button variant="contained" startIcon={<MemoIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 2, bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}>
            New Memo
          </Button>
        </Box>

        {loading ? <LinearProgress /> : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Reference</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created By</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayedMemos.length === 0 ? (
                  <TableRow><TableCell colSpan={7} align="center">No memos</TableCell></TableRow>
                ) : displayedMemos.map((memo) => (
                  <TableRow key={memo.id} hover sx={{ cursor: 'pointer' }}
                    onClick={() => { setSelectedMemo(memo); setDetailOpen(true) }}>
                    <TableCell><strong>{memo.document_reference}</strong></TableCell>
                    <TableCell>{memo.document_reference}</TableCell>
                    <TableCell><Chip label={memo.workflow_type} size="small" /></TableCell>
                    <TableCell><Chip label={memo.status} size="small" color={STATUS_COLORS[memo.status] || 'default'} /></TableCell>
                    <TableCell>{memo.created_by_name}</TableCell>
                    <TableCell>{new Date(memo.created_at).toLocaleDateString()}</TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      {memo.status === 'DRAFT' && <Button size="small" onClick={() => handleApprove(memo.id)}>Submit</Button>}
                      {memo.status === 'UNDER_APPROVAL' && (
                        <>
                          <Button size="small" color="success" onClick={() => handleApprove(memo.id)}>Approve</Button>
                          <Button size="small" color="error" onClick={() => handleReject(memo.id)}>Reject</Button>
                        </>
                      )}
                      {memo.status === 'CIRCULATING' && <Button size="small" onClick={() => { setSelectedMemo(memo); setCirculateDialogOpen(true) }}>Circulate</Button>}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Memo: {selectedMemo?.document_reference}</DialogTitle>
        <DialogContent>
          {selectedMemo && (
            <Box>
              <Typography variant="body2" gutterBottom><strong>Type:</strong> {selectedMemo.workflow_type}</Typography>
              <Typography variant="body2" gutterBottom><strong>Status:</strong> <Chip label={selectedMemo.status} size="small" color={STATUS_COLORS[selectedMemo.status]} /></Typography>
              <Typography variant="body2" gutterBottom><strong>Created by:</strong> {selectedMemo.created_by_name}</Typography>

              <Stepper activeStep={activeStep >= 0 ? activeStep : 0} sx={{ mt: 3, mb: 2 }}>
                {MEMO_STEPS.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
              </Stepper>

              <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                {selectedMemo.status === 'UNDER_APPROVAL' && (
                  <>
                    <Button variant="outlined" color="success" startIcon={<ApproveIcon />} onClick={() => { handleApprove(selectedMemo.id); setDetailOpen(false) }}>Approve</Button>
                    <Button variant="outlined" color="error" startIcon={<RejectIcon />} onClick={() => { handleReject(selectedMemo.id); setDetailOpen(false) }}>Reject</Button>
                  </>
                )}
                {selectedMemo.status === 'CIRCULATING' && (
                  <Button variant="outlined" startIcon={<CirculateIcon />} onClick={() => setCirculateDialogOpen(true)}>Circulate to Staff</Button>
                )}
                <Button variant="outlined" color="error" onClick={() => { handleArchive(selectedMemo.id); setDetailOpen(false) }}>Archive</Button>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Create Memo Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Memo / Circular</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}><TextField fullWidth label="Title" value={newMemo.title} onChange={(e) => setNewMemo({ ...newMemo, title: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Content" multiline rows={4} value={newMemo.content} onChange={(e) => setNewMemo({ ...newMemo, content: e.target.value })} /></Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Type" value={newMemo.document_type} onChange={(e) => setNewMemo({ ...newMemo, document_type: e.target.value })}>
                <MenuItem value="MEMO">Memo</MenuItem>
                <MenuItem value="CIRCULAR">Circular</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Classification" value={newMemo.classification} onChange={(e) => setNewMemo({ ...newMemo, classification: e.target.value })}>
                {['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'].map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateMemo} sx={{ bgcolor: lagosRed }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Circulate Dialog */}
      <Dialog open={circulateDialogOpen} onClose={() => setCirculateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Circulate to Staff</DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom>Select staff members to circulate to:</Typography>
          {staffList.map((staff) => (
            <Box key={staff.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5 }}>
              <input type="checkbox" checked={selectedRecipients.includes(staff.id)}
                onChange={(e) => {
                  if (e.target.checked) setSelectedRecipients([...selectedRecipients, staff.id])
                  else setSelectedRecipients(selectedRecipients.filter((id) => id !== staff.id))
                }} />
              <Typography variant="body2">{staff.first_name} {staff.last_name}</Typography>
            </Box>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCirculateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCirculate}>Circulate ({selectedRecipients.length})</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default MemoWorkflow
