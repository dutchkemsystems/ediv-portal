import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { MaterialIcons } from '@expo/vector-icons'
import { useAuth } from '../services/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

import LoginScreen from '../screens/LoginScreen'
import DashboardScreen from '../screens/DashboardScreen'
import FilesScreen from '../screens/FilesScreen'
import FileDetailScreen from '../screens/FileDetailScreen'
import RegistryScreen from '../screens/RegistryScreen'
import NotificationsScreen from '../screens/NotificationsScreen'
import ProfileScreen from '../screens/ProfileScreen'

const Stack = createNativeStackNavigator()
const Tab = createBottomTabNavigator()

const TAB_ICONS = {
  Dashboard: 'dashboard',
  Files: 'folder',
  Registry: 'description',
  Notifications: 'notifications',
  Profile: 'person',
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
    </Stack.Navigator>
  )
}

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => (
          <MaterialIcons name={TAB_ICONS[route.name] || 'circle'} size={size} color={color} />
        ),
        tabBarActiveTintColor: '#1976d2',
        tabBarInactiveTintColor: '#9e9e9e',
        headerStyle: { backgroundColor: '#1976d2' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard' }} />
      <Tab.Screen name="Files" component={FilesScreen} options={{ title: 'E-Files' }} />
      <Tab.Screen name="Registry" component={RegistryScreen} options={{ title: 'Registry' }} />
      <Tab.Screen name="Notifications" component={NotificationsScreen} options={{ title: 'Alerts' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profile' }} />
    </Tab.Navigator>
  )
}

function AuthStacks() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Tabs" component={TabNavigator} />
      <Stack.Screen
        name="FileDetail"
        component={FileDetailScreen}
        options={{ headerShown: true, title: 'File Detail', headerStyle: { backgroundColor: '#1976d2' }, headerTintColor: '#fff' }}
      />
    </Stack.Navigator>
  )
}

export default function AppNavigator() {
  const { user, loading } = useAuth()

  if (loading) return <LoadingSpinner />

  return (
    <NavigationContainer>
      {user ? <AuthStacks /> : <AuthStack />}
    </NavigationContainer>
  )
}
