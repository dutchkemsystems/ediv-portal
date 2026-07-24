import React, { useState } from 'react'
import { View, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native'
import { TextInput, Button, Text, Surface, HelperText } from 'react-native-paper'
import { MaterialIcons } from '@expo/vector-icons'
import { useAuth } from '../services/AuthContext'

export default function LoginScreen() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [secureEntry, setSecureEntry] = useState(true)
  const { login } = useAuth()

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter email and password')
      return
    }
    setLoading(true)
    setError('')
    try {
      await login(email, password)
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Login failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <MaterialIcons name="school" size={64} color="#fff" />
          <Text style={styles.title}>Education District IV</Text>
          <Text style={styles.subtitle}>Portal Login</Text>
        </View>

        <Surface style={styles.card}>
          <TextInput label="Email" value={email} onChangeText={setEmail}
            mode="outlined" keyboardType="email-address" autoCapitalize="none"
            left={<TextInput.Icon icon="email" />} style={styles.input} />

          <TextInput label="Password" value={password} onChangeText={setPassword}
            mode="outlined" secureTextEntry={secureEntry}
            left={<TextInput.Icon icon="lock" />}
            right={<TextInput.Icon icon={secureEntry ? 'eye' : 'eye-off'} onPress={() => setSecureEntry(!secureEntry)} />}
            style={styles.input} />

          {error ? <HelperText type="error">{error}</HelperText> : null}

          <Button mode="contained" onPress={handleLogin} loading={loading} disabled={loading}
            style={styles.button} buttonColor="#1976d2">
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </Surface>

        <Text style={styles.footer}>Education District IV Portal v1.0</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1976d2' },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  header: { alignItems: 'center', marginBottom: 32 },
  title: { color: '#fff', fontSize: 24, fontWeight: 'bold', marginTop: 8 },
  subtitle: { color: '#bbdefb', fontSize: 16, marginTop: 4 },
  card: { borderRadius: 12, padding: 24, elevation: 4 },
  input: { marginBottom: 12 },
  button: { marginTop: 8, paddingVertical: 4 },
  footer: { textAlign: 'center', color: '#bbdefb', marginTop: 24, fontSize: 12 },
})
