import { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Tabs,
  Tab,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  TextField,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Verified as VerifiedIcon,
  Add as AddIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import api from '../api/client'

const CERTIFICATE_TYPES = [
  { value: 'ACADEMIC', label: 'Academic' },
  { value: 'PROFESSIONAL', label: 'Professional' },
  { value: 'TRAINING', label: 'Training' },
  { value: 'EMPLOYMENT', label: 'Employment' },
  { value: 'COMMENDATION', label: 'Commendation' },
  { value: 'DISCIPLINE', label: 'Discipline' },
  { value: 'OTHER', label: 'Other' },
]

const lagosRed = '#C8102E'

function BlockchainCert() {
  const [tabValue, setTabValue] = useState(0)
  const [certificates, setCertificates] = useState([])
  const [loading, setLoading] = useState(true)
  const [verifyHash, setVerifyHash] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)
  const [verifying, setVerifying] = useState(false)
  const [openIssueDialog, setOpenIssueDialog] = useState(false)
  const [issueForm, setIssueForm] = useState({
    student: '',
    certificate_type: '',
    title: '',
    description: '',
  })
  const [issuing, setIssuing] = useState(false)
  const [issueSuccess, setIssueSuccess] = useState(false)
  const [issueError, setIssueError] = useState('')

  const fetchCertificates = useCallback(async () => {
    try {
      const response = await api.get('/blockchain-certs/certificates/')
      setCertificates(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching certificates:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCertificates()
  }, [fetchCertificates])

  const handleVerify = async () => {
    if (!verifyHash.trim()) return
    setVerifying(true)
    setVerificationResult(null)
    try {
      const response = await api.get(`/blockchain-certs/certificates/public-verify/?hash=${encodeURIComponent(verifyHash)}`)
      setVerificationResult({ valid: true, data: response.data })
    } catch (error) {
      if (error.response?.status === 404) {
        setVerificationResult({ valid: false, message: 'Certificate not found or invalid hash.' })
      } else {
        setVerificationResult({ valid: false, message: error.response?.data?.detail || 'Verification failed. Please try again.' })
      }
    } finally {
      setVerifying(false)
    }
  }

  const handleIssueCertificate = async () => {
    setIssueError('')
    setIssueSuccess(false)
    if (!issueForm.student || !issueForm.certificate_type || !issueForm.title) {
      setIssueError('Student, certificate type, and title are required.')
      return
    }
    setIssuing(true)
    try {
      await api.post('/blockchain-certs/certificates/', issueForm)
      setIssueSuccess(true)
      setIssueForm({ student: '', certificate_type: '', title: '', description: '' })
      fetchCertificates()
    } catch (error) {
      setIssueError(error.response?.data?.detail || error.response?.data?.student?.[0] || 'Failed to issue certificate.')
    } finally {
      setIssuing(false)
    }
  }

  const statusColor = (status) => {
    switch (status) {
      case 'VALID': return 'success'
      case 'REVOKED': return 'error'
      case 'PENDING': return 'warning'
      default: return 'default'
    }
  }

  const typeColor = (type) => {
    switch (type) {
      case 'ACADEMIC': return 'primary'
      case 'PROFESSIONAL': return 'secondary'
      case 'TRAINING': return 'info'
      case 'EMPLOYMENT': return 'success'
      case 'COMMENDATION': return 'warning'
      case 'DISCIPLINE': return 'error'
      default: return 'default'
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, color: lagosRed }}>
          Blockchain Certificates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenIssueDialog(true)}
          sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
        >
          Issue Certificate
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: `4px solid ${lagosRed}` }}>
            <CardContent>
              <Typography variant="h6">{certificates.length}</Typography>
              <Typography variant="body2" color="text.secondary">Total Certificates</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #388e3c' }}>
            <CardContent>
              <Typography variant="h6">{certificates.filter(c => c.status === 'VALID').length}</Typography>
              <Typography variant="body2" color="text.secondary">Valid</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #f57c00' }}>
            <CardContent>
              <Typography variant="h6">{certificates.filter(c => c.status === 'PENDING').length}</Typography>
              <Typography variant="body2" color="text.secondary">Pending</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
            <CardContent>
              <Typography variant="h6">{certificates.filter(c => c.status === 'REVOKED').length}</Typography>
              <Typography variant="body2" color="text.secondary">Revoked</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(e, v) => setTabValue(v)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label="My Certificates" />
          <Tab label="Verify Certificate" />
          <Tab label="Issue Certificate" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            {loading ? (
              <LinearProgress sx={{ my: 2 }} />
            ) : certificates.length === 0 ? (
              <Alert severity="info">No certificates found.</Alert>
            ) : (
              <Grid container spacing={3}>
                {certificates.map((cert) => (
                  <Grid item xs={12} sm={6} md={4} key={cert.id}>
                    <Card
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'translateY(-4px)', boxShadow: 3 },
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
                            {cert.title}
                          </Typography>
                          <VerifiedIcon sx={{ color: cert.status === 'VALID' ? '#388e3c' : '#d32f2f' }} />
                        </Box>
                        <Chip
                          label={cert.certificate_type}
                          size="small"
                          color={typeColor(cert.certificate_type)}
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Issued: {new Date(cert.issue_date || cert.created_at).toLocaleDateString()}
                        </Typography>
                        <Chip
                          label={cert.status}
                          size="small"
                          color={statusColor(cert.status)}
                          sx={{ mb: 2 }}
                        />
                        {cert.blockchain_hash && (
                          <Typography
                            variant="caption"
                            sx={{ display: 'block', wordBreak: 'break-all', color: 'text.secondary', mb: 1 }}
                          >
                            Hash: {cert.blockchain_hash.substring(0, 20)}...
                          </Typography>
                        )}
                      </CardContent>
                      <Box sx={{ p: 2, pt: 0 }}>
                        <Button
                          fullWidth
                          variant="outlined"
                          size="small"
                          startIcon={<SearchIcon />}
                          onClick={() => {
                            setVerifyHash(cert.blockchain_hash || cert.id?.toString() || '')
                            setTabValue(1)
                          }}
                          sx={{ borderColor: lagosRed, color: lagosRed, '&:hover': { borderColor: '#a00d24', bgcolor: 'rgba(200, 16, 46, 0.04)' } }}
                        >
                          Verify
                        </Button>
                      </Box>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Verify a Certificate</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Enter a certificate hash or ID to verify its authenticity on the blockchain.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                label="Certificate Hash or ID"
                value={verifyHash}
                onChange={(e) => setVerifyHash(e.target.value)}
                placeholder="Enter certificate hash or ID"
                onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
              />
              <Button
                variant="contained"
                onClick={handleVerify}
                disabled={verifying || !verifyHash.trim()}
                startIcon={<SearchIcon />}
                sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' }, minWidth: 140 }}
              >
                {verifying ? 'Verifying...' : 'Verify'}
              </Button>
            </Box>

            {verifying && <LinearProgress sx={{ mb: 2 }} />}

            {verificationResult && (
              <Alert
                severity={verificationResult.valid ? 'success' : 'error'}
                icon={verificationResult.valid ? <VerifiedIcon /> : undefined}
                sx={{ mb: 2 }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {verificationResult.valid ? 'Certificate Verified' : 'Verification Failed'}
                </Typography>
                {verificationResult.valid && verificationResult.data ? (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">
                      <strong>Title:</strong> {verificationResult.data.title}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Type:</strong> {verificationResult.data.certificate_type}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Student:</strong> {verificationResult.data.student_name || verificationResult.data.student}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Issue Date:</strong> {new Date(verificationResult.data.issue_date || verificationResult.data.created_at).toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Status:</strong> {verificationResult.data.status}
                    </Typography>
                    {verificationResult.data.blockchain_hash && (
                      <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                        <strong>Blockchain Hash:</strong> {verificationResult.data.blockchain_hash}
                      </Typography>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body2">{verificationResult.message}</Typography>
                )}
              </Alert>
            )}
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Issue a New Certificate</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Issue a new blockchain-verified certificate to a student.
            </Typography>

            {issueSuccess && (
              <Alert severity="success" sx={{ mb: 2 }} onClose={() => setIssueSuccess(false)}>
                Certificate issued successfully!
              </Alert>
            )}
            {issueError && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setIssueError('')}>
                {issueError}
              </Alert>
            )}

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  required
                  label="Student ID"
                  value={issueForm.student}
                  onChange={(e) => setIssueForm({ ...issueForm, student: e.target.value })}
                  placeholder="Enter student ID"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  required
                  select
                  label="Certificate Type"
                  value={issueForm.certificate_type}
                  onChange={(e) => setIssueForm({ ...issueForm, certificate_type: e.target.value })}
                >
                  {CERTIFICATE_TYPES.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Title"
                  value={issueForm.title}
                  onChange={(e) => setIssueForm({ ...issueForm, title: e.target.value })}
                  placeholder="e.g. Certificate of Academic Excellence"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={issueForm.description}
                  onChange={(e) => setIssueForm({ ...issueForm, description: e.target.value })}
                  placeholder="Optional description or notes"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="contained"
                  onClick={handleIssueCertificate}
                  disabled={issuing}
                  startIcon={<AddIcon />}
                  sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
                >
                  {issuing ? 'Issuing...' : 'Issue Certificate'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      <Dialog open={openIssueDialog} onClose={() => setOpenIssueDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Issue Certificate</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Student ID"
                value={issueForm.student}
                onChange={(e) => setIssueForm({ ...issueForm, student: e.target.value })}
                placeholder="Enter student ID"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                select
                label="Certificate Type"
                value={issueForm.certificate_type}
                onChange={(e) => setIssueForm({ ...issueForm, certificate_type: e.target.value })}
              >
                {CERTIFICATE_TYPES.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Title"
                value={issueForm.title}
                onChange={(e) => setIssueForm({ ...issueForm, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={issueForm.description}
                onChange={(e) => setIssueForm({ ...issueForm, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenIssueDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleIssueCertificate}
            disabled={issuing}
            sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
          >
            {issuing ? 'Issuing...' : 'Issue'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default BlockchainCert
