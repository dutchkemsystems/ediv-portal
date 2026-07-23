import React, { useState, useEffect } from 'react'
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
  Step,
  StepLabel,
  Stepper,
  Chip,
} from '@mui/material'
import { VerifiedUser as MFAIcon } from '@mui/icons-material'
import api from '../api/client'
import { notify } from '../utils/notifications'

const steps = ['Setup Secret', 'Scan QR Code', 'Verify Code']

function MFASetup() {
  const [activeStep, setActiveStep] = useState(0)
  const [secret, setSecret] = useState('')
  const [qrCodeUrl, setQrCodeUrl] = useState('')
  const [provisioningUri, setProvisioningUri] = useState('')
  const [verifyCode, setVerifyCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mfaEnabled, setMfaEnabled] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    checkMFAStatus()
  }, [])

  const checkMFAStatus = async () => {
    try {
      const res = await api.get('/users/users/me/')
      setMfaEnabled(res.data.mfa_enabled)
      if (res.data.mfa_enabled) {
        setActiveStep(3)
      }
    } catch (err) {
      console.error('Failed to check MFA status')
    }
  }

  const handleSetup = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/users/auth/mfa_setup/')
      setSecret(res.data.secret)
      setQrCodeUrl(res.data.qr_code_url)
      setProvisioningUri(res.data.provisioning_uri)
      setActiveStep(1)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to setup MFA')
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    setLoading(true)
    setError('')
    try {
      await api.post('/users/auth/mfa_enable/', { code: verifyCode })
      setMfaEnabled(true)
      setActiveStep(3)
      notify.success('MFA enabled successfully!')
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid MFA code')
    } finally {
      setLoading(false)
    }
  }

  const handleDisable = async () => {
    setLoading(true)
    setError('')
    try {
      await api.post('/users/auth/mfa_disable/', { code: verifyCode })
      setMfaEnabled(false)
      setActiveStep(0)
      setSecret('')
      setQrCodeUrl('')
      setVerifyCode('')
      notify.success('MFA disabled successfully!')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to disable MFA')
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
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={8} sx={{ p: 4, borderRadius: 3 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <MFAIcon sx={{ fontSize: 60, color: '#C8102E', mb: 1 }} />
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Multi-Factor Authentication Setup
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Secure your account with an additional layer of protection
            </Typography>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {activeStep === 0 && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                MFA adds an extra layer of security. You'll need an authenticator app like Google Authenticator or Authy.
              </Alert>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSetup}
                disabled={loading}
                sx={{ bgcolor: '#C8102E', '&:hover': { bgcolor: '#8B0000' } }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Begin Setup'}
              </Button>
            </Box>
          )}

          {activeStep === 1 && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Scan this QR code with your authenticator app, or manually enter the secret key.
              </Alert>

              {qrCodeUrl && (
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <img src={qrCodeUrl} alt="MFA QR Code" style={{ maxWidth: 200, border: '2px solid #eee', borderRadius: 8 }} />
                </Box>
              )}

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">Manual Entry Key:</Typography>
                <Chip label={secret} sx={{ ml: 1, fontFamily: 'monospace' }} />
              </Box>

              <Button
                fullWidth
                variant="contained"
                onClick={() => setActiveStep(2)}
                sx={{ bgcolor: '#C8102E', '&:hover': { bgcolor: '#8B0000' } }}
              >
                I've Scanned the Code
              </Button>
            </Box>
          )}

          {activeStep === 2 && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Enter the 6-digit code from your authenticator app to verify setup.
              </Alert>

              <TextField
                fullWidth
                label="Verification Code"
                value={verifyCode}
                onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                margin="normal"
                inputProps={{
                  maxLength: 6,
                  style: { textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5em' },
                }}
                placeholder="000000"
              />

              <Button
                fullWidth
                variant="contained"
                onClick={handleVerify}
                disabled={loading || verifyCode.length !== 6}
                sx={{ mt: 2, bgcolor: '#C8102E', '&:hover': { bgcolor: '#8B0000' } }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Verify & Enable'}
              </Button>
            </Box>
          )}

          {activeStep === 3 && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                MFA is {mfaEnabled ? 'enabled' : 'disabled'} for your account.
              </Alert>

              {mfaEnabled ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    To disable MFA, enter your current MFA code:
                  </Typography>
                  <TextField
                    fullWidth
                    label="Current MFA Code"
                    value={verifyCode}
                    onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    margin="normal"
                    inputProps={{
                      maxLength: 6,
                      style: { textAlign: 'center', fontSize: '1.2rem', letterSpacing: '0.5em' },
                    }}
                  />
                  <Button
                    fullWidth
                    variant="outlined"
                    color="error"
                    onClick={handleDisable}
                    disabled={loading || verifyCode.length !== 6}
                    sx={{ mt: 2 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Disable MFA'}
                  </Button>
                </Box>
              ) : (
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => setActiveStep(0)}
                  sx={{ bgcolor: '#C8102E', '&:hover': { bgcolor: '#8B0000' } }}
                >
                  Setup MFA
                </Button>
              )}
            </Box>
          )}

          <Button
            fullWidth
            variant="text"
            onClick={() => navigate('/dashboard')}
            sx={{ mt: 2 }}
          >
            Back to Dashboard
          </Button>
        </Paper>
      </Container>
    </Box>
  )
}

export default MFASetup
