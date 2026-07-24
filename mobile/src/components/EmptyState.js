import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { MaterialIcons } from '@expo/vector-icons'

export default function EmptyState({ icon = 'inbox', message = 'No data available' }) {
  return (
    <View style={styles.container}>
      <MaterialIcons name={icon} size={48} color="#bdbdbd" />
      <Text style={styles.text}>{message}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  text: { marginTop: 12, color: '#9e9e9e', fontSize: 16 },
})
