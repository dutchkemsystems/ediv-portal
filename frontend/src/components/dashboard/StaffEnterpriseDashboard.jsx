import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Avatar,
  Chip,
  Divider,
  LinearProgress,
} from '@mui/material'
import {
  Person as PersonIcon,
  Badge as BadgeIcon,
  Work as WorkIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
  Star as StarIcon,
  Timeline as TimelineIcon,
  Cake as CakeIcon,
  Groups as GroupsIcon,
  CalendarMonth as CalendarIcon,
  Money as SalaryIcon,
  CreditCard as CardIcon,
  AccountBalance as BankIcon,
  AccessTime as TimeIcon,
  TrendingUp as TrendIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  Legend,
} from 'recharts'
import api from '../../api/client'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'
const lagosGold = '#D4A017'

const metricCardStyles = {
  borderRadius: 3,
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  transition: 'transform 0.2s, box-shadow 0.2s',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
  },
}

const sectionCardStyles = {
  borderRadius: 3,
  boxShadow: '0 2px 16px rgba(0,0,0,0.06)',
  border: '1px solid rgba(0,0,0,0.04)',
}

function StaffEnterpriseDashboard() {
  const { user } = useSelector((state) => state.auth)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user?.id) return
    const fetchProfile = async () => {
      try {
        const res = await api.get(`/analytics/stats/staff-profile/${user.id}/`)
        setProfile(res.data)
      } catch (err) {
        setError('Failed to load staff profile')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [user?.id])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress sx={{ color: lagosRed }} />
      </Box>
    )
  }

  if (error || !profile) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography color="error" variant="h6">{error || 'No profile data available'}</Typography>
      </Box>
    )
  }

  const { personal_info, employment_info, service_timeline, school_history, financial, performance, leave_summary } = profile

  // Calculate service progress (out of 35 years)
  const serviceProgress = Math.min((service_timeline.years_of_service / 35) * 100, 100)
  const ageProgress = Math.min((personal_info.current_age / 60) * 100, 100)

  // Performance radar data
  const radarData = performance
    ? [
        { subject: 'Punctuality', A: performance.punctuality_score, fullMark: 100 },
        { subject: 'Dedication', A: performance.dedication_score, fullMark: 100 },
        { subject: 'Teaching Quality', A: performance.teaching_quality_score, fullMark: 100 },
        { subject: 'Student Performance', A: performance.student_performance_score, fullMark: 100 },
      ]
    : []

  // Radial data for service years
  const radialData = [
    {
      name: 'Years Served',
      value: serviceProgress,
      fill: lagosGreen,
    },
    {
      name: 'Age Progress',
      value: ageProgress,
      fill: lagosRed,
    },
  ]

  const getRatingColor = (rating) => {
    const colors = {
      'Excellent': lagosGreen,
      'Very Good': '#2196F3',
      'Good': lagosGold,
      'Satisfactory': '#FF9800',
      'Needs Improvement': '#FF5722',
      'Unsatisfactory': lagosRed,
    }
    return colors[rating] || '#757575'
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, maxWidth: 1600, mx: 'auto' }}>
      {/* ===== TOP BANNER ===== */}
      <Card sx={{ ...sectionCardStyles, mb: 3, background: `linear-gradient(135deg, ${lagosRed}15, ${lagosGreen}10)` }}>
        <CardContent sx={{ py: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
            <Avatar
              src={personal_info.profile_photo}
              sx={{
                width: 120,
                height: 120,
                border: `4px solid ${lagosGreen}`,
                boxShadow: '0 4px 20px rgba(0,132,61,0.3)',
              }}
            >
              <PersonIcon sx={{ fontSize: 60 }} />
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 200 }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1a1a2e', mb: 0.5 }}>
                {personal_info.full_name}
              </Typography>
              <Typography variant="h6" sx={{ color: lagosGreen, fontWeight: 500, mb: 1 }}>
                {employment_info.designation}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<BadgeIcon />}
                  label={`ID: ${employment_info.staff_id}`}
                  size="small"
                  sx={{ bgcolor: `${lagosRed}15`, color: lagosRed, fontWeight: 600 }}
                />
                <Chip
                  icon={<CakeIcon />}
                  label={`Age: ${personal_info.current_age}`}
                  size="small"
                  sx={{ bgcolor: `${lagosGold}20`, color: '#8B6914', fontWeight: 600 }}
                />
                <Chip
                  icon={<WorkIcon />}
                  label={employment_info.category}
                  size="small"
                  sx={{ bgcolor: `${lagosGreen}15`, color: lagosGreen, fontWeight: 600 }}
                />
              </Box>
            </Box>
            <Box sx={{ textAlign: 'center', px: 3 }}>
              <Typography variant="h2" sx={{ fontWeight: 800, color: lagosGreen, lineHeight: 1 }}>
                {service_timeline.years_of_service}
              </Typography>
              <Typography variant="caption" sx={{ color: '#666', fontWeight: 500 }}>
                Years of Service
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* ===== SERVICE TIMELINE CARD ===== */}
      <Card sx={{ ...sectionCardStyles, mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TimelineIcon sx={{ color: lagosGreen, fontSize: 28 }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>Service Timeline</Typography>
          </Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosGreen}08`, borderRadius: 2 }}>
                <Typography variant="overline" sx={{ color: '#888' }}>First Appointment</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, color: lagosGreen }}>
                  {service_timeline.date_of_first_appointment
                    ? new Date(service_timeline.date_of_first_appointment).toLocaleDateString('en-NG', { year: 'numeric', month: 'long', day: 'numeric' })
                    : 'N/A'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosRed}08`, borderRadius: 2 }}>
                <Typography variant="overline" sx={{ color: '#888' }}>Joined Service</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, color: lagosRed }}>
                  {new Date(service_timeline.date_joined).toLocaleDateString('en-NG', { year: 'numeric', month: 'long', day: 'numeric' })}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosGold}10`, borderRadius: 2 }}>
                <Typography variant="overline" sx={{ color: '#888' }}>Year of Retirement</Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, color: lagosGold }}>
                  {service_timeline.year_of_retirement}
                </Typography>
              </Box>
            </Grid>
          </Grid>
          {/* Service Progress Bar */}
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>Service Progress</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: lagosGreen }}>
                {service_timeline.years_of_service} of 35 years
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={serviceProgress}
              sx={{
                height: 12,
                borderRadius: 6,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 6,
                  background: `linear-gradient(90deg, ${lagosGreen}, ${lagosGold})`,
                },
              }}
            />
          </Box>
          {/* Age Countdown */}
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>Age Progress (to 60)</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: lagosRed }}>
                {personal_info.current_age} of 60 years
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={ageProgress}
              sx={{
                height: 12,
                borderRadius: 6,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 6,
                  background: `linear-gradient(90deg, ${lagosRed}, ${lagosGold})`,
                },
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* ===== KEY METRICS ROW ===== */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Years Served', value: service_timeline.years_of_service, icon: <TimeIcon />, color: lagosGreen, bg: `${lagosGreen}12` },
          { label: 'Years Remaining', value: service_timeline.years_remaining, icon: <TrendIcon />, color: lagosGold, bg: `${lagosGold}15` },
          { label: 'Oracle Number', value: employment_info.employee_number, icon: <AssignmentIcon />, color: lagosRed, bg: `${lagosRed}12` },
          { label: 'Grade / Step', value: `${employment_info.grade_level || 'N/A'} / ${employment_info.step}`, icon: <StarIcon />, color: '#6A1B9A', bg: '#6A1B9A12' },
        ].map((metric, idx) => (
          <Grid item xs={6} md={3} key={idx}>
            <Card sx={{ ...metricCardStyles, bgcolor: metric.bg }}>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <Box sx={{ color: metric.color, mb: 1 }}>{metric.icon}</Box>
                <Typography variant="h4" sx={{ fontWeight: 700, color: metric.color, lineHeight: 1.2 }}>
                  {metric.value}
                </Typography>
                <Typography variant="caption" sx={{ color: '#666', fontWeight: 500 }}>
                  {metric.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* ===== EMPLOYMENT DETAILS + SCHOOL ===== */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={sectionCardStyles}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <WorkIcon sx={{ color: lagosRed, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Employment Details</Typography>
              </Box>
              <Grid container spacing={2}>
                {[
                  { label: 'Category', value: employment_info.category },
                  { label: 'Employment Type', value: employment_info.employment_type },
                  { label: 'Qualification', value: employment_info.qualification },
                  { label: 'Department', value: school_history.department || 'N/A' },
                  { label: 'Designation', value: employment_info.designation },
                  { label: 'Staff ID', value: employment_info.staff_id },
                ].map((item, idx) => (
                  <Grid item xs={6} key={idx}>
                    <Typography variant="caption" sx={{ color: '#888', fontWeight: 500 }}>{item.label}</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600, color: '#333' }}>{item.value}</Typography>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={sectionCardStyles}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <SchoolIcon sx={{ color: lagosGreen, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>School Information</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="caption" sx={{ color: '#888', fontWeight: 500 }}>Current School</Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: lagosGreen }}>
                    {school_history.current_school || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888', fontWeight: 500 }}>School Code</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>{school_history.current_school_code || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888', fontWeight: 500 }}>Department</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>{school_history.department || 'N/A'}</Typography>
                </Grid>
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <GroupsIcon sx={{ color: '#666', fontSize: 20 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Personal Details</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888' }}>Gender</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{personal_info.gender}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888' }}>Marital Status</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{personal_info.marital_status}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888' }}>State of Origin</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{personal_info.state_of_origin}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: '#888' }}>LGA of Origin</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{personal_info.lga_of_origin}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ===== PERFORMANCE + LEAVE + CHARTS ===== */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Performance Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ ...sectionCardStyles, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <StarIcon sx={{ color: lagosGold, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Performance</Typography>
              </Box>
              {performance ? (
                <>
                  <Box sx={{ textAlign: 'center', mb: 2 }}>
                    <Chip
                      label={performance.rating}
                      sx={{
                        bgcolor: `${getRatingColor(performance.rating)}20`,
                        color: getRatingColor(performance.rating),
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        px: 2,
                        py: 1,
                      }}
                    />
                    <Typography variant="h3" sx={{ fontWeight: 800, color: lagosGreen, mt: 1 }}>
                      {performance.average_score}%
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#888' }}>Average Score</Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888' }}>
                    {performance.academic_year} — {performance.term}
                  </Typography>
                  {performance.comments && (
                    <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', color: '#555' }}>
                      "{performance.comments}"
                    </Typography>
                  )}
                </>
              ) : (
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                  No performance data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Leave Summary Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ ...sectionCardStyles, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CalendarIcon sx={{ color: lagosRed, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Leave Summary</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosGreen}10`, borderRadius: 2 }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, color: lagosGreen }}>
                      {leave_summary.approved_leaves}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Approved</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosGold}15`, borderRadius: 2 }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, color: lagosGold }}>
                      {leave_summary.pending_leaves}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Pending</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: `${lagosRed}10`, borderRadius: 2 }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, color: lagosRed }}>
                      {leave_summary.total_leaves_taken}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Total Taken</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ ...sectionCardStyles, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MoneyIcon sx={{ color: lagosGreen, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Financial Details</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SalaryIcon sx={{ fontSize: 18, color: '#888' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: '#888' }}>Salary</Typography>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        ₦{financial.salary.toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CardIcon sx={{ fontSize: 18, color: '#888' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: '#888' }}>Pension PIN</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{financial.pension_pin || 'N/A'}</Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BankIcon sx={{ fontSize: 18, color: '#888' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: '#888' }}>Bank</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{financial.bank_name || 'N/A'}</Typography>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>{financial.bank_account_number}</Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ===== CHARTS SECTION ===== */}
      <Grid container spacing={3}>
        {/* Performance Radar Chart */}
        {radarData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card sx={sectionCardStyles}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <TrendIcon sx={{ color: lagosGreen, fontSize: 24 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>Performance Radar</Typography>
                </Box>
                <ResponsiveContainer width="100%" height={320}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#e0e0e0" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#555', fontSize: 13 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 11 }} />
                    <Radar
                      name="Score"
                      dataKey="A"
                      stroke={lagosGreen}
                      fill={lagosGreen}
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Service Years Radial Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={sectionCardStyles}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TimelineIcon sx={{ color: lagosGold, fontSize: 24 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Service & Age Progress</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={320}>
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="30%"
                  outerRadius="90%"
                  barSize={20}
                  data={radialData}
                >
                  <RadialBar
                    minAngle={15}
                    background={{ fill: '#f0f0f0' }}
                    clockWise
                    dataKey="value"
                  />
                  <Legend
                    iconSize={12}
                    layout="horizontal"
                    verticalAlign="bottom"
                    wrapperStyle={{ fontSize: 13, paddingTop: 10 }}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mt: 1 }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: lagosGreen }}>
                    {service_timeline.years_of_service}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#888' }}>Years Served</Typography>
                </Box>
                <Divider orientation="vertical" flexItem />
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: lagosRed }}>
                    {service_timeline.years_remaining}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#888' }}>Years Remaining</Typography>
                </Box>
                <Divider orientation="vertical" flexItem />
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: lagosGold }}>
                    {personal_info.current_age}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#888' }}>Current Age</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default StaffEnterpriseDashboard
