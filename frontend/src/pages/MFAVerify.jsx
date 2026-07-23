import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material'
import { VerifiedUser as MFAIcon } from '@mui/icons-material'
import api from '../api/client'
import { notify } from '../utils/notifications'

function MFAVerify() {
  const [mfaCode, setMfaCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const tempToken = localStorage.getItem('temp_token')
  const pendingUser = JSON.parse(localStorage.getItem('pending_user') || '{}')

  if (!tempToken) {
    navigate('/login')
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await api.post('/users/auth/mfa_verify/', {
        temp_token: tempToken,
        mfa_code: mfaCode,
      })

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      localStorage.removeItem('temp_token')
      localStorage.removeItem('pending_user')

      notify.success('MFA verification successful')
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid MFA code')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #C8102E 0%, #8B0000 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={8} sx={{ p: 4, borderRadius: 3 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <MFAIcon sx={{ fontSize: 60, color: '#C8102E', mb: 1 }} />
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Two-Factor Authentication
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Enter the 6-digit code from your authenticator app
            </Typography>
          </Box>

          {pendingUser.email && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Logging in as: {pendingUser.email}
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="MFA Code"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              margin="normal"
              required
              autoFocus
              inputProps={{
                maxLength: 6,
                style: { textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5em' },
              }}
              placeholder="000000"
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || mfaCode.length !== 6}
              sx={{
                mt: 3,
                py: 1.5,
                bgcolor: '#C8102E',
                fontWeight: 600,
                '&:hover': { bgcolor: '#8B0000' },
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Verify'}
            </Button>
          </form>

          <Button
            fullWidth
            variant="text"
            onClick={() => {
              localStorage.removeItem('temp_token')
              localStorage.removeItem('pending_user')
              navigate('/login')
            }}
            sx={{ mt: 2 }}
          >
            Back to Login
          </Button>
        </Paper>
      </Container>
    </Box>
  )
}

export default MFAVerify
