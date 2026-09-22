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

// Mock lazy-loaded dashboard components
vi.mock('../components/dashboard/SysAdminDashboard', () => ({
  default: function SysAdminDashboard() {
    return <div><h2>System Overview</h2></div>
  },
}))
vi.mock('../components/dashboard/FinanceDashboard', () => ({
  default: function FinanceDashboard() {
    return <div><h2>Financial Overview</h2></div>
  },
}))
vi.mock('../components/dashboard/PrincipalDashboard', () => ({
  default: function PrincipalDashboard() {
    return <div><h2>School Operations Overview</h2></div>
  },
}))
vi.mock('../components/dashboard/ParentDashboard', () => ({
  default: function ParentDashboard() {
    return <div><h2>Your Children's Overview</h2></div>
  },
}))
vi.mock('../components/dashboard/StaffEnterpriseDashboard', () => ({
  default: function StaffEnterpriseDashboard() {
    return <div><h2>Staff Dashboard</h2></div>
  },
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

  describe('Generic Dashboard (non-role-specific)', () => {
    const genericRole = 'UNKNOWN_ROLE'

    it('shows loading state while data is being fetched', () => {
      mockGet.mockReturnValue(new Promise(() => {}))

      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Admin', role: genericRole }, isAuthenticated: true, loading: false, error: null },
        },
      })

      expect(screen.getByTestId('loading')).toBeInTheDocument()
    })

    it('renders welcome message with user name', async () => {
      mockGet
        .mockResolvedValueOnce({ data: mockStatsData })
        .mockResolvedValueOnce({ data: mockActivityData })

      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'John', role: genericRole }, isAuthenticated: true, loading: false, error: null },
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
          auth: { user: { first_name: 'Admin', role: genericRole }, isAuthenticated: true, loading: false, error: null },
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
          auth: { user: { first_name: 'Admin', role: genericRole }, isAuthenticated: true, loading: false, error: null },
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
          auth: { user: { first_name: 'Admin', role: genericRole }, isAuthenticated: true, loading: false, error: null },
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
          auth: { user: { first_name: 'Admin', role: genericRole }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
      })
    })
  })

  describe('Role-specific Dashboard Routing', () => {
    it('routes SYSADMIN to SysAdminDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('System Overview')).toBeInTheDocument()
      })
    })

    it('routes HR to StaffEnterpriseDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'HR Manager', role: 'HR' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('Staff Dashboard')).toBeInTheDocument()
      })
    })

    it('routes FIN to FinanceDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Finance', role: 'FIN' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('Financial Overview')).toBeInTheDocument()
      })
    })

    it('routes PRI to PrincipalDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Principal', role: 'PRI' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('School Operations Overview')).toBeInTheDocument()
      })
    })

    it('routes TCH to StaffEnterpriseDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Teacher', role: 'TCH' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('Staff Dashboard')).toBeInTheDocument()
      })
    })

    it('routes REG to StaffEnterpriseDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Registry', role: 'REG' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('Staff Dashboard')).toBeInTheDocument()
      })
    })

    it('routes PAR to ParentDashboard', async () => {
      renderWithProviders(<Dashboard />, {
        preloadedState: {
          auth: { user: { first_name: 'Parent', role: 'PAR' }, isAuthenticated: true, loading: false, error: null },
        },
      })

      await waitFor(() => {
        expect(screen.getByText("Your Children's Overview")).toBeInTheDocument()
      })
    })
  })
})
