import React from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'
import { Error as ErrorIcon } from '@mui/icons-material'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    // Don't catch network/API errors
    if (error?.message?.includes('Network Error') || error?.code === 'ERR_NETWORK') {
      return { hasError: false }
    }
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    if (!error?.message?.includes('Network Error')) {
      console.error('Render error:', error)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
          <Paper sx={{ p: 4, textAlign: 'center', maxWidth: 500 }}>
            <ErrorIcon sx={{ fontSize: 64, color: '#d32f2f', mb: 2 }} />
            <Typography variant="h5" gutterBottom color="error">
              Something went wrong
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              {this.state.error?.message || 'An unexpected error occurred.'}
            </Typography>
            <Button
              variant="contained"
              onClick={() => window.location.reload()}
              sx={{ mt: 2, bgcolor: '#1a237e' }}
            >
              Refresh Page
            </Button>
          </Paper>
        </Box>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
