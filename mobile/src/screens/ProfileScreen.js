import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text, Button, Avatar, Divider } from 'react-native-paper'
import { MaterialIcons } from '@expo/vector-icons'
import { useAuth } from '../services/AuthContext'

export default function ProfileScreen() {
  const { user, logout } = useAuth()

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text size={72} label={(user?.first_name?.[0] || 'U') + (user?.last_name?.[0] || '')} style={styles.avatar} />
        <Text style={styles.name}>{user?.first_name} {user?.last_name}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        <Text style={styles.role}>{user?.role}</Text>
      </View>

      <View style={styles.infoCard}>
        <InfoRow icon="email" label="Email" value={user?.email} />
        <Divider />
        <InfoRow icon="badge" label="Role" value={user?.role} />
        <Divider />
        <InfoRow icon="school" label="School" value={user?.school_name || 'N/A'} />
        <Divider />
        <InfoRow icon="business" label="Department" value={user?.department_name || 'N/A'} />
      </View>

      <Button mode="outlined" onPress={logout} textColor="#d32f2f" icon="logout" style={styles.logoutBtn}>
        Sign Out
      </Button>
    </View>
  )
}

function InfoRow({ icon, label, value }) {
  return (
    <View style={styles.infoRow}>
      <MaterialIcons name={icon} size={20} color="#757575" />
      <View style={styles.infoText}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value || 'N/A'}</Text>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { alignItems: 'center', paddingVertical: 32, backgroundColor: '#1976d2' },
  avatar: { backgroundColor: '#fff' },
  name: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginTop: 12 },
  email: { color: '#bbdefb', fontSize: 14, marginTop: 4 },
  role: { color: '#bbdefb', fontSize: 13, marginTop: 2, fontWeight: '600' },
  infoCard: { backgroundColor: '#fff', margin: 16, borderRadius: 12, padding: 16, elevation: 2 },
  infoRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10 },
  infoText: { marginLeft: 12 },
  infoLabel: { fontSize: 12, color: '#9e9e9e' },
  infoValue: { fontSize: 14, fontWeight: '500' },
  logoutBtn: { marginHorizontal: 16, marginTop: 8, borderColor: '#d32f2f' },
})
