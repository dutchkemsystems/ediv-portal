import React, { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
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
} from '@mui/material'
import { ArrowBack as BackIcon } from '@mui/icons-material'
import api from '../api/client'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/users/auth/forgot_password/', { email })
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom sx={{ color: '#1a237e' }}>
            Forgot Password
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" gutterBottom>
            Enter your email address and we'll send you a link to reset your password.
          </Typography>

          {success ? (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Alert severity="success" sx={{ mb: 3 }}>
                If an account exists with <strong>{email}</strong>, a password reset link has been sent.
                Please check your inbox and follow the instructions.
              </Alert>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Didn't receive the email? Check your spam folder or try again.
              </Typography>
              <Button
                variant="outlined"
                component={RouterLink}
                to="/login"
                startIcon={<BackIcon />}
                sx={{ mt: 1 }}
              >
                Back to Login
              </Button>
            </Box>
          ) : (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  margin="normal"
                  required
                  autoFocus
                  placeholder="e.g. user@ediv.gov.ng"
                />
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 3, bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Send Reset Link'}
                </Button>
              </form>

              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Link component={RouterLink} to="/login" variant="body2" sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
                  <BackIcon fontSize="small" />
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

export default ForgotPassword
