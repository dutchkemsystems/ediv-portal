import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/client'

export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await api.post('/users/auth/', { email, password })

      // Handle MFA required response
      if (response.data.mfa_required) {
        localStorage.setItem('temp_token', response.data.temp_token)
        localStorage.setItem('pending_user', JSON.stringify(response.data.user))
        return { mfa_required: true, user: response.data.user }
      }

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      return response.data
    } catch (error) {
      // No response = network error or timeout (likely Render cold start)
      if (!error.response) {
        const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout')
        return rejectWithValue({
          error: isTimeout
            ? 'Server is taking too long to respond (cold start). Please wait 30 seconds and try again.'
            : 'Could not reach the login server. Please check your internet connection.',
        })
      }
      return rejectWithValue(error.response?.data || { error: 'Login failed' })
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  const refreshToken = localStorage.getItem('refresh_token')
  try {
    await api.post('/users/auth/logout/', { refresh: refreshToken })
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('temp_token')
    localStorage.removeItem('pending_user')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    mfa_required: false,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearMFARequired: (state) => {
      state.mfa_required = false
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
        state.mfa_required = false
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        if (action.payload.mfa_required) {
          state.mfa_required = true
          state.user = action.payload.user
        } else {
          state.isAuthenticated = true
          state.user = action.payload.user
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        const err = action.payload
        // Backend uses DRF + custom_exception_handler that wraps errors as:
        //   { success: false, error: { status_code, message } }
        // Unwrap that first, then fall back to common shapes.
        let unwrapped = err
        if (err && typeof err === 'object' && err.error && typeof err.error === 'object') {
          unwrapped = err.error.message
        }
        // Ensure error is always a string, never an object
        if (typeof unwrapped === 'string') {
          state.error = unwrapped
        } else if (typeof unwrapped?.error === 'string') {
          state.error = unwrapped.error
        } else if (typeof unwrapped?.detail === 'string') {
          state.error = unwrapped.detail
        } else if (typeof unwrapped?.message === 'string') {
          state.error = unwrapped.message
        } else if (unwrapped && typeof unwrapped === 'object') {
          // DRF validation errors: {field: ["error msg", ...]}
          // Flatten into first human-readable message
          const flat = []
          for (const v of Object.values(unwrapped)) {
            if (typeof v === 'string') flat.push(v)
            else if (Array.isArray(v)) {
              for (const item of v) {
                if (typeof item === 'string') flat.push(item)
              }
            }
          }
          state.error = flat[0] || 'Login failed. Please check your credentials.'
        } else {
          state.error = 'Login failed. Please check your credentials.'
        }
      })
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.mfa_required = false
      })
  },
})

export const { clearError, clearMFARequired } = authSlice.actions
export default authSlice.reducer
