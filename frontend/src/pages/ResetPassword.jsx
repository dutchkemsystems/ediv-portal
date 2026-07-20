import React, { useState } from 'react'
import { useSearchParams, Link as RouterLink, useNavigate } from 'react-router-dom'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Visibility, VisibilityOff, CheckCircle as SuccessIcon } from '@mui/icons-material'
import api from '../api/client'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  if (!token) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Paper elevation={3} sx={{ p: 4, width: '100%', textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom sx={{ color: '#d32f2f' }}>
              Invalid Reset Link
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              This password reset link is invalid or missing a token.
            </Typography>
            <Button variant="contained" component={RouterLink} to="/forgot-password" sx={{ mt: 2, bgcolor: '#1a237e' }}>
              Request New Reset Link
            </Button>
          </Paper>
        </Box>
      </Container>
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (newPassword.length < 12) {
      setError('Password must be at least 12 characters long.')
      return
    }

    setLoading(true)
    try {
      await api.post('/users/auth/reset_password/', {
        token,
        new_password: newPassword,
        new_password_confirm: confirmPassword,
      })
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.new_password?.[0] || 'Something went wrong. The link may have expired.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom sx={{ color: '#1a237e' }}>
            Reset Password
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" gutterBottom>
            Enter your new password below.
          </Typography>

          {success ? (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <SuccessIcon sx={{ fontSize: 64, color: '#388e3c', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Password Reset Successful
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Your password has been updated. You can now log in with your new password.
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/login')}
                sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
              >
                Go to Login
              </Button>
            </Box>
          ) : (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}

              <Alert severity="info" sx={{ mb: 2 }}>
                Password must be at least 12 characters with uppercase, lowercase, digit, and special character.
              </Alert>

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="New Password"
                  type={showPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  margin="normal"
                  required
                  autoFocus
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  margin="normal"
                  required
                />
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 3, bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Reset Password'}
                </Button>
              </form>

              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Link component={RouterLink} to="/login" variant="body2">
                  Back to Login
                </Link>
              </Box>
            </>
          )}
        </Paper>
      </Box>
    </Container>
  )
}

export default ResetPassword
