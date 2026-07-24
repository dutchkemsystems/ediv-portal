import React, { useState, useEffect, useCallback } from 'react'
import { View, FlatList, StyleSheet } from 'react-native'
import { Text, ActivityIndicator } from 'react-native-paper'
import { MaterialIcons } from '@expo/vector-icons'
import api from '../services/api'
import EmptyState from '../components/EmptyState'

export default function NotificationsScreen() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await api.get('/notifications/notifications/')
      setNotifications(res.data.results || res.data)
    } catch {
      /* silent */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchNotifications() }, [fetchNotifications])

  const renderItem = ({ item }) => (
    <View style={[styles.card, !item.is_read && styles.unread]}>
      <MaterialIcons name={item.is_read ? 'notifications-none' : 'notifications-active'}
        size={24} color={item.is_read ? '#9e9e9e' : '#1976d2'} />
      <View style={styles.content}>
        <Text style={styles.title}>{item.title || 'Notification'}</Text>
        <Text style={styles.message}>{item.message || ''}</Text>
        <Text style={styles.date}>{new Date(item.created_at).toLocaleDateString()}</Text>
      </View>
    </View>
  )

  if (loading) return <ActivityIndicator size="large" style={styles.loader} />

  return (
    <View style={styles.container}>
      <FlatList data={notifications} keyExtractor={(item) => String(item.id)} renderItem={renderItem}
        contentContainerStyle={notifications.length === 0 && styles.empty}
        ListEmptyComponent={<EmptyState icon="notifications-off" message="No notifications" />} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loader: { flex: 1, justifyContent: 'center' },
  card: { flexDirection: 'row', backgroundColor: '#fff', marginHorizontal: 12, marginBottom: 6, borderRadius: 8, padding: 14, elevation: 1, alignItems: 'flex-start' },
  unread: { borderLeftWidth: 3, borderLeftColor: '#1976d2' },
  content: { marginLeft: 12, flex: 1 },
  title: { fontSize: 14, fontWeight: '600' },
  message: { fontSize: 13, color: '#616161', marginTop: 2 },
  date: { fontSize: 11, color: '#9e9e9e', marginTop: 4 },
  empty: { flex: 1 },
})
