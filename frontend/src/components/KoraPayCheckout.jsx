import React, { useState, useEffect, useRef } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material'
import { CheckCircle as SuccessIcon, Error as ErrorIcon } from '@mui/icons-material'
import api from '../api/client'

const KORAPAY_SCRIPT_URL = 'https://korablobstorage.blob.core.windows.net/modal-bucket/korapay-collections.min.js'

function KoraPayCheckout({ open, onClose, onSuccess, studentFeeId, amount, studentName, studentEmail, feeName }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('idle') // idle, loading, success, failed
  const scriptLoaded = useRef(false)

  useEffect(() => {
    if (open && !scriptLoaded.current) {
      const script = document.createElement('script')
      script.src = KORAPAY_SCRIPT_URL
      script.async = true
      script.onload = () => { scriptLoaded.current = true }
      document.head.appendChild(script)
    }
  }, [open])

  const handlePay = async () => {
    setLoading(true)
    setError('')
    setStatus('loading')

    try {
      // Initialize payment on backend
      const response = await api.post('/finance/payments/initialize/', {
        student_fee_id: studentFeeId,
        amount: amount,
      })

      const { public_key, reference, amount: amountKobo, currency, customer_name, customer_email } = response.data

      // Open KoraPay checkout
      if (window.Korapay) {
        window.Korapay.initialize({
          key: public_key,
          reference: reference,
          amount: amountKobo,
          currency: currency,
          customer: {
            name: customer_name,
            email: customer_email,
          },
          channels: ['card', 'bank_transfer', 'bank', 'ussd'],
          onSuccess: async (data) => {
            setStatus('success')
            setLoading(false)
            // Verify payment
            try {
              await api.get(`/finance/payments/verify/${reference}/`)
            } catch (e) {
              console.error('Verification error:', e)
            }
            if (onSuccess) onSuccess(data)
          },
          onFailed: (data) => {
            setStatus('failed')
            setLoading(false)
            setError('Payment failed. Please try again.')
            if (onFailed) onFailed(data)
          },
          onClose: () => {
            setLoading(false)
            setStatus('idle')
          },
        })
      } else {
        throw new Error('Payment gateway not loaded. Please refresh and try again.')
      }
    } catch (err) {
      setLoading(false)
      setStatus('failed')
      setError(err.response?.data?.error || err.message || 'Failed to initialize payment')
    }
  }

  const handleClose = () => {
    setStatus('idle')
    setError('')
    setLoading(false)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ bgcolor: '#1a237e', color: 'white' }}>
        Pay School Fees
      </DialogTitle>
      <DialogContent sx={{ pt: 3 }}>
        {status === 'success' ? (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <SuccessIcon sx={{ fontSize: 64, color: '#388e3c', mb: 2 }} />
            <Typography variant="h5" gutterBottom color="primary">
              Payment Successful!
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              Your payment of <strong>₦{Number(amount).toLocaleString()}</strong> has been confirmed.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {feeName && `For: ${feeName}`}
            </Typography>
          </Box>
        ) : status === 'failed' ? (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <ErrorIcon sx={{ fontSize: 64, color: '#d32f2f', mb: 2 }} />
            <Typography variant="h5" gutterBottom color="error">
              Payment Failed
            </Typography>
            <Typography color="text.secondary">
              {error || 'Something went wrong. Please try again.'}
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="body1" gutterBottom>
              You are about to make a payment for:
            </Typography>

            <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1, mb: 2 }}>
              {feeName && (
                <Typography variant="subtitle2" gutterBottom>
                  Fee: {feeName}
                </Typography>
              )}
              <Typography variant="subtitle2" gutterBottom>
                Student: {studentName}
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                Email: {studentEmail}
              </Typography>
              <Typography variant="h5" sx={{ mt: 1, color: '#1a237e', fontWeight: 'bold' }}>
                ₦{Number(amount).toLocaleString()}
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              Payment methods accepted: Card, Bank Transfer, USSD
            </Typography>

            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip label="Secure" size="small" color="success" variant="outlined" />
              <Chip label="Instant" size="small" color="primary" variant="outlined" />
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')}>
                {error}
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        {status === 'success' ? (
          <Button onClick={handleClose} variant="contained" sx={{ bgcolor: '#1a237e' }}>
            Done
          </Button>
        ) : status === 'failed' ? (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handlePay} variant="contained" disabled={loading} sx={{ bgcolor: '#1a237e' }}>
              Try Again
            </Button>
          </>
        ) : (
          <>
            <Button onClick={handleClose} disabled={loading}>Cancel</Button>
            <Button
              onClick={handlePay}
              variant="contained"
              disabled={loading}
              sx={{ bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
            >
              {loading ? <CircularProgress size={24} /> : `Pay ₦${Number(amount).toLocaleString()}`}
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  )
}

export default KoraPayCheckout
