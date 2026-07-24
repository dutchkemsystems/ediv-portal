import React, { useState, useEffect } from 'react'
import { View, ScrollView, StyleSheet } from 'react-native'
import { Text, Button, Divider, ActivityIndicator } from 'react-native-paper'
import { MaterialIcons } from '@expo/vector-icons'
import api from '../services/api'
import { useAuth } from '../services/AuthContext'
import StatusBadge from '../components/StatusBadge'

export default function FileDetailScreen({ route, navigation }) {
  const { fileId } = route.params
  const { user } = useAuth()
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchFile = async () => {
    try {
      const res = await api.get(`/files/files/${fileId}/`)
      setFile(res.data)
    } catch {
      /* silent */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchFile() }, [fileId])

  const handleReceive = async () => {
    try {
      await api.post(`/files/files/${fileId}/receive/`)
      fetchFile()
    } catch {
      /* silent */
    }
  }

  const handleClose = async () => {
    try {
      await api.post(`/files/files/${fileId}/close/`)
      fetchFile()
    } catch {
      /* silent */
    }
  }

  if (loading) return <ActivityIndicator size="large" style={styles.loader} />
  if (!file) return <View style={styles.container}><Text>File not found</Text></View>

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.fileNumber}>{file.file_number}</Text>
        <StatusBadge status={file.status} />
      </View>

      <Text style={styles.title}>{file.title}</Text>
      {file.description ? <Text style={styles.desc}>{file.description}</Text> : null}

      <View style={styles.infoRow}>
        <InfoItem icon="person" label="Created by" value={file.created_by_name} />
        <InfoItem icon="person-outline" label="Current holder" value={file.current_holder_name || 'None'} />
      </View>
      <View style={styles.infoRow}>
        <InfoItem icon="business" label="Department" value={file.department_name || 'N/A'} />
        <InfoItem icon="priority-high" label="Priority" value={file.priority} />
      </View>
      <View style={styles.infoRow}>
        <InfoItem icon="security" label="Classification" value={file.classification} />
        <InfoItem icon="category" label="Type" value={file.file_type} />
      </View>

      {file.status_timeline?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Status Timeline</Text>
          {file.status_timeline.map((entry, i) => (
            <View key={i} style={styles.timelineItem}>
              <MaterialIcons name="radio-button-checked" size={16} color="#1976d2" />
              <View style={{ marginLeft: 8 }}>
                <Text style={styles.timelineStatus}>{entry.status}</Text>
                <Text style={styles.timelineNotes}>{entry.notes}</Text>
                <Text style={styles.timelineDate}>{new Date(entry.timestamp).toLocaleString()}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {file.movements?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Movement History</Text>
          {file.movements.map((m) => (
            <View key={m.id} style={styles.movementCard}>
              <Text style={styles.movementAction}>{m.action}</Text>
              <Text style={styles.movementDetail}>{m.from_holder_name} → {m.to_holder_name}</Text>
              {m.remarks ? <Text style={styles.movementRemarks}>{m.remarks}</Text> : null}
            </View>
          ))}
        </View>
      )}

      <View style={styles.actions}>
        {file.current_holder_name?.includes(user?.first_name) && file.status === 'IN_TRANSIT' && (
          <Button mode="contained" onPress={handleReceive} buttonColor="#2e7d32" style={styles.actionBtn}>Receive</Button>
        )}
        {(file.created_by_name?.includes(user?.first_name) || ['SYSADMIN', 'TG', 'PS'].includes(user?.role)) && (
          <Button mode="outlined" onPress={handleClose} textColor="#d32f2f" style={styles.actionBtn}>Close File</Button>
        )}
      </View>
    </ScrollView>
  )
}

function InfoItem({ icon, label, value }) {
  return (
    <View style={styles.infoItem}>
      <MaterialIcons name={icon} size={18} color="#757575" />
      <View style={{ marginLeft: 6 }}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 16 },
  loader: { flex: 1, justifyContent: 'center' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  fileNumber: { fontSize: 14, color: '#1976d2', fontWeight: '600' },
  title: { fontSize: 20, fontWeight: 'bold', marginTop: 8 },
  desc: { fontSize: 14, color: '#616161', marginTop: 4 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 12 },
  infoItem: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  infoLabel: { fontSize: 11, color: '#9e9e9e' },
  infoValue: { fontSize: 13, fontWeight: '500' },
  section: { marginTop: 20 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', marginBottom: 8 },
  timelineItem: { flexDirection: 'row', marginBottom: 8 },
  timelineStatus: { fontSize: 13, fontWeight: '600' },
  timelineNotes: { fontSize: 12, color: '#616161' },
  timelineDate: { fontSize: 11, color: '#9e9e9e' },
  movementCard: { backgroundColor: '#fff', borderRadius: 8, padding: 10, marginBottom: 6, elevation: 1 },
  movementAction: { fontSize: 13, fontWeight: '600' },
  movementDetail: { fontSize: 12, color: '#616161', marginTop: 2 },
  movementRemarks: { fontSize: 12, color: '#9e9e9e', fontStyle: 'italic' },
  actions: { marginTop: 24, gap: 8 },
  actionBtn: { marginBottom: 8 },
})
