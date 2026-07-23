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
        state.error = action.payload?.error || 'Login failed'
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
