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
  Card,
  CardContent,
} from '@mui/material'
import {
  DevicesOther as DeviceIcon,
  Sensors as SensorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const statusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'online':
      return 'success'
    case 'offline':
      return 'error'
    case 'maintenance':
      return 'warning'
    default:
      return 'default'
  }
}

const severityColor = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return 'error'
    case 'high':
      return 'warning'
    case 'medium':
      return 'info'
    case 'low':
      return 'default'
    default:
      return 'default'
  }
}

function TabPanel({ children, value, index }) {
  if (value !== index) return null
  return <Box sx={{ pt: 3 }}>{children}</Box>
}

function IoT() {
  const [tabValue, setTabValue] = useState(0)
  const [devices, setDevices] = useState([])
  const [readings, setReadings] = useState([])
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      const [devicesRes, readingsRes, alertsRes, statsRes] = await Promise.all([
        api.get('/iot/iot-devices/'),
        api.get('/iot/sensor-readings/'),
        api.get('/iot/iot-alerts/'),
        api.get('/iot/iot-devices/device_stats/'),
      ])
      setDevices(devicesRes.data.results || devicesRes.data)
      setReadings(readingsRes.data.results || readingsRes.data)
      setAlerts(alertsRes.data.results || alertsRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error fetching IoT data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchData()
  }

  const handleAcknowledge = async (alertId) => {
    try {
      await api.post(`/iot/iot-alerts/${alertId}/acknowledge/`)
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'ACKNOWLEDGED' } : a))
      )
    } catch (error) {
      console.error('Error acknowledging alert:', error)
    }
  }

  const onlineDevices = devices.filter((d) => d.status?.toLowerCase() === 'online')
  const offlineDevices = devices.filter((d) => d.status?.toLowerCase() === 'offline')
  const unacknowledgedAlerts = alerts.filter((a) => a.status?.toLowerCase() !== 'acknowledged')

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress sx={{ mt: 2 }} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
          Loading IoT data...
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">IoT Device Dashboard</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
          sx={{ borderColor: lagosRed, color: lagosRed, '&:hover': { borderColor: '#a00d24', bgcolor: 'rgba(200,16,46,0.04)' } }}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Devices"
            value={devices.length}
            icon={<DeviceIcon />}
            color={lagosRed}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Online"
            value={onlineDevices.length}
            icon={<DeviceIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Offline"
            value={offlineDevices.length}
            icon={<DeviceIcon />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={unacknowledgedAlerts.length}
            icon={<WarningIcon />}
            color="#f57c00"
          />
        </Grid>
      </Grid>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={(_, v) => setTabValue(v)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab icon={<DeviceIcon />} iconPosition="start" label="Devices" />
          <Tab icon={<SensorIcon />} iconPosition="start" label="Readings" />
          <Tab icon={<WarningIcon />} iconPosition="start" label="Alerts" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Container maxWidth={false}>
            {devices.length === 0 ? (
              <Alert severity="info">No devices found.</Alert>
            ) : (
              <Grid container spacing={3}>
                {devices.map((device) => (
                  <Grid item xs={12} sm={6} md={4} key={device.id}>
                    <Card
                      sx={{
                        height: '100%',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
                        },
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            {device.name}
                          </Typography>
                          <Chip
                            label={device.status}
                            size="small"
                            color={statusColor(device.status)}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                          <strong>Type:</strong> {device.device_type || device.type}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                          <strong>School:</strong> {device.school_name || device.school}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Last Reading:</strong>{' '}
                          {device.last_reading || device.last_reading_value || 'N/A'}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Container>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Container maxWidth={false}>
            {readings.length === 0 ? (
              <Alert severity="info">No readings found.</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell sx={{ fontWeight: 'bold' }}>Device</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Sensor Type</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Value</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Unit</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Timestamp</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Anomaly</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {readings.map((reading) => (
                      <TableRow key={reading.id} hover>
                        <TableCell>{reading.device_name || reading.device}</TableCell>
                        <TableCell>{reading.sensor_type}</TableCell>
                        <TableCell>{reading.value}</TableCell>
                        <TableCell>{reading.unit}</TableCell>
                        <TableCell>
                          {reading.timestamp
                            ? new Date(reading.timestamp).toLocaleString()
                            : reading.created_at
                            ? new Date(reading.created_at).toLocaleString()
                            : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {reading.is_anomaly || reading.anomaly ? (
                            <Chip label="Anomaly" size="small" color="error" icon={<WarningIcon />} />
                          ) : (
                            <Chip label="Normal" size="small" color="success" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Container>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Container maxWidth={false}>
            {alerts.length === 0 ? (
              <Alert severity="info">No alerts found.</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell sx={{ fontWeight: 'bold' }}>Severity</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Condition</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Device</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Message</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Created</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {alerts.map((alert) => (
                      <TableRow key={alert.id} hover>
                        <TableCell>
                          <Chip
                            label={alert.severity}
                            size="small"
                            color={severityColor(alert.severity)}
                          />
                        </TableCell>
                        <TableCell>{alert.condition}</TableCell>
                        <TableCell>{alert.device_name || alert.device}</TableCell>
                        <TableCell>{alert.message || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={alert.status}
                            size="small"
                            color={alert.status?.toLowerCase() === 'acknowledged' ? 'success' : 'warning'}
                          />
                        </TableCell>
                        <TableCell>
                          {alert.created_at
                            ? new Date(alert.created_at).toLocaleString()
                            : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {alert.status?.toLowerCase() !== 'acknowledged' && (
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => handleAcknowledge(alert.id)}
                              sx={{
                                borderColor: lagosRed,
                                color: lagosRed,
                                '&:hover': { borderColor: '#a00d24', bgcolor: 'rgba(200,16,46,0.04)' },
                              }}
                            >
                              Acknowledge
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Container>
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default IoT
