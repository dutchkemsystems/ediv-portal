import React, { createContext, useState, useEffect, useContext } from 'react'
import * as SecureStore from 'expo-secure-store'
import api from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadToken = async () => {
      try {
        const storedToken = await SecureStore.getItemAsync('access_token')
        const storedUser = await SecureStore.getItemAsync('user_data')
        if (storedToken && storedUser) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
        }
      } catch {
        /* silent */
      } finally {
        setLoading(false)
      }
    }
    loadToken()
  }, [])

  const login = async (email, password) => {
    const res = await api.post('/users/auth/', { email, password })
    const { access, refresh, user: userData } = res.data
    await SecureStore.setItemAsync('access_token', access)
    await SecureStore.setItemAsync('refresh_token', refresh)
    await SecureStore.setItemAsync('user_data', JSON.stringify(userData))
    setToken(access)
    setUser(userData)
    return userData
  }

  const logout = async () => {
    await SecureStore.deleteItemAsync('access_token')
    await SecureStore.deleteItemAsync('refresh_token')
    await SecureStore.deleteItemAsync('user_data')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
