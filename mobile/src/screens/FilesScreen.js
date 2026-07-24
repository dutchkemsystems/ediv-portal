import React, { useState, useEffect, useCallback } from 'react'
import { View, FlatList, StyleSheet, TouchableOpacity } from 'react-native'
import { Text, Searchbar, ActivityIndicator, FAB } from 'react-native-paper'
import { useNavigation } from '@react-navigation/native'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'

export default function FilesScreen() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const navigation = useNavigation()

  const fetchFiles = useCallback(async () => {
    try {
      const res = await api.get('/files/files/')
      setFiles(res.data.results || res.data)
    } catch {
      /* silent */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchFiles() }, [fetchFiles])

  const filtered = files.filter((f) =>
    (f.title || '').toLowerCase().includes(search.toLowerCase()) ||
    (f.file_number || '').toLowerCase().includes(search.toLowerCase())
  )

  const PRIORITY_COLORS = { URGENT: '#d32f2f', HIGH: '#ed6c02', NORMAL: '#1976d2', LOW: '#757575' }

  const renderItem = ({ item }) => (
    <TouchableOpacity onPress={() => navigation.navigate('FileDetail', { fileId: item.id })}>
      <View style={styles.fileCard}>
        <View style={styles.fileHeader}>
          <Text style={styles.fileNumber}>{item.file_number}</Text>
          <StatusBadge status={item.status} />
        </View>
        <Text style={styles.fileTitle}>{item.title}</Text>
        <View style={styles.fileFooter}>
          <Text style={[styles.priority, { color: PRIORITY_COLORS[item.priority] || '#757575' }]}>
            {item.priority}
          </Text>
          <Text style={styles.holder}>{item.current_holder_name || 'Unassigned'}</Text>
        </View>
      </View>
    </TouchableOpacity>
  )

  if (loading) return <ActivityIndicator size="large" style={styles.loader} />

  return (
    <View style={styles.container}>
      <Searchbar placeholder="Search files..." value={search} onChangeText={setSearch} style={styles.search} />
      <FlatList data={filtered} keyExtractor={(item) => String(item.id)} renderItem={renderItem}
        contentContainerStyle={filtered.length === 0 && styles.empty}
        ListEmptyComponent={<EmptyState icon="folder-open" message="No files found" />} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loader: { flex: 1, justifyContent: 'center' },
  search: { margin: 12, elevation: 1 },
  fileCard: { backgroundColor: '#fff', marginHorizontal: 12, marginBottom: 8, borderRadius: 8, padding: 14, elevation: 1 },
  fileHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  fileNumber: { fontSize: 13, color: '#1976d2', fontWeight: '600' },
  fileTitle: { fontSize: 15, fontWeight: '500', marginTop: 6 },
  fileFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  priority: { fontSize: 12, fontWeight: '600' },
  holder: { fontSize: 12, color: '#757575' },
  empty: { flex: 1 },
})
