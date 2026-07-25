import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
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
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Container,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  IconButton,
  Alert,
  Tooltip,
} from '@mui/material'
import {
  Add as AddIcon,
  FolderOpen as FileIcon,
  MoveUp as MoveIcon,
  Send as SubmitIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Upgrade as EscalateIcon,
  Archive as ArchiveIcon,
  Refresh as RefreshIcon,
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

const FILE_STEPS = ['Draft', 'Active', 'Pending', 'In Transit', 'Under Review', 'Approved', 'Rejected', 'Closed', 'Archived']

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
  const [formData, setFormData] = useState({
    title: '',
    file_type: 'CORRESPONDENCE',
    file_category: 'ADMIN',
    status: 'DRAFT',
    classification: 'CONFIDENTIAL',
    priority: 'NORMAL',
    description: '',
  })
  const [moveData, setMoveData] = useState({
    to_holder_id: '',
    action: 'FORWARDED',
    remarks: '',
    expected_return_date: '',
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
      title: '',
      file_type: 'CORRESPONDENCE',
      file_category: 'ADMIN',
      status: 'DRAFT',
      classification: 'CONFIDENTIAL',
      priority: 'NORMAL',
      description: '',
    })
    setOpenDialog(true)
  }

  const handleMove = (file) => {
    setSelectedFile(file)
    setMoveData({ to_holder_id: '', action: 'FORWARDED', remarks: '', expected_return_date: '' })
    setOpenMovementDialog(true)
  }

  const handleViewDetail = (file) => {
    setSelectedFile(file)
    setDetailOpen(true)
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
    setMoveData({ to_holder_id: '', action: 'ESCALATED', remarks: '', expected_return_date: '' })
    setOpenMovementDialog(true)
  }

  const handleSubmitMove = async () => {
    try {
      const endpoint = moveData.action === 'ESCALATED'
        ? `/files/files/${selectedFile.id}/escalate/`
        : `/files/files/${selectedFile.id}/move/`

      const payload = moveData.action === 'ESCALATED'
        ? { to_holder_id: parseInt(moveData.to_holder_id), notes: moveData.remarks }
        : {
            to_holder_id: parseInt(moveData.to_holder_id),
            action: moveData.action,
            remarks: moveData.remarks,
            expected_return_date: moveData.expected_return_date || undefined,
          }

      await api.post(endpoint, payload)
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'DRAFT': return 'default'
      case 'ACTIVE': return 'success'
      case 'PENDING': return 'warning'
      case 'IN_TRANSIT': return 'info'
      case 'UNDER_REVIEW': return 'warning'
      case 'APPROVED': return 'success'
      case 'REJECTED': return 'error'
      case 'CLOSED': return 'default'
      case 'ARCHIVED': return 'default'
      default: return 'default'
    }
  }

  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'PUBLIC': return 'success'
      case 'CONFIDENTIAL': return 'warning'
      case 'RESTRICTED': return 'error'
      case 'TOP_SECRET': return 'error'
      default: return 'default'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'error'
      case 'URGENT': return 'error'
      case 'NORMAL': return 'info'
      case 'LOW': return 'default'
      default: return 'default'
    }
  }

  const activeFiles = files.filter(f => !['ARCHIVED', 'CLOSED'].includes(f.status))
  const archivedFiles = files.filter(f => ['ARCHIVED', 'CLOSED'].includes(f.status))
  const displayedFiles = tabValue === 0 ? activeFiles : archivedFiles

  const activeStep = selectedFile
    ? FILE_STEPS.findIndex(s => s.toLowerCase().replace(' ', '_') === selectedFile.status)
    : 0

  const columns = [
    { id: 'file_number', label: 'File Number' },
    { id: 'title', label: 'Title' },
    { id: 'file_category', label: 'Category', render: (row) => {
      const cat = FILE_CATEGORIES.find(c => c.value === row.file_category)
      return <Chip label={cat?.label || row.file_category} size="small" />
    }},
    { id: 'file_type', label: 'Type' },
    { id: 'status', label: 'Status', render: (row) => (
      <Chip label={row.status} size="small" color={getStatusColor(row.status)} />
    )},
    { id: 'current_holder_name', label: 'Current Holder' },
    { id: 'classification', label: 'Classification', render: (row) => (
      <Chip label={row.classification} size="small" color={getClassificationColor(row.classification)} />
    )},
    { id: 'priority', label: 'Priority', render: (row) => (
      <Chip label={row.priority || 'NORMAL'} size="small" color={getPriorityColor(row.priority)} />
    )},
  ]

  if (loading) {
    return <Loading message="Loading files..." />
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">E-Registry File Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
        >
          New File
        </Button>
      </Box>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>
          {alert.msg}
        </Alert>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Files" value={files.length} icon={<FileIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Files" value={activeFiles.length} icon={<FileIcon />} color="#388e3c" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Review" value={files.filter(f => f.status === 'PENDING' || f.status === 'UNDER_REVIEW').length} icon={<FileIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Archived" value={archivedFiles.length} icon={<ArchiveIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
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
                  <TableCell>Category</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Holder</TableCell>
                  <TableCell>Classification</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayedFiles.length === 0 ? (
                  <TableRow><TableCell colSpan={9} align="center">No files found</TableCell></TableRow>
                ) : displayedFiles.map((file) => (
                  <TableRow key={file.id} hover sx={{ cursor: 'pointer' }}
                    onClick={() => handleViewDetail(file)}>
                    <TableCell><strong>{file.file_number}</strong></TableCell>
                    <TableCell>{file.title}</TableCell>
                    <TableCell><Chip label={FILE_CATEGORIES.find(c => c.value === file.file_category)?.label || file.file_category} size="small" /></TableCell>
                    <TableCell>{file.file_type}</TableCell>
                    <TableCell><Chip label={file.status} size="small" color={getStatusColor(file.status)} /></TableCell>
                    <TableCell>{file.current_holder_name || '—'}</TableCell>
                    <TableCell><Chip label={file.classification} size="small" color={getClassificationColor(file.classification)} /></TableCell>
                    <TableCell><Chip label={file.priority || 'NORMAL'} size="small" color={getPriorityColor(file.priority)} /></TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Tooltip title="Move">
                        <IconButton size="small" onClick={() => handleMove(file)}><MoveIcon fontSize="small" /></IconButton>
                      </Tooltip>
                      {file.status === 'DRAFT' && (
                        <Tooltip title="Submit for Review">
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
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedFile?.file_number} — {selectedFile?.title}</DialogTitle>
        <DialogContent>
          {selectedFile && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2"><strong>Category:</strong> {FILE_CATEGORIES.find(c => c.value === selectedFile.file_category)?.label}</Typography>
                  <Typography variant="body2"><strong>Type:</strong> {selectedFile.file_type}</Typography>
                  <Typography variant="body2"><strong>Classification:</strong> {selectedFile.classification}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2"><strong>Status:</strong> <Chip label={selectedFile.status} size="small" color={getStatusColor(selectedFile.status)} /></Typography>
                  <Typography variant="body2"><strong>Priority:</strong> <Chip label={selectedFile.priority} size="small" color={getPriorityColor(selectedFile.priority)} /></Typography>
                  <Typography variant="body2"><strong>Holder:</strong> {selectedFile.current_holder_name || '—'}</Typography>
                </Grid>
              </Grid>

              {selectedFile.description && (
                <Typography variant="body2" sx={{ mb: 2 }}><strong>Description:</strong> {selectedFile.description}</Typography>
              )}

              <Stepper activeStep={activeStep >= 0 ? activeStep : 0} sx={{ mt: 3, mb: 2 }}>
                {FILE_STEPS.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
              </Stepper>

              <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                {selectedFile.status === 'DRAFT' && (
                  <Button variant="outlined" startIcon={<SubmitIcon />} onClick={() => { handleSubmitFile(selectedFile); setDetailOpen(false) }}>Submit for Review</Button>
                )}
                {selectedFile.status === 'PENDING' && (
                  <>
                    <Button variant="outlined" color="success" startIcon={<ApproveIcon />} onClick={() => { handleApproveFile(selectedFile); setDetailOpen(false) }}>Approve</Button>
                    <Button variant="outlined" color="error" startIcon={<RejectIcon />} onClick={() => { handleRejectFile(selectedFile); setDetailOpen(false) }}>Reject</Button>
                  </>
                )}
                <Button variant="outlined" startIcon={<MoveIcon />} onClick={() => { setDetailOpen(false); handleMove(selectedFile) }}>Move</Button>
                <Button variant="outlined" startIcon={<EscalateIcon />} onClick={() => { setDetailOpen(false); handleEscalateFile(selectedFile) }}>Escalate</Button>
                <Button variant="outlined" color="error" startIcon={<ArchiveIcon />} onClick={() => { handleClose(selectedFile); setDetailOpen(false) }}>Archive</Button>
              </Box>

              {selectedFile.movements?.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Movement History</Typography>
                  <Table size="small">
                    <TableHead><TableRow><TableCell>From</TableCell><TableCell>To</TableCell><TableCell>Action</TableCell><TableCell>Remarks</TableCell><TableCell>Date</TableCell></TableRow></TableHead>
                    <TableBody>
                      {selectedFile.movements.map((m) => (
                        <TableRow key={m.id}>
                          <TableCell>{m.from_holder_name}</TableCell>
                          <TableCell>{m.to_holder_name || '—'}</TableCell>
                          <TableCell><Chip label={m.action} size="small" /></TableCell>
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
                    <TableHead><TableRow><TableCell>Status</TableCell><TableCell>Changed By</TableCell><TableCell>Notes</TableCell><TableCell>Timestamp</TableCell></TableRow></TableHead>
                    <TableBody>
                      {selectedFile.status_timeline.map((entry, idx) => (
                        <TableRow key={idx}>
                          <TableCell><Chip label={entry.status} size="small" color={getStatusColor(entry.status)} /></TableCell>
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
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>{moveData.action === 'ESCALATED' ? 'Escalate To' : 'Move To'}</InputLabel>
                <Select value={moveData.to_holder_id} onChange={(e) => setMoveData({ ...moveData, to_holder_id: e.target.value })} label={moveData.action === 'ESCALATED' ? 'Escalate To' : 'Move To'}>
                  {staffList.map((s) => <MenuItem key={s.id} value={s.id}>{s.first_name} {s.last_name}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
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
          <Button onClick={handleSubmitMove} variant="contained" disabled={!moveData.to_holder_id}
            sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}>
            {moveData.action === 'ESCALATED' ? 'Escalate' : 'Move File'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Files
