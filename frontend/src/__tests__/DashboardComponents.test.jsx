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

import SysAdminDashboard from '../components/dashboard/SysAdminDashboard'
import HRDashboard from '../components/dashboard/HRDashboard'
import FinanceDashboard from '../components/dashboard/FinanceDashboard'
import PrincipalDashboard from '../components/dashboard/PrincipalDashboard'
import TeacherDashboard from '../components/dashboard/TeacherDashboard'
import RegistryDashboard from '../components/dashboard/RegistryDashboard'
import ParentDashboard from '../components/dashboard/ParentDashboard'

function renderWithProviders(ui, {
  preloadedState = {},
  store = configureStore({
    reducer: { auth: authReducer },
    preloadedState,
  }),
} = {}) {
  return render(
    <Provider store={store}>
      <MemoryRouter>{ui}</MemoryRouter>
    </Provider>
  )
}

const emptyStats = {
  total_schools: 0, total_students: 0, total_staff: 0, total_files: 0,
  active_files: 0, pending_files: 0,
}

const defaultMocks = () => {
  mockGet.mockImplementation(() => Promise.resolve({ data: emptyStats }))
}

describe('Role-specific Dashboard Components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    defaultMocks()
  })

  it('SysAdminDashboard renders 8 KPI cards', async () => {
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
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
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
      const { unmount } = renderWithProviders(<Comp />, {
        preloadedState: { auth: { user: { first_name: 'X', role: 'SYSADMIN' }, isAuthenticated: true } },
      })
      await waitFor(() => {
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
      })
      unmount()
    }
  })
})
