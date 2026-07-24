import React from 'react'
import { View, Text, StyleSheet } from 'react-native'

const COLORS = {
  ACTIVE: '#2e7d32', PENDING: '#ed6c02', IN_TRANSIT: '#1976d2',
  ARCHIVED: '#757575', CONFIDENTIAL: '#d32f2f', DEFAULT: '#9e9e9e',
  RECEIVED: '#0288d1', SCANNED: '#0288d1', CLASSIFIED: '#1976d2',
  ASSIGNED: '#ed6c02', UNDER_REVIEW: '#ed6c02', IN_ACTION: '#7b1fa2',
  RESPONDED: '#2e7d32', DISPATCHED: '#2e7d32', DRAFT: '#9e9e9e',
  REGISTERED: '#0288d1', UNDER_APPROVAL: '#ed6c02', CIRCULATING: '#1976d2',
  ACKNOWLEDGED: '#2e7d32', REPORTED: '#2e7d32', APPROVED: '#2e7d32',
  REJECTED: '#d32f2f',
}

export default function StatusBadge({ status }) {
  const color = COLORS[status] || COLORS.DEFAULT
  return (
    <View style={[styles.badge, { backgroundColor: color }]}>
      <Text style={styles.text}>{status}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12, alignSelf: 'flex-start' },
  text: { color: '#fff', fontSize: 11, fontWeight: '600' },
})
