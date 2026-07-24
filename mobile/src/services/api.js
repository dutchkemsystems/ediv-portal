import axios from 'axios'
import * as SecureStore from 'expo-secure-store'

const BASE_URL = 'https://ediv-portal.onrender.com/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = await SecureStore.getItemAsync('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post(`${BASE_URL}/users/auth/refresh/`, { refresh: refreshToken })
          await SecureStore.setItemAsync('access_token', res.data.access)
          error.config.headers.Authorization = `Bearer ${res.data.access}`
          return api(error.config)
        } catch {
          await SecureStore.deleteItemAsync('access_token')
          await SecureStore.deleteItemAsync('refresh_token')
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
