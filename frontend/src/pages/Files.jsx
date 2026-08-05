import React, { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Button, Grid, Card, CardContent, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, FormControl, InputLabel, Select,
  MenuItem, Tabs, Tab, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Container, LinearProgress, Stepper, Step, StepLabel,
  IconButton, Alert, Tooltip, Divider,
} from '@mui/material'
import {
  Add as AddIcon, FolderOpen as FileIcon, MoveUp as MoveIcon, Send as SubmitIcon,
  CheckCircle as ApproveIcon, Cancel as RejectIcon, Upgrade as EscalateIcon,
  Archive as ArchiveIcon, Refresh as RefreshIcon, PlayArrow as AdvanceIcon,
  Warning as WarningIcon, Timeline as WorkflowIcon, Search as SearchIcon,
} from '@mui/icons-material'
import DataTable from '../components/common/DataTable'
import StatCard from '../components/common/StatCard'
import Loading from '../components/common/Loading'
import api from '../api/client'
import { notify } from '../utils/notifications'

const FILE_CATEGORIES = [
  { value: 'ADMIN', label: 'Administrative' },
  { value: 'ACAD', label: 'Academic' },
  { value: 'FIN', label: 'Finance' },
  { value: 'INSP', label: 'Inspection' },
  { value: 'DISC', label: 'Discipline' },
  { value: 'COCC', label: 'Co-curricular' },
  { value: 'POL', label: 'Policy' },
  { value: 'CORR', label: 'Correspondence' },
  { value: 'PROC', label: 'Procurement' },
]

const FILE_TYPES = [
  { value: 'CORRESPONDENCE', label: 'Correspondence' },
  { value: 'MEMO', label: 'Memo' },
  { value: 'CIRCULAR', label: 'Circular' },
  { value: 'REPORT', label: 'Report' },
  { value: 'MINUTES', label: 'Minutes' },
  { value: 'POLICY', label: 'Policy' },
  { value: 'CONTRACT', label: 'Contract' },
  { value: 'INVOICE', label: 'Invoice' },
  { value: 'RECEIPT', label: 'Receipt' },
  { value: 'OTHER', label: 'Other' },
]

const CLASSIFICATIONS = [
  { value: 'PUBLIC', label: 'Public' },
  { value: 'CONFIDENTIAL', label: 'Confidential' },
  { value: 'RESTRICTED', label: 'Restricted' },
  { value: 'TOP_SECRET', label: 'Top Secret' },
]

const FILE_STATUSES = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'ACTIVE', label: 'Active' },
  { value: 'PENDING', label: 'Pending' },
  { value: 'IN_TRANSIT', label: 'In Transit' },
  { value: 'UNDER_REVIEW', label: 'Under Review' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'CLOSED', label: 'Closed' },
  { value: 'ARCHIVED', label: 'Archived' },
]

const MOVE_ACTIONS = [
  { value: 'CREATED', label: 'Created' },
  { value: 'SUBMITTED', label: 'Submitted' },
  { value: 'REVIEWED', label: 'Reviewed' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'FORWARDED', label: 'Forwarded' },
  { value: 'RETURNED', label: 'Returned' },
  { value: 'ESCALATED', label: 'Escalated' },
  { value: 'COMMENTED', label: 'Commented' },
  { value: 'ARCHIVED', label: 'Archived' },
]

const DIRECTIONS = [
  { value: 'INCOMING', label: 'Incoming' },
  { value: 'OUTGOING', label: 'Outgoing' },
  { value: 'INTERNAL', label: 'Internal' },
]

function Files() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [tabValue, setTabValue] = useState(0)
  const [alert, setAlert] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openMovementDialog, setOpenMovementDialog] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [staffList, setStaffList] = useState([])
  const [workflowData, setWorkflowData] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    file_type: 'CORRESPONDENCE',
    file_category: 'ADMIN',
    status: 'DRAFT',
    classification: 'CONFIDENTIAL',
    priority: 'NORMAL',
    direction: 'INCOMING',
    description: '',
  })
  const [moveData, setMoveData] = useState({
    to_holder_id: '',
    action: 'FORWARDED',
    remarks: '',
    expected_return_date: '',
    use_workflow: true,
  })

  const fetchFiles = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.get('/files/files/')
      setFiles(response.data.results || response.data)
    } catch (error) {
      notify.error('Failed to load files')
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

  useEffect(() => { fetchFiles(); fetchStaff() }, [fetchFiles, fetchStaff])

  const handleAdd = () => {
    setSelectedFile(null)
    setFormData({
      title: '', file_type: 'CORRESPONDENCE', file_category: 'ADMIN',
      status: 'DRAFT', classification: 'CONFIDENTIAL', priority: 'NORMAL',
      direction: 'INCOMING', description: '',
    })
    setOpenDialog(true)
  }

  const handleMove = (file) => {
    setSelectedFile(file)
    setMoveData({ to_holder_id: '', action: 'FORWARDED', remarks: '', expected_return_date: '', use_workflow: true })
    setOpenMovementDialog(true)
  }

  const handleViewDetail = async (file) => {
    setSelectedFile(file)
    setDetailOpen(true)
    try {
      const res = await api.get(`/files/workflow/${file.id}/detail/`)
      setWorkflowData(res.data)
    } catch {
      setWorkflowData(null)
    }
  }

  const handleAdvanceWorkflow = async (file) => {
    try {
      const res = await api.post(`/files/workflow/${file.id}/advance/`, {
        action: 'FORWARDED',
        notes: 'Workflow advanced',
      })
      notify.success(`File advanced to step ${res.data.current_step}`)
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to advance workflow')
    }
  }

  const handleReceive = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/receive/`)
      notify.success('File received successfully')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to receive file')
    }
  }

  const handleClose = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/close/`)
      notify.success('File archived successfully')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to close file')
    }
  }

  const handleSubmitFile = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/submit/`)
      notify.success('File submitted for review')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to submit file')
    }
  }

  const handleApproveFile = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/approve/`, { notes: 'Approved' })
      notify.success('File approved')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to approve file')
    }
  }

  const handleRejectFile = async (file) => {
    try {
      await api.post(`/files/files/${file.id}/reject/`, { notes: 'Needs revision' })
      notify.success('File rejected and returned to draft')
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to reject file')
    }
  }

  const handleEscalateFile = async (file) => {
    setSelectedFile(file)
    setMoveData({ to_holder_id: '', action: 'ESCALATED', remarks: '', expected_return_date: '', use_workflow: false })
    setOpenMovementDialog(true)
  }

  const handleSubmitMove = async () => {
    try {
      if (moveData.action === 'ESCALATED') {
        await api.post(`/files/files/${selectedFile.id}/escalate/`, {
          to_holder_id: parseInt(moveData.to_holder_id),
          notes: moveData.remarks,
        })
      } else if (moveData.use_workflow) {
        await api.post(`/files/workflow/${selectedFile.id}/move/`, {
          to_holder_id: moveData.to_holder_id ? parseInt(moveData.to_holder_id) : null,
          action: moveData.action,
          remarks: moveData.remarks,
          expected_return_date: moveData.expected_return_date || null,
        })
      } else {
        await api.post(`/files/files/${selectedFile.id}/move/`, {
          to_holder_id: parseInt(moveData.to_holder_id),
          action: moveData.action,
          remarks: moveData.remarks,
          expected_return_date: moveData.expected_return_date || undefined,
          use_workflow: false,
        })
      }
      notify.success(moveData.action === 'ESCALATED' ? 'File escalated' : 'File moved successfully')
      setOpenMovementDialog(false)
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.error || 'Failed to move file')
    }
  }

  const handleSubmitCreate = async () => {
    try {
      await api.post('/files/files/', formData)
      notify.success('File created successfully')
      setOpenDialog(false)
      fetchFiles()
    } catch (error) {
      notify.error(error.response?.data?.detail || 'Failed to create file')
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) { setSearchResults(null); return }
    try {
      const res = await api.get(`/files/search/?q=${encodeURIComponent(searchQuery)}`)
      setSearchResults(res.data)
    } catch {
      notify.error('Search failed')
    }
  }

  const getStatusColor = (status) => {
    const colors = { DRAFT: 'default', ACTIVE: 'success', PENDING: 'warning', IN_TRANSIT: 'info',
      UNDER_REVIEW: 'warning', APPROVED: 'success', REJECTED: 'error', CLOSED: 'default', ARCHIVED: 'default' }
    return colors[status] || 'default'
  }

  const getPriorityColor = (priority) => {
    const colors = { HIGH: 'error', URGENT: 'error', NORMAL: 'info', LOW: 'default' }
    return colors[priority] || 'default'
  }

  const getClassificationColor = (c) => {
    const colors = { PUBLIC: 'success', CONFIDENTIAL: 'warning', RESTRICTED: 'error', TOP_SECRET: 'error' }
    return colors[c] || 'default'
  }

  const activeFiles = files.filter(f => !['ARCHIVED', 'CLOSED'].includes(f.status))
  const archivedFiles = files.filter(f => ['ARCHIVED', 'CLOSED'].includes(f.status))
  const displayedFiles = searchResults ? searchResults.results : (tabValue === 0 ? activeFiles : archivedFiles)
  const overdueFiles = files.filter(f => f.is_overdue)

  if (loading) return <Loading message="Loading files..." />

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">E-Registry File Management</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            size="small" placeholder="Search files..." value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{ endAdornment: <IconButton size="small" onClick={handleSearch}><SearchIcon /></IconButton> }}
            sx={{ width: 250 }}
          />
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            New File
          </Button>
        </Box>
      </Box>

      {alert && <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>{alert.msg}</Alert>}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Files" value={files.length} icon={<FileIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Files" value={activeFiles.length} icon={<FileIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="In Workflow" value={files.filter(f => f.current_workflow_step > 0 && f.current_workflow_step < 11).length} icon={<WorkflowIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Overdue" value={overdueFiles.length} icon={<WarningIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setSearchResults(null) }}>
            <Tab label={`Active (${activeFiles.length})`} />
            <Tab label={`Archived (${archivedFiles.length})`} />
          </Tabs>
          <IconButton onClick={fetchFiles} sx={{ mr: 2 }}><RefreshIcon /></IconButton>
        </Box>

        {loading ? <LinearProgress /> : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>File Number</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Direction</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Step</TableCell>
                  <TableCell>Holder</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Escalation</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayedFiles.length === 0 ? (
                  <TableRow><TableCell colSpan={9} align="center">No files found</TableCell></TableRow>
                ) : displayedFiles.map((file) => (
                  <TableRow key={file.id} hover sx={{ cursor: 'pointer' }} onClick={() => handleViewDetail(file)}>
                    <TableCell><strong>{file.file_number}</strong></TableCell>
                    <TableCell>{file.title}</TableCell>
                    <TableCell><Chip label={file.direction || 'INCOMING'} size="small" variant="outlined" /></TableCell>
                    <TableCell><Chip label={file.status} size="small" color={getStatusColor(file.status)} /></TableCell>
                    <TableCell>
                      {file.current_workflow_step > 0 ? (
                        <Chip label={`Step ${file.current_workflow_step}`} size="small" color="info" />
                      ) : '—'}
                    </TableCell>
                    <TableCell>{file.current_holder_name || '—'}</TableCell>
                    <TableCell><Chip label={file.priority || 'NORMAL'} size="small" color={getPriorityColor(file.priority)} /></TableCell>
                    <TableCell>
                      {file.escalation_status === 'ESCALATED' && (
                        <Chip label="Escalated" size="small" color="error" icon={<WarningIcon />} />
                      )}
                      {file.is_overdue && (
                        <Chip label="Overdue" size="small" color="error" sx={{ ml: 0.5 }} />
                      )}
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Tooltip title="Advance Workflow">
                        <IconButton size="small" color="primary" onClick={() => handleAdvanceWorkflow(file)}>
                          <AdvanceIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Move">
                        <IconButton size="small" onClick={() => handleMove(file)}><MoveIcon fontSize="small" /></IconButton>
                      </Tooltip>
                      {file.status === 'DRAFT' && (
                        <Tooltip title="Submit">
                          <IconButton size="small" color="primary" onClick={() => handleSubmitFile(file)}><SubmitIcon fontSize="small" /></IconButton>
                        </Tooltip>
                      )}
                      {file.status === 'PENDING' && (
                        <>
                          <Tooltip title="Approve">
                            <IconButton size="small" color="success" onClick={() => handleApproveFile(file)}><ApproveIcon fontSize="small" /></IconButton>
                          </Tooltip>
                          <Tooltip title="Reject">
                            <IconButton size="small" color="error" onClick={() => handleRejectFile(file)}><RejectIcon fontSize="small" /></IconButton>
                          </Tooltip>
                        </>
                      )}
                      <Tooltip title="Escalate">
                        <IconButton size="small" color="warning" onClick={() => handleEscalateFile(file)}><EscalateIcon fontSize="small" /></IconButton>
                      </Tooltip>
                      <Tooltip title="Archive">
                        <IconButton size="small" onClick={() => handleClose(file)}><ArchiveIcon fontSize="small" /></IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* File Detail Dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{selectedFile?.file_number} — {selectedFile?.title}</span>
          {selectedFile?.is_overdue && <Chip label="OVERDUE" color="error" icon={<WarningIcon />} />}
        </DialogTitle>
        <DialogContent>
          {selectedFile && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={4}>
                  <Typography variant="body2"><strong>Category:</strong> {FILE_CATEGORIES.find(c => c.value === selectedFile.file_category)?.label}</Typography>
                  <Typography variant="body2"><strong>Type:</strong> {selectedFile.file_type}</Typography>
                  <Typography variant="body2"><strong>Direction:</strong> {selectedFile.direction || 'INCOMING'}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2"><strong>Status:</strong> <Chip label={selectedFile.status} size="small" color={getStatusColor(selectedFile.status)} /></Typography>
                  <Typography variant="body2"><strong>Priority:</strong> <Chip label={selectedFile.priority} size="small" color={getPriorityColor(selectedFile.priority)} /></Typography>
                  <Typography variant="body2"><strong>Holder:</strong> {selectedFile.current_holder_name || '—'}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2"><strong>Workflow Step:</strong> {selectedFile.current_workflow_step || 0}</Typography>
                  <Typography variant="body2"><strong>Escalation:</strong> <Chip label={selectedFile.escalation_status || 'NORMAL'} size="small" color={selectedFile.escalation_status === 'ESCALATED' ? 'error' : 'default'} /></Typography>
                  {selectedFile.escalation_reason && (
                    <Typography variant="body2"><strong>Reason:</strong> {selectedFile.escalation_reason}</Typography>
                  )}
                </Grid>
              </Grid>

              {selectedFile.description && (
                <Typography variant="body2" sx={{ mb: 2 }}><strong>Description:</strong> {selectedFile.description}</Typography>
              )}

              {/* Workflow Visualization */}
              {workflowData && (
                <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
                    Workflow Progress ({workflowData.progress_percent}%)
                  </Typography>
                  <LinearProgress variant="determinate" value={workflowData.progress_percent} sx={{ mb: 2 }} />
                  <Stepper activeStep={(workflowData.file?.current_step || 0)} sx={{ mb: 2 }}>
                    {workflowData.workflow_steps?.map((step) => (
                      <Step key={step.step} completed={step.is_completed}>
                        <StepLabel
                          error={step.is_current && selectedFile.escalation_status === 'ESCALATED'}
                        >
                          <Tooltip title={`${step.label} (${step.location})`}>
                            <span>{step.label}</span>
                          </Tooltip>
                        </StepLabel>
                      </Step>
                    ))}
                  </Stepper>
                </Box>
              )}

              <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                <Button variant="outlined" startIcon={<AdvanceIcon />} onClick={() => { handleAdvanceWorkflow(selectedFile); setDetailOpen(false) }}>
                  Advance Workflow
                </Button>
                <Button variant="outlined" startIcon={<MoveIcon />} onClick={() => { setDetailOpen(false); handleMove(selectedFile) }}>Move</Button>
                <Button variant="outlined" startIcon={<EscalateIcon />} onClick={() => { setDetailOpen(false); handleEscalateFile(selectedFile) }}>Escalate</Button>
                <Button variant="outlined" color="error" startIcon={<ArchiveIcon />} onClick={() => { handleClose(selectedFile); setDetailOpen(false) }}>Archive</Button>
              </Box>

              {selectedFile.movements?.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Movement History</Typography>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>From</TableCell>
                        <TableCell>To</TableCell>
                        <TableCell>Action</TableCell>
                        <TableCell>Step</TableCell>
                        <TableCell>Location</TableCell>
                        <TableCell>Remarks</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedFile.movements.map((m) => (
                        <TableRow key={m.id}>
                          <TableCell>{m.from_holder_name}</TableCell>
                          <TableCell>{m.to_holder_name || '—'}</TableCell>
                          <TableCell><Chip label={m.action} size="small" /></TableCell>
                          <TableCell>{m.workflow_step || '—'}</TableCell>
                          <TableCell>{m.from_location && m.to_location ? `${m.from_location} → ${m.to_location}` : '—'}</TableCell>
                          <TableCell>{m.remarks}</TableCell>
                          <TableCell>{new Date(m.movement_date).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
              )}

              {selectedFile.status_timeline?.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Status Timeline</Typography>
                  <Table size="small">
                    <TableHead><TableRow><TableCell>Status</TableCell><TableCell>Action</TableCell><TableCell>Changed By</TableCell><TableCell>Notes</TableCell><TableCell>Timestamp</TableCell></TableRow></TableHead>
                    <TableBody>
                      {selectedFile.status_timeline.slice(-10).map((entry, idx) => (
                        <TableRow key={idx}>
                          <TableCell><Chip label={entry.status} size="small" color={getStatusColor(entry.status)} /></TableCell>
                          <TableCell>{entry.action || '—'}</TableCell>
                          <TableCell>{entry.changed_by_name}</TableCell>
                          <TableCell>{entry.notes}</TableCell>
                          <TableCell>{new Date(entry.timestamp).toLocaleString()}</TableCell>
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

      {/* Create File Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New File</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth required label="Title" value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Description" multiline rows={2} value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Direction</InputLabel>
                <Select value={formData.direction} onChange={(e) => setFormData({ ...formData, direction: e.target.value })} label="Direction">
                  {DIRECTIONS.map((d) => <MenuItem key={d.value} value={d.value}>{d.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>File Category</InputLabel>
                <Select value={formData.file_category} onChange={(e) => setFormData({ ...formData, file_category: e.target.value })} label="File Category">
                  {FILE_CATEGORIES.map((c) => <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>File Type</InputLabel>
                <Select value={formData.file_type} onChange={(e) => setFormData({ ...formData, file_type: e.target.value })} label="File Type">
                  {FILE_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Classification</InputLabel>
                <Select value={formData.classification} onChange={(e) => setFormData({ ...formData, classification: e.target.value })} label="Classification">
                  {CLASSIFICATIONS.map((c) => <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })} label="Priority">
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="NORMAL">Normal</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="URGENT">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} label="Status">
                  {FILE_STATUSES.map((s) => <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitCreate} variant="contained" disabled={!formData.title}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Move File Dialog */}
      <Dialog open={openMovementDialog} onClose={() => setOpenMovementDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {moveData.action === 'ESCALATED' ? <EscalateIcon /> : <MoveIcon />}
          {moveData.action === 'ESCALATED' ? 'Escalate' : 'Move'} File — {selectedFile?.file_number}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {moveData.action !== 'ESCALATED' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Move To (auto-assign if empty)</InputLabel>
                  <Select value={moveData.to_holder_id} onChange={(e) => setMoveData({ ...moveData, to_holder_id: e.target.value })} label="Move To (auto-assign if empty)">
                    <MenuItem value="">Auto-assign (Workflow)</MenuItem>
                    {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            )}
            {moveData.action === 'ESCALATED' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Escalate To</InputLabel>
                  <Select value={moveData.to_holder_id} onChange={(e) => setMoveData({ ...moveData, to_holder_id: e.target.value })} label="Escalate To">
                    {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            )}
            {moveData.action !== 'ESCALATED' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Action</InputLabel>
                  <Select value={moveData.action} onChange={(e) => setMoveData({ ...moveData, action: e.target.value })} label="Action">
                    {MOVE_ACTIONS.map((a) => <MenuItem key={a.value} value={a.value}>{a.label}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            )}
            <Grid item xs={12}>
              <TextField fullWidth label="Remarks" multiline rows={2} value={moveData.remarks}
                onChange={(e) => setMoveData({ ...moveData, remarks: e.target.value })} />
            </Grid>
            {moveData.action !== 'ESCALATED' && (
              <Grid item xs={12}>
                <TextField fullWidth type="date" label="Expected Return Date" value={moveData.expected_return_date}
                  onChange={(e) => setMoveData({ ...moveData, expected_return_date: e.target.value })}
                  InputLabelProps={{ shrink: true }} />
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMovementDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitMove} variant="contained"
            disabled={moveData.action === 'ESCALATED' && !moveData.to_holder_id}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {moveData.action === 'ESCALATED' ? 'Escalate' : 'Move File'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Files
