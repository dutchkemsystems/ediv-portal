import React from 'react'
import { Box, CircularProgress, Typography } from '@mui/material'

function Loading({ message = 'Loading...', fullScreen = false }) {
  if (fullScreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: 'rgba(255,255,255,0.9)',
          zIndex: 9999,
        }}
      >
        <CircularProgress size={60} sx={{ color: '#1a237e' }} />
        <Typography variant="h6" sx={{ mt: 3, color: '#1a237e' }}>
          {message}
        </Typography>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        py: 8,
      }}
    >
      <CircularProgress size={40} sx={{ color: '#1a237e' }} />
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        {message}
      </Typography>
    </Box>
  )
}

export default Loading
