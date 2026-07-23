import axios from 'axios'

// Determine the API base URL
// If VITE_API_URL is set and is a full URL, use it directly
// If VITE_API_URL is '/api' or unset, try to detect the backend URL
const configuredUrl = import.meta.env.VITE_API_URL
let baseURL = '/api'

if (configuredUrl) {
  if (configuredUrl.startsWith('http')) {
    // Full URL provided (e.g., https://ediv-portal.onrender.com/api)
    baseURL = configuredUrl
  } else {
    // Relative path - check if we're on a static site (no backend proxy)
    // On Render static sites, /api goes to the static site itself
    // We need to redirect to the backend
    const backendUrl = import.meta.env.VITE_BACKEND_URL
    if (backendUrl) {
      baseURL = `${backendUrl}/api`
    } else {
      baseURL = configuredUrl
    }
  }
}

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only attempt refresh on 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/users/auth/') {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }
        const response = await axios.post(`${baseURL}/users/auth/refresh/`, {
          refresh: refreshToken,
        })
        localStorage.setItem('access_token', response.data.access)
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default api
