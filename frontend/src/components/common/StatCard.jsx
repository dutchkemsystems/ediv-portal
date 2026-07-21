import React from 'react'
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material'

function StatCard({ title, value, icon, color = '#1a237e', subtitle, trend, trendValue }) {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: color,
                mb: 0.5,
              }}
            >
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" display="block">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography
                  variant="caption"
                  sx={{
                    color: trend === 'up' ? '#388e3c' : trend === 'down' ? '#d32f2f' : 'text.secondary',
                    fontWeight: 'bold',
                  }}
                >
                  {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
                </Typography>
              </Box>
            )}
          </Box>
          {icon && (
            <Avatar
              sx={{
                bgcolor: color,
                opacity: 0.1,
                width: 56,
                height: 56,
              }}
            >
              <Box sx={{ color: color, opacity: 1 }}>{icon}</Box>
            </Avatar>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}

export default StatCard
