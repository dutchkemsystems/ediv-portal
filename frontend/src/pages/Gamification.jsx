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
  Avatar,
} from '@mui/material'
import {
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  Refresh as RefreshIcon,
  WorkspacePremium as BadgeIcon,
} from '@mui/icons-material'
import api from '../api/client'
import StatCard from '../components/common/StatCard'

const lagosRed = '#C8102E'

const tierColors = {
  Bronze: '#CD7F32',
  Silver: '#C0C0C0',
  Gold: '#FFD700',
  Platinum: '#E5E4E2',
  Diamond: '#B9F2FF',
}

const tierIcons = {
  Bronze: '🥉',
  Silver: '🥈',
  Gold: '🥇',
  Platinum: '💎',
  Diamond: '💠',
}

function Gamification() {
  const [activeTab, setActiveTab] = useState(0)
  const [leaderboard, setLeaderboard] = useState([])
  const [badges, setBadges] = useState([])
  const [pointsHistory, setPointsHistory] = useState([])
  const [stats, setStats] = useState({
    total_points: 0,
    current_level: 0,
    badges_earned: 0,
    rank: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAllData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [leaderboardRes, badgesRes, pointsRes, statsRes] = await Promise.all([
        api.get('/gamification/points/leaderboard/'),
        api.get('/gamification/user-badges/'),
        api.get('/gamification/transactions/'),
        api.get('/gamification/points/my-stats/'),
      ])
      setLeaderboard(leaderboardRes.data.results || leaderboardRes.data)
      setBadges(badgesRes.data.results || badgesRes.data)
      setPointsHistory(pointsRes.data.results || pointsRes.data)
      setStats(statsRes.data)
    } catch (err) {
      console.error('Error fetching gamification data:', err)
      setError('Failed to load gamification data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAllData()
  }, [fetchAllData])

  const handleTabChange = (_, newValue) => {
    setActiveTab(newValue)
  }

  const getRankBadge = (rank) => {
    if (rank === 1) return { bgcolor: '#FFD700', color: '#000' }
    if (rank === 2) return { bgcolor: '#C0C0C0', color: '#000' }
    if (rank === 3) return { bgcolor: '#CD7F32', color: '#fff' }
    return { bgcolor: 'grey.300', color: 'text.primary' }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  const renderLeaderboard = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: lagosRed }}>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Rank</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>User</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }} align="right">Points</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }} align="right">Level</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }} align="right">Badges</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {leaderboard.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} align="center">
                <Typography color="text.secondary" sx={{ py: 3 }}>
                  No leaderboard data available.
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            leaderboard.map((entry, index) => {
              const rank = entry.rank || index + 1
              const rankStyle = getRankBadge(rank)
              return (
                <TableRow
                  key={entry.id || index}
                  hover
                  sx={{
                    '&:last-child td': { border: 0 },
                    bgcolor: rank <= 3 ? `${rankStyle.bgcolor}10` : 'inherit',
                  }}
                >
                  <TableCell>
                    <Avatar
                      sx={{
                        bgcolor: rankStyle.bgcolor,
                        color: rankStyle.color,
                        width: 36,
                        height: 36,
                        fontWeight: 'bold',
                        fontSize: '0.875rem',
                      }}
                    >
                      {rank}
                    </Avatar>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {entry.user_name || entry.username || entry.user || 'Unknown'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      icon={<StarIcon sx={{ fontSize: 16 }} />}
                      label={entry.points || entry.total_points || 0}
                      size="small"
                      sx={{
                        bgcolor: lagosRed,
                        color: '#fff',
                        '& .MuiChip-icon': { color: '#fff' },
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`Lv. ${entry.level || entry.current_level || 1}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontWeight: 'bold' }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      icon={<BadgeIcon sx={{ fontSize: 16 }} />}
                      label={entry.badges_count || entry.badges || 0}
                      size="small"
                      color="primary"
                    />
                  </TableCell>
                </TableRow>
              )
            })
          )}
        </TableBody>
      </Table>
    </TableContainer>
  )

  const renderBadges = () => (
    <Grid container spacing={3}>
      {badges.length === 0 ? (
        <Grid item xs={12}>
          <Alert severity="info">No badges earned yet. Keep participating to earn badges!</Alert>
        </Grid>
      ) : (
        badges.map((badge, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={badge.id || index}>
            <Card
              sx={{
                height: '100%',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 16px rgba(0,0,0,0.15)',
                },
                borderTop: `4px solid ${tierColors[badge.tier] || tierColors.Bronze}`,
              }}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar
                  sx={{
                    width: 64,
                    height: 64,
                    mx: 'auto',
                    mb: 2,
                    bgcolor: `${tierColors[badge.tier] || tierColors.Bronze}30`,
                    fontSize: '2rem',
                  }}
                >
                  {tierIcons[badge.tier] || '🏅'}
                </Avatar>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  {badge.name || badge.badge_name || 'Badge'}
                </Typography>
                <Chip
                  label={badge.tier || 'Bronze'}
                  size="small"
                  sx={{
                    bgcolor: tierColors[badge.tier] || tierColors.Bronze,
                    color: badge.tier === 'Gold' || badge.tier === 'Platinum' || badge.tier === 'Diamond' ? '#000' : '#fff',
                    fontWeight: 'bold',
                    mb: 1,
                  }}
                />
                {badge.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 1 }}>
                    {badge.description}
                  </Typography>
                )}
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                  Earned: {formatDate(badge.earned_date || badge.date_earned || badge.created_at)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))
      )}
    </Grid>
  )

  const renderPointsHistory = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: lagosRed }}>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }}>Action</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }} align="right">Points</TableCell>
            <TableCell sx={{ color: '#fff', fontWeight: 'bold' }} align="right">Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pointsHistory.length === 0 ? (
            <TableRow>
              <TableCell colSpan={3} align="center">
                <Typography color="text.secondary" sx={{ py: 3 }}>
                  No points history available.
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            pointsHistory.map((transaction, index) => (
              <TableRow key={transaction.id || index} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {transaction.action || transaction.description || 'Unknown Action'}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Chip
                    label={`+${transaction.points || 0}`}
                    size="small"
                    sx={{
                      bgcolor: transaction.points > 0 ? '#388e3c' : '#d32f2f',
                      color: '#fff',
                      fontWeight: 'bold',
                    }}
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(transaction.date || transaction.created_at)}
                  </Typography>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  )

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Gamification & Leaderboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchAllData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Points"
            value={stats.total_points || 0}
            icon={<StarIcon />}
            color={lagosRed}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Current Level"
            value={stats.current_level || 1}
            icon={<TrophyIcon />}
            color="#1a237e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Badges Earned"
            value={stats.badges_earned || 0}
            icon={<BadgeIcon />}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Rank"
            value={`#${stats.rank || '—'}`}
            icon={<TrophyIcon />}
            color="#f57c00"
          />
        </Grid>
      </Grid>

      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': { fontWeight: 'bold' },
            '& .MuiTabs-indicator': { bgcolor: lagosRed },
          }}
        >
          <Tab label="Leaderboard" />
          <Tab label="My Badges" />
          <Tab label="Points History" />
        </Tabs>
      </Paper>

      <Box>
        {activeTab === 0 && renderLeaderboard()}
        {activeTab === 1 && renderBadges()}
        {activeTab === 2 && renderPointsHistory()}
      </Box>
    </Box>
  )
}

export default Gamification
