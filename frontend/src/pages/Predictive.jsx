import { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Container,
  LinearProgress,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
} from '@mui/material'
import {
  Assessment as AssessIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

function getRiskColor(level) {
  switch (level) {
    case 'HIGH':
      return 'error'
    case 'MEDIUM':
      return 'warning'
    case 'LOW':
      return 'success'
    default:
      return 'default'
  }
}

function getRiskChipColor(score) {
  if (score >= 70) return { bgcolor: '#FFEBEE', color: '#C62828', border: '#EF9A9A' }
  if (score >= 40) return { bgcolor: '#FFF3E0', color: '#E65100', border: '#FFCC80' }
  return { bgcolor: '#E8F5E9', color: '#2E7D32', border: '#A5D6A7' }
}

function Predictive() {
  const [riskProfiles, setRiskProfiles] = useState([])
  const [riskSummary, setRiskSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [schools, setSchools] = useState([])

  const [filterSchool, setFilterSchool] = useState('')
  const [filterRiskLevel, setFilterRiskLevel] = useState('')

  const fetchRiskProfiles = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const params = new URLSearchParams()
      if (filterSchool) params.append('school', filterSchool)
      if (filterRiskLevel) params.append('risk_level', filterRiskLevel)
      const query = params.toString()
      const response = await api.get(`/predictive/risk-profiles/${query ? `?${query}` : ''}`)
      setRiskProfiles(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load risk profiles')
    } finally {
      setLoading(false)
    }
  }, [filterSchool, filterRiskLevel])

  const fetchRiskSummary = useCallback(async () => {
    try {
      const response = await api.get('/predictive/risk-summary/')
      setRiskSummary(response.data)
    } catch (err) {
      // silent
    }
  }, [])

  const fetchAlerts = useCallback(async () => {
    try {
      const response = await api.get('/predictive/alerts/')
      setAlerts(response.data.results || response.data)
    } catch (err) {
      // silent
    }
  }, [])

  const fetchSchools = useCallback(async () => {
    try {
      const response = await api.get('/schools/schools/')
      setSchools(response.data.results || response.data)
    } catch (err) {
      // silent
    }
  }, [])

  useEffect(() => {
    fetchRiskProfiles()
    fetchRiskSummary()
    fetchAlerts()
    fetchSchools()
  }, [fetchRiskProfiles, fetchRiskSummary, fetchAlerts, fetchSchools])

  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true)
      setError('')
      setSuccess('')
      const response = await api.post('/predictive/analyze-all/')
      setSuccess(response.data?.message || 'Analysis completed successfully')
      await Promise.all([fetchRiskProfiles(), fetchRiskSummary(), fetchAlerts()])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run analysis')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleRefresh = () => {
    setError('')
    setSuccess('')
    fetchRiskProfiles()
    fetchRiskSummary()
    fetchAlerts()
  }

  const totalStudents = riskSummary?.total_students ?? riskProfiles.length
  const highRisk = riskSummary?.high_risk ?? riskProfiles.filter(p => p.risk_level === 'HIGH').length
  const mediumRisk = riskSummary?.medium_risk ?? riskProfiles.filter(p => p.risk_level === 'MEDIUM').length
  const lowRisk = riskSummary?.low_risk ?? riskProfiles.filter(p => p.risk_level === 'LOW').length

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            Predictive Analytics - Student Risk Assessment
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Early warning system for dropout prevention and intervention planning
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={analyzing ? null : <RunIcon />}
            onClick={handleRunAnalysis}
            disabled={analyzing}
            sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#A00D24' } }}
          >
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}
      {alerts.length > 0 && !error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 0.5 }}>Early Warning Alerts</Typography>
          {alerts.slice(0, 3).map((alert, idx) => (
            <Typography key={idx} variant="body2">
              {alert.message || `Student at risk: ${alert.student_name || 'Unknown'}`}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Analyzing progress */}
      {analyzing && <LinearProgress sx={{ mb: 2, bgcolor: '#FFCDD2', '& .MuiLinearProgress-bar': { bgcolor: lagosRed } }} />}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Students Analyzed" value={totalStudents} icon={<AssessIcon />} color={lagosRed} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="High Risk" value={highRisk} icon={<WarningIcon />} color="#C62828" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Medium Risk" value={mediumRisk} icon={<WarningIcon />} color="#E65100" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Low Risk" value={lowRisk} icon={<AssessIcon />} color="#2E7D32" />
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5 }}>
          Filter by
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              size="small"
              select
              label="School"
              value={filterSchool}
              onChange={(e) => setFilterSchool(e.target.value)}
            >
              <MenuItem value="">All Schools</MenuItem>
              {schools.map((school) => (
                <MenuItem key={school.id} value={school.id}>
                  {school.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              size="small"
              select
              label="Risk Level"
              value={filterRiskLevel}
              onChange={(e) => setFilterRiskLevel(e.target.value)}
            >
              <MenuItem value="">All Risk Levels</MenuItem>
              <MenuItem value="HIGH">High Risk</MenuItem>
              <MenuItem value="MEDIUM">Medium Risk</MenuItem>
              <MenuItem value="LOW">Low Risk</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Risk Profiles Table */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Student Risk Profiles
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {riskProfiles.length} record{riskProfiles.length !== 1 ? 's' : ''}
          </Typography>
        </Box>

        {loading ? (
          <LinearProgress sx={{ bgcolor: '#FFCDD2', '& .MuiLinearProgress-bar': { bgcolor: lagosRed } }} />
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#FFF5F5' }}>
                  <TableCell sx={{ fontWeight: 700 }}>Student</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Risk Score</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Risk Level</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Risk Factors</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Last Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {riskProfiles.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">
                        No risk profiles found. Run an analysis to generate risk assessments.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  riskProfiles.map((profile) => {
                    const chipStyle = getRiskChipColor(profile.risk_score ?? 0)
                    return (
                      <TableRow key={profile.id} hover>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {profile.student_name || profile.student_display_name || `-`}
                          </Typography>
                          {profile.school_name && (
                            <Typography variant="caption" color="text.secondary">
                              {profile.school_name}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${profile.risk_score ?? 0}%`}
                            size="small"
                            sx={{
                              bgcolor: chipStyle.bgcolor,
                              color: chipStyle.color,
                              border: `1px solid ${chipStyle.border}`,
                              fontWeight: 600,
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={profile.risk_level || 'N/A'}
                            size="small"
                            color={getRiskColor(profile.risk_level)}
                          />
                        </TableCell>
                        <TableCell>
                          {profile.risk_factors && Array.isArray(profile.risk_factors) ? (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {profile.risk_factors.map((factor, idx) => (
                                <Chip key={idx} label={factor} size="small" variant="outlined" />
                              ))}
                            </Box>
                          ) : profile.risk_factors ? (
                            <Typography variant="body2" color="text.secondary">
                              {profile.risk_factors}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              -
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {profile.last_updated
                              ? new Date(profile.last_updated).toLocaleDateString()
                              : profile.created_at
                                ? new Date(profile.created_at).toLocaleDateString()
                                : '-'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Risk Summary Breakdown */}
      {riskSummary && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Risk Summary Breakdown
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: '#FFEBEE',
                  border: '1px solid #EF9A9A',
                  textAlign: 'center',
                }}
              >
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#C62828' }}>
                  {highRisk}
                </Typography>
                <Typography variant="body2" sx={{ color: '#C62828', fontWeight: 500 }}>
                  High Risk
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Score 70-100% · Immediate intervention required
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: '#FFF3E0',
                  border: '1px solid #FFCC80',
                  textAlign: 'center',
                }}
              >
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#E65100' }}>
                  {mediumRisk}
                </Typography>
                <Typography variant="body2" sx={{ color: '#E65100', fontWeight: 500 }}>
                  Medium Risk
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Score 40-69% · Monitoring and support needed
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: '#E8F5E9',
                  border: '1px solid #A5D6A7',
                  textAlign: 'center',
                }}
              >
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#2E7D32' }}>
                  {lowRisk}
                </Typography>
                <Typography variant="body2" sx={{ color: '#2E7D32', fontWeight: 500 }}>
                  Low Risk
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Score 0-39% · Regular monitoring
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Box>
  )
}

export default Predictive
