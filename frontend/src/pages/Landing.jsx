import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Divider,
} from '@mui/material'
import {
  School as SchoolIcon,
  People as PeopleIcon,
  Person as PersonIcon,
  AccountBalance as FinanceIcon,
  Assessment as ReportsIcon,
  Security as SecurityIcon,
  ArrowForward as ArrowIcon,
  Visibility as VisionIcon,
  EmojiObjects as MissionIcon,
  DirectionsBus as TrafficIcon,
  LocalHospital as HealthIcon,
  MenuBook as EducationIcon,
  AccountBalance as EconomyIcon,
  Celebration as EntertainmentIcon,
  Shield as SecurityPolicyIcon,
  PlusOne as PlusIcon,
} from '@mui/icons-material'

const lagosRed = '#C8102E'
const lagosGreen = '#00843D'
const lagosGold = '#D4A017'

const themes = [
  { letter: 'T', title: 'Traffic Management & Transportation', icon: <TrafficIcon />, color: '#1565C0', desc: 'Efficient traffic management and modern transportation systems for Lagos' },
  { letter: 'H', title: 'Health & Environment', icon: <HealthIcon />, color: '#2E7D32', desc: 'Quality healthcare delivery and sustainable environmental practices' },
  { letter: 'E', title: 'Education & Technology', icon: <EducationIcon />, color: '#C8102E', desc: 'Excellence in education through technology-driven learning and innovation' },
  { letter: 'M', title: 'Making Lagos a 21st Century Economy', icon: <EconomyIcon />, color: '#6A1B9A', desc: 'Transforming Lagos into a globally competitive 21st century economy' },
  { letter: 'S', title: 'Entertainment & Tourism', icon: <EntertainmentIcon />, color: '#E65100', desc: 'Promoting Lagos as Africa\'s entertainment and tourism hub' },
  { letter: '+', title: 'Security & Governance', icon: <SecurityPolicyIcon />, color: '#37474F', desc: 'Enhanced security architecture and responsive governance' },
]

const features = [
  { icon: <SchoolIcon sx={{ fontSize: 48 }} />, title: 'School Management', desc: 'Manage 95 schools across Apapa, Mainland, and Surulere LGAs' },
  { icon: <PeopleIcon sx={{ fontSize: 48 }} />, title: 'Staff Administration', desc: 'Complete HR management with payroll, leave, and performance tracking' },
  { icon: <PersonIcon sx={{ fontSize: 48 }} />, title: 'Student Records', desc: 'Student profiles, attendance, academics, and parent communication' },
  { icon: <FinanceIcon sx={{ fontSize: 48 }} />, title: 'Financial Management', desc: 'Fee collection, budgets, grants, payments with KoraPay integration' },
  { icon: <ReportsIcon sx={{ fontSize: 48 }} />, title: 'Analytics & Reports', desc: 'Real-time dashboards, KPIs, and comprehensive reporting' },
  { icon: <SecurityIcon sx={{ fontSize: 48 }} />, title: 'Role-Based Access', desc: '23 user roles with granular privileges and MFA support' },
]

const stats = [
  { value: '95', label: 'Schools' },
  { value: '3', label: 'LGAs' },
  { value: '23', label: 'User Roles' },
  { value: '29', label: 'Modules' },
]

function Landing() {
  const navigate = useNavigate()

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8F9FA' }}>
      {/* Header */}
      <AppBar position="static" sx={{ bgcolor: lagosRed, boxShadow: 'none' }}>
        <Toolbar>
          <SchoolIcon sx={{ mr: 1.5 }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Education District IV Portal
          </Typography>
          <Button
            color="inherit"
            onClick={() => navigate('/login')}
            sx={{ fontWeight: 600, borderColor: 'rgba(255,255,255,0.5)', border: '1px solid' }}
          >
            Sign In
          </Button>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${lagosRed} 0%, #8B0000 100%)`,
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 60,
            bgcolor: '#F8F9FA',
            clipPath: 'polygon(0 100%, 100% 100%, 100% 0, 0 100%)',
          },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={7}>
              <Typography variant="body2" sx={{ mb: 1, opacity: 0.8, textTransform: 'uppercase', letterSpacing: 2, fontWeight: 600 }}>
                Lagos State Ministry of Education
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 2, lineHeight: 1.2 }}>
                Education District IV
                <br />
                <Box component="span" sx={{ color: '#FFD700' }}>Digital Portal</Box>
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9, fontWeight: 400, lineHeight: 1.6 }}>
                A comprehensive digital platform for managing schools, staff, students,
                and administrative operations across Education District IV in Lagos State.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/login')}
                  sx={{
                    bgcolor: 'white',
                    color: lagosRed,
                    fontWeight: 700,
                    px: 4,
                    '&:hover': { bgcolor: '#f5f5f5', transform: 'translateY(-2px)' },
                    transition: 'all 0.2s',
                  }}
                  endIcon={<ArrowIcon />}
                >
                  Access Portal
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => document.getElementById('themes-section')?.scrollIntoView({ behavior: 'smooth' })}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    px: 4,
                    '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
                  }}
                >
                  Our Agenda
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={5}>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Box
                  sx={{
                    width: 220,
                    height: 220,
                    borderRadius: '50%',
                    bgcolor: 'rgba(255,255,255,0.15)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '3px solid rgba(255,255,255,0.3)',
                  }}
                >
                  <SchoolIcon sx={{ fontSize: 80, opacity: 0.9, mb: 1 }} />
                  <Typography variant="caption" sx={{ opacity: 0.8, textTransform: 'uppercase', letterSpacing: 2 }}>
                    Est. Lagos State
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ mt: -3, position: 'relative', zIndex: 1 }}>
        <Grid container spacing={3}>
          {stats.map((stat) => (
            <Grid item xs={6} md={3} key={stat.label}>
              <Card sx={{ textAlign: 'center', py: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
                <CardContent>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: lagosRed }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Vision & Mission Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', borderLeft: `4px solid ${lagosRed}`, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <VisionIcon sx={{ color: lagosRed, fontSize: 32 }} />
                  <Typography variant="h5" sx={{ fontWeight: 700, color: lagosRed }}>
                    Our Vision
                  </Typography>
                </Box>
                <Typography variant="body1" sx={{ lineHeight: 1.8, color: '#444' }}>
                  To be the leading education district in Lagos State, providing quality,
                  inclusive, and technology-driven education that empowers every student
                  to reach their full potential and contribute meaningfully to the development
                  of Lagos State and Nigeria at large.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%', borderLeft: `4px solid ${lagosGreen}`, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <MissionIcon sx={{ color: lagosGreen, fontSize: 32 }} />
                  <Typography variant="h5" sx={{ fontWeight: 700, color: lagosGreen }}>
                    Our Mission
                  </Typography>
                </Box>
                <Typography variant="body1" sx={{ lineHeight: 1.8, color: '#444' }}>
                  To deliver exceptional educational services through effective management
                  of schools, dedicated staff, and innovative programs. We are committed
                  to maintaining high academic standards, fostering discipline, promoting
                  ICT integration, and ensuring the holistic development of every student
                  under our care.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* T.H.E.M.E.S. Plus Section */}
      <Box id="themes-section" sx={{ bgcolor: '#1a1a2e', py: 8, color: 'white' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography variant="overline" sx={{ color: lagosGold, letterSpacing: 3, fontWeight: 600 }}>
              Aligned with the Administration of
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700, mt: 1, mb: 1 }}>
              Mr. Babajide Olusola Sanwo-Olu
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.7, fontWeight: 400 }}>
              Governor of Lagos State
            </Typography>
            <Divider sx={{ bgcolor: lagosGold, width: 80, height: 3, mx: 'auto', mt: 3 }} />
          </Box>

          <Typography variant="h5" align="center" sx={{ fontWeight: 600, mb: 1 }}>
            T.H.E.M.E.S. Plus Agenda
          </Typography>
          <Typography variant="body1" align="center" sx={{ opacity: 0.7, mb: 5, maxWidth: 600, mx: 'auto' }}>
            The strategic development agenda driving transformation across Lagos State,
            with Education as a core pillar
          </Typography>

          <Grid container spacing={3}>
            {themes.map((theme) => (
              <Grid item xs={12} sm={6} md={4} key={theme.letter}>
                <Card
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    height: '100%',
                    transition: 'all 0.3s',
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                      transform: 'translateY(-4px)',
                      border: `1px solid ${theme.color}`,
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Box
                        sx={{
                          width: 48,
                          height: 48,
                          borderRadius: '12px',
                          bgcolor: theme.color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: '1.5rem',
                        }}
                      >
                        {theme.letter}
                      </Box>
                      <Box sx={{ color: theme.color }}>
                        {theme.icon}
                      </Box>
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, fontSize: '0.95rem' }}>
                      {theme.title}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.7, lineHeight: 1.6 }}>
                      {theme.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ mt: 6, p: 3, bgcolor: 'rgba(200, 16, 46, 0.15)', borderRadius: 2, border: '1px solid rgba(200, 16, 46, 0.3)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: lagosGold }}>
              Education & Technology (E) - Our Core Focus
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.85, lineHeight: 1.7 }}>
              As Education District IV, we are at the forefront of implementing Governor Sanwo-Olu's
              vision for education in Lagos State. This portal represents our commitment to leveraging
              technology for efficient school management, data-driven decision-making, and improved
              learning outcomes across all 95 schools in Apapa, Mainland, and Surulere Local Government
              Areas.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" align="center" sx={{ fontWeight: 700, mb: 1, color: '#333' }}>
          Platform Features
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 6, maxWidth: 600, mx: 'auto' }}>
          Everything you need to manage Education District IV efficiently
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature) => (
            <Grid item xs={12} sm={6} md={4} key={feature.title}>
              <Card
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  py: 3,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 8px 30px rgba(0,0,0,0.12)' },
                }}
              >
                <CardContent>
                  <Box sx={{ color: lagosRed, mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>{feature.title}</Typography>
                  <Typography variant="body2" color="text.secondary">{feature.desc}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Footer */}
      <Box sx={{ bgcolor: '#1a1a1a', color: 'white', py: 4 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Education District IV
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                Lagos State Ministry of Education
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'left', md: 'center' } }}>
              <Typography variant="body2" sx={{ opacity: 0.7, mb: 0.5 }}>
                Aligned with the T.H.E.M.E.S. Plus Agenda
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.5, fontSize: '0.8rem' }}>
                His Excellency, Mr. Babajide Olusola Sanwo-Olu
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign: { md: 'right' } }}>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                &copy; {new Date().getFullYear()} Lagos State Government. All rights reserved.
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  )
}

export default Landing
