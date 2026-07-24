import React, { useState, useEffect, useCallback } from 'react'
import { View, FlatList, StyleSheet } from 'react-native'
import { Text, SegmentedButtons, ActivityIndicator } from 'react-native-paper'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'

export default function RegistryScreen() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const fetchDocs = useCallback(async () => {
    try {
      const res = await api.get('/registry/documents/')
      setDocs(res.data.results || res.data)
    } catch {
      /* silent */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  const filtered = filter === 'all' ? docs : docs.filter((d) => d.status === filter.toUpperCase())

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.refNumber}>{item.reference_number}</Text>
        <StatusBadge status={item.status} />
      </View>
      <Text style={styles.docTitle}>{item.title}</Text>
      <View style={styles.cardFooter}>
        <Text style={styles.docType}>{item.document_type}</Text>
        <Text style={styles.createdBy}>{item.created_by_name}</Text>
      </View>
    </View>
  )

  if (loading) return <ActivityIndicator size="large" style={styles.loader} />

  return (
    <View style={styles.container}>
      <SegmentedButtons value={filter} onValueChange={setFilter}
        buttons={[
          { value: 'all', label: 'All' },
          { value: 'pending', label: 'Pending' },
          { value: 'approved', label: 'Approved' },
        ]} style={styles.tabs} />
      <FlatList data={filtered} keyExtractor={(item) => String(item.id)} renderItem={renderItem}
        contentContainerStyle={filtered.length === 0 && styles.empty}
        ListEmptyComponent={<EmptyState icon="description" message="No documents found" />} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loader: { flex: 1, justifyContent: 'center' },
  tabs: { margin: 12 },
  card: { backgroundColor: '#fff', marginHorizontal: 12, marginBottom: 8, borderRadius: 8, padding: 14, elevation: 1 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  refNumber: { fontSize: 13, color: '#1976d2', fontWeight: '600' },
  docTitle: { fontSize: 15, fontWeight: '500', marginTop: 6 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  docType: { fontSize: 12, color: '#757575' },
  createdBy: { fontSize: 12, color: '#757575' },
  empty: { flex: 1 },
})
