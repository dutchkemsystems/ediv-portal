import React from 'react'
import { StatusBar } from 'expo-status-bar'
import { Provider as PaperProvider } from 'react-native-paper'
import { AuthProvider } from './src/services/AuthContext'
import AppNavigator from './src/navigation/AppNavigator'

export default function App() {
  return (
    <PaperProvider>
      <AuthProvider>
        <StatusBar style="light" />
        <AppNavigator />
      </AuthProvider>
    </PaperProvider>
  )
}
