import { useState, useEffect, useCallback } from 'react'
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
  Container,
  LinearProgress,
  TextField,
  MenuItem,
} from '@mui/material'
import {
  TrendingUp as TrendIcon,
  School as SchoolIcon,
  Refresh as RefreshIcon,
  Compare as CompareIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const performanceColor = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'primary'
  if (score >= 40) return 'warning'
  return 'error'
}

const performanceLabel = (score) => {
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'Fair'
  return 'Poor'
}

function Benchmarking() {
  const [tab, setTab] = useState(0)
  const [rankings, setRankings] = useState([])
  const [schools, setSchools] = useState([])
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState('')

  const [selectedSchools, setSelectedSchools] = useState([])
  const [compareData, setCompareData] = useState(null)
  const [compareLoading, setCompareLoading] = useState(false)

  const [metricsCategory, setMetricsCategory] = useState('')

  const fetchRankings = useCallback(async () => {
    try {
      const response = await api.get('/benchmarking/benchmarks/rankings/')
      setRankings(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load rankings')
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

  const fetchMetrics = useCallback(async () => {
    try {
      const params = metricsCategory ? `?category=${metricsCategory}` : ''
      const response = await api.get(`/benchmarking/metrics/${params}`)
      setMetrics(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load metrics')
    }
  }, [metricsCategory])

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      await Promise.all([fetchRankings(), fetchSchools(), fetchMetrics()])
    } finally {
      setLoading(false)
    }
  }, [fetchRankings, fetchSchools, fetchMetrics])

  useEffect(() => {
    fetchAll()
  }, [fetchAll])

  useEffect(() => {
    if (tab === 2) fetchMetrics()
  }, [tab, metricsCategory, fetchMetrics])

  const handleCalculate = async () => {
    try {
      setCalculating(true)
      setError('')
      await api.post('/benchmarking/benchmarks/calculate/')
      await fetchRankings()
      await fetchMetrics()
    } catch (err) {
      setError('Failed to calculate benchmark metrics')
    } finally {
      setCalculating(false)
    }
  }

  const handleToggleSchool = (schoolId) => {
    setSelectedSchools((prev) => {
      if (prev.includes(schoolId)) return prev.filter((id) => id !== schoolId)
      if (prev.length >= 3) return prev
      return [...prev, schoolId]
    })
  }

  const handleCompare = async () => {
    if (selectedSchools.length < 2) return
    try {
      setCompareLoading(true)
      setError('')
      const ids = selectedSchools
      const response = await api.post('/benchmarking/comparisons/compare/', {
        school_a: ids[0],
        school_b: ids[1],
      })
      setCompareData(response.data)
    } catch (err) {
      setError('Failed to compare schools')
    } finally {
      setCompareLoading(false)
    }
  }

  const handleRefresh = () => {
    setError('')
    if (tab === 0) fetchRankings()
    else if (tab === 1) fetchSchools()
    else fetchMetrics()
  }

  const topSchool = rankings.length > 0 ? rankings[0] : null
  const avgScore = rankings.length > 0
    ? Math.round(rankings.reduce((sum, r) => sum + (r.score || 0), 0) / rankings.length)
    : 0
  const excellentCount = rankings.filter((r) => (r.score || 0) >= 80).length

  return (
    <Box>
      {calculating && <LinearProgress sx={{ mb: 2 }} />}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>School Benchmarking & Rankings</Typography>
          <Typography variant="body2" color="text.secondary">
            Compare school performance across key metrics
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<SchoolIcon />}
            onClick={handleCalculate}
            disabled={calculating}
            sx={{ bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
          >
            {calculating ? 'Calculating...' : 'Calculate Metrics'}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Schools Ranked"
            value={rankings.length}
            icon={<SchoolIcon />}
            color={lagosRed}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Top School"
            value={topSchool?.school_name || topSchool?.name || '-'}
            icon={<TrendIcon />}
            color="#388e3c"
            subtitle={topSchool ? `Score: ${topSchool.score}` : ''}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Average Score"
            value={avgScore}
            icon={<TrendIcon />}
            color="#1a237e"
            subtitle="Across all schools"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Excellent Schools"
            value={excellentCount}
            icon={<TrendIcon />}
            color="#f57c00"
            subtitle="Score >= 80"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ mb: 2 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => { setTab(v); setError('') }}
          sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 } }}
        >
          <Tab label={`Rankings (${rankings.length})`} icon={<TrendIcon />} iconPosition="start" />
          <Tab label="Compare Schools" icon={<CompareIcon />} iconPosition="start" />
          <Tab label={`Metrics (${metrics.length})`} icon={<SchoolIcon />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* Rankings Tab */}
      {tab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 700 }}>Rank</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>School</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Score</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Performance</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Trend</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">Loading rankings...</Typography>
                  </TableCell>
                </TableRow>
              ) : rankings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No rankings available. Click "Calculate Metrics" to generate.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                rankings.map((row, index) => (
                  <TableRow
                    key={row.id || index}
                    hover
                    sx={index < 3 ? { bgcolor: index === 0 ? '#FFF8E1' : index === 1 ? '#F5F5F5' : '#FFF3E0' } : {}}
                  >
                    <TableCell>
                      <Chip
                        label={`#${row.rank || index + 1}`}
                        size="small"
                        sx={{
                          fontWeight: 700,
                          bgcolor: index === 0 ? lagosRed : index < 3 ? '#f57c00' : 'default',
                          color: index < 3 ? '#fff' : 'inherit',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {row.school_name || row.name}
                      </Typography>
                      {row.school_type && (
                        <Typography variant="caption" color="text.secondary">{row.school_type}</Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{row.score ?? '-'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={performanceLabel(row.score)}
                        size="small"
                        color={performanceColor(row.score)}
                      />
                    </TableCell>
                    <TableCell>
                      {row.trend === 'up' && <TrendIcon sx={{ color: '#388e3c', fontSize: 20 }} />}
                      {row.trend === 'down' && <TrendIcon sx={{ color: lagosRed, fontSize: 20, transform: 'rotate(180deg)' }} />}
                      {(!row.trend || row.trend === 'stable') && (
                        <Typography variant="caption" color="text.secondary">-</Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Compare Schools Tab */}
      {tab === 1 && (
        <Box>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Select Schools to Compare (2-3)</Typography>
            <Grid container spacing={1}>
              {schools.map((school) => {
                const isSelected = selectedSchools.includes(school.id)
                return (
                  <Grid item key={school.id}>
                    <Chip
                      label={school.name}
                      onClick={() => handleToggleSchool(school.id)}
                      color={isSelected ? 'primary' : 'default'}
                      variant={isSelected ? 'filled' : 'outlined'}
                      sx={{
                        fontWeight: isSelected ? 600 : 400,
                        borderColor: isSelected ? lagosRed : undefined,
                        bgcolor: isSelected ? lagosRed : undefined,
                        '&:hover': { bgcolor: isSelected ? '#a00d24' : undefined },
                      }}
                    />
                  </Grid>
                )
              })}
            </Grid>
            <Button
              variant="contained"
              startIcon={<CompareIcon />}
              onClick={handleCompare}
              disabled={selectedSchools.length < 2 || compareLoading}
              sx={{ mt: 2, bgcolor: lagosRed, '&:hover': { bgcolor: '#a00d24' } }}
            >
              {compareLoading ? 'Comparing...' : 'Compare Selected'}
            </Button>
          </Paper>

          {compareLoading && <LinearProgress sx={{ mb: 2 }} />}

          {compareData && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3 }}>Comparison Results</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                      <TableCell sx={{ fontWeight: 700 }}>Metric</TableCell>
                      {(compareData.schools || compareData.results || []).map((s) => (
                        <TableCell key={s.id || s.school_name} sx={{ fontWeight: 700 }} align="right">
                          {s.school_name || s.name}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(() => {
                      const schoolList = compareData.schools || compareData.results || []
                      const metricKeys = compareData.metrics || compareData.comparison_metrics || []
                      if (metricKeys.length === 0 && schoolList.length > 0) {
                        const allKeys = new Set()
                        schoolList.forEach((s) => {
                          if (s.metrics) Object.keys(s.metrics).forEach((k) => allKeys.push ? allKeys.add(k) : null)
                          Object.keys(s).forEach((k) => {
                            if (!['id', 'school', 'school_name', 'name', 'score'].includes(k)) allKeys.add(k)
                          })
                        })
                        return Array.from(allKeys).map((key) => (
                          <TableRow key={key}>
                            <TableCell sx={{ fontWeight: 500 }}>{key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</TableCell>
                            {schoolList.map((s) => {
                              const val = s.metrics?.[key] ?? s[key]
                              return (
                                <TableCell key={s.id || s.school_name} align="right">
                                  {typeof val === 'number' ? (
                                    <Box>
                                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{val}</Typography>
                                      <LinearProgress
                                        variant="determinate"
                                        value={Math.min(val, 100)}
                                        sx={{
                                          height: 6,
                                          borderRadius: 3,
                                          mt: 0.5,
                                          '& .MuiLinearProgress-bar': { bgcolor: lagosRed },
                                        }}
                                      />
                                    </Box>
                                  ) : (
                                    val ?? '-'
                                  )}
                                </TableCell>
                              )
                            })}
                          </TableRow>
                        ))
                      }
                      return metricKeys.map((metric) => (
                        <TableRow key={metric.name || metric}>
                          <TableCell sx={{ fontWeight: 500 }}>{metric.name || metric}</TableCell>
                          {schoolList.map((s) => {
                            const val = s.metrics?.[metric.name || metric] ?? s[metric.name || metric]
                            return (
                              <TableCell key={s.id || s.school_name} align="right">
                                {typeof val === 'number' ? (
                                  <Box>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{val}</Typography>
                                    <LinearProgress
                                      variant="determinate"
                                      value={Math.min(val, 100)}
                                      sx={{
                                        height: 6,
                                        borderRadius: 3,
                                        mt: 0.5,
                                        '& .MuiLinearProgress-bar': { bgcolor: lagosRed },
                                      }}
                                    />
                                  </Box>
                                ) : (
                                  val ?? '-'
                                )}
                              </TableCell>
                            )
                          })}
                        </TableRow>
                      ))
                    })()}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {compareData && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Score Comparison</Typography>
              <Grid container spacing={2}>
                {(compareData.schools || compareData.results || []).map((s) => (
                  <Grid item xs={12} sm={4} key={s.id || s.school_name}>
                    <Paper sx={{ p: 2, textAlign: 'center', border: `2px solid ${lagosRed}` }}>
                      <Typography variant="subtitle2" color="text.secondary">{s.school_name || s.name}</Typography>
                      <Typography variant="h3" sx={{ fontWeight: 700, color: lagosRed, my: 1 }}>
                        {s.score ?? s.total_score ?? '-'}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(s.score || s.total_score || 0, 100)}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                          '& .MuiLinearProgress-bar': { bgcolor: lagosRed },
                          bgcolor: '#f5f5f5',
                        }}
                      />
                      <Chip
                        label={performanceLabel(s.score || s.total_score)}
                        size="small"
                        color={performanceColor(s.score || s.total_score)}
                        sx={{ mt: 1 }}
                      />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          )}

          {!compareData && !compareLoading && (
            <Alert severity="info">
              Select 2-3 schools above and click "Compare Selected" to see a side-by-side comparison.
            </Alert>
          )}
        </Box>
      )}

      {/* Metrics Tab */}
      {tab === 2 && (
        <Box>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              select
              size="small"
              label="Category"
              value={metricsCategory}
              onChange={(e) => setMetricsCategory(e.target.value)}
              sx={{ minWidth: 200 }}
            >
              <MenuItem value="">All Categories</MenuItem>
              <MenuItem value="ACADEMIC">Academic</MenuItem>
              <MenuItem value="INFRASTRUCTURE">Infrastructure</MenuItem>
              <MenuItem value="STAFF">Staff</MenuItem>
              <MenuItem value="STUDENT">Student</MenuItem>
              <MenuItem value="FINANCIAL">Financial</MenuItem>
            </TextField>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                  <TableCell sx={{ fontWeight: 700 }}>Category</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Metric</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">Value</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">Target</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">Loading metrics...</Typography>
                    </TableCell>
                  </TableRow>
                ) : metrics.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No benchmark metrics available.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  metrics.map((row, index) => {
                    const value = row.value ?? row.metric_value ?? 0
                    const target = row.target ?? row.target_value ?? 100
                    const percentage = target > 0 ? Math.round((value / target) * 100) : 0
                    const met = percentage >= 100

                    return (
                      <TableRow key={row.id || index} hover>
                        <TableCell>
                          <Chip
                            label={row.category || 'General'}
                            size="small"
                            variant="outlined"
                            sx={{ textTransform: 'capitalize' }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {row.name || row.metric_name || row.label}
                          </Typography>
                          {row.description && (
                            <Typography variant="caption" color="text.secondary">{row.description}</Typography>
                          )}
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>{value}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="text.secondary">{target}</Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={Math.min(percentage, 100)}
                              sx={{
                                height: 8,
                                borderRadius: 4,
                                flexGrow: 1,
                                '& .MuiLinearProgress-bar': { bgcolor: met ? '#388e3c' : lagosRed },
                                bgcolor: '#f5f5f5',
                              }}
                            />
                            <Chip
                              label={met ? 'Met' : `${percentage}%`}
                              size="small"
                              color={met ? 'success' : percentage >= 70 ? 'warning' : 'error'}
                            />
                          </Box>
                        </TableCell>
                      </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Box>
  )
}

export default Benchmarking
