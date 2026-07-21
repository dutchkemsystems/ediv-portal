import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import authReducer from '../store/authSlice'

const mockGet = vi.fn()
vi.mock('../api/client', () => ({
  default: { get: (...args) => mockGet(...args) },
}))

import Dashboard from '../pages/Dashboard'

function renderWithProviders(ui, {
  preloadedState = {},
  store = configureStore({
    reducer: { auth: authReducer },
    preloadedState,
  }),
} = {}) {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </Provider>
  )
}

const mockStatsData = {
  total_schools: 25,
  total_students: 5000,
  total_staff: 350,
  active_files: 120,
}

const mockActivityData = {
  recent_files: [
    { file__title: 'Transfer Letter', action: 'TRANSFERRED', from_holder__first_name: 'John', to_holder__first_name: 'Jane' },
  ],
  recent_tasks: [],
}

describe('Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner while data is being fetched', () => {
    mockGet.mockReturnValue(new Promise(() => {}))

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('renders welcome message with user name', async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockStatsData })
      .mockResolvedValueOnce({ data: mockActivityData })

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'John', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Welcome, John')).toBeInTheDocument()
    })
  })

  it('renders subtitle text', async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockStatsData })
      .mockResolvedValueOnce({ data: mockActivityData })

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'Admin', role: 'TG' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Education District IV Portal Dashboard')).toBeInTheDocument()
    })
  })

  it('renders stat cards with data from API', async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockStatsData })
      .mockResolvedValueOnce({ data: mockActivityData })

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Total Schools')).toBeInTheDocument()
      expect(screen.getByText('Total Students')).toBeInTheDocument()
      expect(screen.getByText('Total Staff')).toBeInTheDocument()
      expect(screen.getByText('Active Files')).toBeInTheDocument()
    })
  })

  it('calls both API endpoints on mount', async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockStatsData })
      .mockResolvedValueOnce({ data: mockActivityData })

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith('/analytics/stats/overview/')
      expect(mockGet).toHaveBeenCalledWith('/analytics/stats/recent_activity/')
    })
  })

  it('handles API error gracefully', async () => {
    mockGet.mockRejectedValue(new Error('Network Error'))

    renderWithProviders(<Dashboard />, {
      preloadedState: {
        auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
      },
    })

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })
})
