import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  MenuItem,
  TextField,
  IconButton,
  LinearProgress,
  Container,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const MODEL_OPTIONS = [
  { value: 'students', label: 'Students' },
  { value: 'staff', label: 'Staff' },
  { value: 'schools', label: 'Schools' },
]

const FORMAT_OPTIONS = [
  { value: 'csv', label: 'CSV' },
  { value: 'excel', label: 'Excel' },
  { value: 'pdf', label: 'PDF' },
  { value: 'word', label: 'Word' },
  { value: 'json', label: 'JSON' },
]

function DataImportExport() {
  const [tabValue, setTabValue] = useState(0)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [importing, setImporting] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [importModel, setImportModel] = useState('students')
  const [exportModel, setExportModel] = useState('students')
  const [exportFormat, setExportFormat] = useState('csv')
  const [alert, setAlert] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/data-import-export/jobs/')
      setJobs(res.data.results || res.data)
    } catch {
      setAlert({ type: 'error', msg: 'Failed to load import jobs' })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleImport = async () => {
    if (!selectedFile) {
      setAlert({ type: 'error', msg: 'Please select a file to import' })
      return
    }
    setImporting(true)
    setAlert(null)
    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('model', importModel)
    try {
      const res = await api.post('/data-import-export/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const job = res.data
      if (job.error_rows > 0) {
        setAlert({
          type: 'warning',
          msg: `Imported ${job.success_rows}/${job.total_rows} rows. ${job.error_rows} errors.`,
        })
      } else {
        setAlert({
          type: 'success',
          msg: `Successfully imported ${job.success_rows} rows from ${job.file_name}`,
        })
      }
      setSelectedFile(null)
      fetchJobs()
    } catch (err) {
      setAlert({ type: 'error', msg: err.response?.data?.error || 'Import failed' })
    } finally {
      setImporting(false)
    }
  }

  const handleExport = async () => {
    setAlert(null)
    try {
      const res = await api.get('/data-import-export/export/', {
        params: { model: exportModel, format: exportFormat },
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      const ext = exportFormat === 'excel' ? 'xlsx' : exportFormat === 'word' ? 'docx' : exportFormat
      link.href = url
      link.setAttribute('download', `${exportModel}_export.${ext}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      setAlert({ type: 'success', msg: `Exported ${exportModel} as ${exportFormat.toUpperCase()}` })
    } catch (err) {
      setAlert({ type: 'error', msg: 'Export failed' })
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0])
    }
  }

  const completedJobs = jobs.filter((j) => j.status === 'COMPLETED')
  const failedJobs = jobs.filter((j) => j.status === 'FAILED')
  const totalImported = completedJobs.reduce((sum, j) => sum + (j.success_rows || 0), 0)

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Data Import / Export
      </Typography>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 2 }}>
          {alert.msg}
        </Alert>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <StatCard title="Total Imports" value={jobs.length} icon={<UploadIcon />} color={lagosRed} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Successful" value={completedJobs.length} icon={<CheckIcon />} color="#2e7d32" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard title="Failed" value={failedJobs.length} icon={<ErrorIcon />} color="#d32f2f" />
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Import Data" />
          <Tab label="Export Data" />
          <Tab label="Job History" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Import Data from File
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField
                  select
                  fullWidth
                  label="Target Model"
                  value={importModel}
                  onChange={(e) => setImportModel(e.target.value)}
                >
                  {MODEL_OPTIONS.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={5}>
                <Box
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  sx={{
                    border: '2px dashed',
                    borderColor: dragOver ? lagosRed : '#ccc',
                    borderRadius: 1,
                    p: 2,
                    textAlign: 'center',
                    bgcolor: dragOver ? '#fff5f5' : 'background.paper',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onClick={() => document.getElementById('file-input').click()}
                >
                  <input
                    id="file-input"
                    type="file"
                    accept=".csv,.xlsx,.xls,.pdf,.docx,.json"
                    style={{ display: 'none' }}
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                  />
                  {selectedFile ? (
                    <Typography variant="body2">{selectedFile.name}</Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Drag & drop file here, or click to browse (CSV, Excel, PDF, Word, JSON)
                    </Typography>
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<UploadIcon />}
                  onClick={handleImport}
                  disabled={!selectedFile || importing}
                  sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
                >
                  {importing ? 'Importing...' : 'Import'}
                </Button>
              </Grid>
            </Grid>
            {importing && <LinearProgress sx={{ mt: 2 }} />}
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Export Data
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField
                  select
                  fullWidth
                  label="Data Model"
                  value={exportModel}
                  onChange={(e) => setExportModel(e.target.value)}
                >
                  {MODEL_OPTIONS.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  select
                  fullWidth
                  label="Export Format"
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                >
                  {FORMAT_OPTIONS.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<DownloadIcon />}
                  onClick={handleExport}
                  sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
                >
                  Export
                </Button>
              </Grid>
            </Grid>
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Import Job History</Typography>
              <IconButton onClick={fetchJobs}>
                <RefreshIcon />
              </IconButton>
            </Box>
            {loading ? (
              <LinearProgress />
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>File</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Model</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Rows</TableCell>
                      <TableCell>Success</TableCell>
                      <TableCell>Errors</TableCell>
                      <TableCell>Created By</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {jobs.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} align="center">
                          No import jobs yet
                        </TableCell>
                      </TableRow>
                    ) : (
                      jobs.map((job) => (
                        <TableRow key={job.id}>
                          <TableCell>{job.file_name}</TableCell>
                          <TableCell>
                            <Chip label={job.file_type} size="small" />
                          </TableCell>
                          <TableCell>{job.target_model}</TableCell>
                          <TableCell>
                            <Chip
                              label={job.status}
                              size="small"
                              color={job.status === 'COMPLETED' ? 'success' : job.status === 'FAILED' ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell>{job.total_rows}</TableCell>
                          <TableCell>{job.success_rows}</TableCell>
                          <TableCell>{job.error_rows}</TableCell>
                          <TableCell>{job.created_by_name}</TableCell>
                          <TableCell>{new Date(job.created_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Paper>
    </Container>
  )
}

export default DataImportExport
