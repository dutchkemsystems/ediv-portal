import axios from 'axios'

// Determine the API base URL
const configuredUrl = import.meta.env.VITE_API_URL
let baseURL = '/api'

// If no explicit URL configured, auto-detect backend based on current hostname
if (!configuredUrl) {
  const hostname = window.location.hostname
  // If frontend is on a separate static site, point API to the backend
  if (hostname.includes('ediv-frontend-static')) {
    baseURL = 'https://ediv-portal.onrender.com/api'
  } else if (hostname.includes('onrender.com') && !hostname.includes('ediv-portal')) {
    // Any other Render static site - try the backend URL
    const backendUrl = import.meta.env.VITE_BACKEND_URL
    if (backendUrl) {
      baseURL = `${backendUrl}/api`
    }
  }
} else if (configuredUrl.startsWith('http')) {
  baseURL = configuredUrl
}

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Render free tier services sleep after 15min inactivity and need ~30s to wake up.
  // Set timeout to 60s to give cold-start requests time to complete.
  timeout: 60000,
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
