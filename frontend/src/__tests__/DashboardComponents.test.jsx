import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import authReducer from '../store/authSlice'

// Mock react-apexcharts — jsdom lacks SVG getScreenCTM needed by apexcharts
vi.mock('react-apexcharts', () => ({
  default: () => <div data-testid="apex-chart" />,
}))

const mockGet = vi.fn()
vi.mock('../api/client', () => ({
  default: { get: (...args) => mockGet(...args) },
}))

import SysAdminDashboard from '../components/dashboard/SysAdminDashboard'
import HRDashboard from '../components/dashboard/HRDashboard'
import FinanceDashboard from '../components/dashboard/FinanceDashboard'
import PrincipalDashboard from '../components/dashboard/PrincipalDashboard'
import TeacherDashboard from '../components/dashboard/TeacherDashboard'
import RegistryDashboard from '../components/dashboard/RegistryDashboard'
import ParentDashboard from '../components/dashboard/ParentDashboard'

const theme = createTheme()

function renderWithProviders(ui, {
  preloadedState = {},
  store = configureStore({
    reducer: { auth: authReducer },
    preloadedState,
  }),
} = {}) {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <MemoryRouter>{ui}</MemoryRouter>
      </ThemeProvider>
    </Provider>
  )
}

const defaultMocks = () => {
  mockGet.mockImplementation((url) => {
    if (url.includes('students_by_lga')) return Promise.resolve({ data: [{ school__lga: 'Apapa', count: 5000 }] })
    if (url.includes('staff_by_role')) return Promise.resolve({ data: [{ category: 'Teaching', count: 300 }] })
    if (url.includes('attendance_stats')) return Promise.resolve({ data: [{ status: 'PRESENT', count: 500 }, { status: 'ABSENT', count: 50 }] })
    if (url.includes('financial_stats')) return Promise.resolve({ data: { total_collected: 1000000, collection_rate: 78 } })
    if (url.includes('user_stats')) return Promise.resolve({ data: { total_users: 100, recent_logins_24h: 20 } })
    if (url.includes('system_status')) return Promise.resolve({ data: { database: 'online', storage_percent: 67 } })
    if (url.includes('recent_activity')) return Promise.resolve({ data: { recent_files: [], recent_tasks: [] } })
    return Promise.resolve({ data: { total_schools: 0, total_students: 0, total_staff: 0, active_files: 0, pending_files: 0 } })
  })
}

describe('Role-specific Dashboard Components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    defaultMocks()
  })

  it('SysAdminDashboard renders KPI cards', async () => {
    renderWithProviders(<SysAdminDashboard />, {
      preloadedState: { auth: { user: { first_name: 'Admin', role: 'SYSADMIN' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.getByText('Total Schools')).toBeInTheDocument()
      expect(screen.getByText('Revenue Collected')).toBeInTheDocument()
      expect(screen.getByText('Attendance Rate')).toBeInTheDocument()
    })
  })

  it('HRDashboard renders without error', async () => {
    renderWithProviders(<HRDashboard />, {
      preloadedState: { auth: { user: { first_name: 'HR', role: 'HR' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })

  it('FinanceDashboard renders without error', async () => {
    renderWithProviders(<FinanceDashboard />, {
      preloadedState: { auth: { user: { first_name: 'FIN', role: 'FIN' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      // FinanceDashboard always has a LinearProgress (collection rate bar) after loading
      expect(screen.getByText('Finance Dashboard')).toBeInTheDocument()
    })
  })

  it('PrincipalDashboard handles missing school gracefully', async () => {
    mockGet.mockRejectedValueOnce({ response: { status: 400, data: { error: 'No school assigned' } } })
    renderWithProviders(<PrincipalDashboard />, {
      preloadedState: { auth: { user: { first_name: 'Pri', role: 'PRI' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })

  it('TeacherDashboard renders without error', async () => {
    renderWithProviders(<TeacherDashboard />, {
      preloadedState: { auth: { user: { first_name: 'T', role: 'TCH' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })

  it('RegistryDashboard renders without error', async () => {
    renderWithProviders(<RegistryDashboard />, {
      preloadedState: { auth: { user: { first_name: 'R', role: 'REG' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })

  it('ParentDashboard handles empty children list', async () => {
    mockGet.mockResolvedValueOnce({ data: { children: [], total_children: 0 } })
    renderWithProviders(<ParentDashboard />, {
      preloadedState: { auth: { user: { first_name: 'P', role: 'PAR' }, isAuthenticated: true } },
    })
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })
  })

  it('all dashboards handle API failures without crashing', async () => {
    mockGet.mockImplementation(() => Promise.reject(new Error('Network')))
    const components = [
      SysAdminDashboard, HRDashboard, FinanceDashboard, PrincipalDashboard,
      TeacherDashboard, RegistryDashboard, ParentDashboard,
    ]
    for (const Comp of components) {
      const { unmount, container } = renderWithProviders(<Comp />, {
        preloadedState: { auth: { user: { first_name: 'X', role: 'SYSADMIN' }, isAuthenticated: true } },
      })
      // Wait for loading to complete — component renders without crashing
      await waitFor(() => {
        expect(container.querySelector('[class*="MuiBox"]')).toBeInTheDocument()
      })
      unmount()
    }
  })
})
