import React, { useState, useEffect, useCallback } from 'react'
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native'
import { Text, Surface, ActivityIndicator } from 'react-native-paper'
import { MaterialIcons } from '@expo/vector-icons'
import { useAuth } from '../services/AuthContext'
import api from '../services/api'

export default function DashboardScreen() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ files: 0, pending: 0, documents: 0 })
  const [refreshing, setRefreshing] = useState(false)
  const [loading, setLoading] = useState(true)

  const fetchStats = useCallback(async () => {
    try {
      const [filesRes, docsRes] = await Promise.all([
        api.get('/files/files/'),
        api.get('/registry/documents/'),
      ])
      const files = filesRes.data.results || filesRes.data
      const docs = docsRes.data.results || docsRes.data
      setStats({
        files: Array.isArray(files) ? files.length : 0,
        pending: Array.isArray(files) ? files.filter((f) => f.status === 'PENDING' || f.status === 'IN_TRANSIT').length : 0,
        documents: Array.isArray(docs) ? docs.length : 0,
      })
    } catch {
      /* silent */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchStats() }, [fetchStats])

  const onRefresh = async () => {
    setRefreshing(true)
    await fetchStats()
    setRefreshing(false)
  }

  if (loading) return <ActivityIndicator size="large" style={styles.loader} />

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Surface style={styles.welcomeCard}>
        <Text variant="headlineSmall" style={styles.welcome}>Welcome, {user?.first_name || 'User'}</Text>
        <Text variant="bodyMedium" style={styles.role}>{user?.role || 'Staff'}</Text>
      </Surface>

      <View style={styles.statsRow}>
        <Surface style={[styles.statCard, { borderLeftColor: '#1976d2' }]}>
          <MaterialIcons name="folder" size={32} color="#1976d2" />
          <Text style={styles.statValue}>{stats.files}</Text>
          <Text style={styles.statLabel}>Total Files</Text>
        </Surface>
        <Surface style={[styles.statCard, { borderLeftColor: '#ed6c02' }]}>
          <MaterialIcons name="pending" size={32} color="#ed6c02" />
          <Text style={styles.statValue}>{stats.pending}</Text>
          <Text style={styles.statLabel}>Pending</Text>
        </Surface>
      </View>

      <View style={styles.statsRow}>
        <Surface style={[styles.statCard, { borderLeftColor: '#2e7d32' }]}>
          <MaterialIcons name="description" size={32} color="#2e7d32" />
          <Text style={styles.statValue}>{stats.documents}</Text>
          <Text style={styles.statLabel}>Documents</Text>
        </Surface>
        <Surface style={[styles.statCard, { borderLeftColor: '#d32f2f' }]}>
          <MaterialIcons name="notifications" size={32} color="#d32f2f" />
          <Text style={styles.statValue}>0</Text>
          <Text style={styles.statLabel}>Notifications</Text>
        </Surface>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 16 },
  loader: { flex: 1, justifyContent: 'center' },
  welcomeCard: { borderRadius: 12, padding: 20, marginBottom: 16, backgroundColor: '#1976d2' },
  welcome: { color: '#fff', fontWeight: 'bold' },
  role: { color: '#bbdefb', marginTop: 4 },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 12 },
  statCard: { flex: 1, borderRadius: 12, padding: 16, alignItems: 'center', borderLeftWidth: 4 },
  statValue: { fontSize: 24, fontWeight: 'bold', marginTop: 8 },
  statLabel: { fontSize: 12, color: '#757575', marginTop: 4 },
})
