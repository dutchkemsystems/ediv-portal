import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import { vi, describe, it, expect } from 'vitest'
import authReducer from '../store/authSlice'
import App from '../App'

vi.mock('../api/client', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: {} }), post: vi.fn().mockResolvedValue({ data: {} }) },
}))

vi.mock('../pages/Login', () => ({ default: () => <div data-testid="login-page">Login Page</div> }))
vi.mock('../pages/ForgotPassword', () => ({ default: () => <div data-testid="forgot-password-page">Forgot Password Page</div> }))
vi.mock('../pages/ResetPassword', () => ({ default: () => <div data-testid="reset-password-page">Reset Password Page</div> }))
vi.mock('../pages/Dashboard', () => ({ default: () => <div data-testid="dashboard-page">Dashboard Page</div> }))
vi.mock('../pages/Schools', () => ({ default: () => <div data-testid="schools-page">Schools Page</div> }))
vi.mock('../pages/Staff', () => ({ default: () => <div>Staff Page</div> }))
vi.mock('../pages/Students', () => ({ default: () => <div>Students Page</div> }))
vi.mock('../pages/Attendance', () => ({ default: () => <div>Attendance Page</div> }))
vi.mock('../pages/Academics', () => ({ default: () => <div>Academics Page</div> }))
vi.mock('../pages/Finance', () => ({ default: () => <div>Finance Page</div> }))
vi.mock('../pages/HR', () => ({ default: () => <div>HR Page</div> }))
vi.mock('../pages/Registry', () => ({ default: () => <div>Registry Page</div> }))
vi.mock('../pages/Files', () => ({ default: () => <div>Files Page</div> }))
vi.mock('../pages/Workflows', () => ({ default: () => <div>Workflows Page</div> }))
vi.mock('../pages/Communication', () => ({ default: () => <div>Communication Page</div> }))
vi.mock('../pages/Notifications', () => ({ default: () => <div>Notifications Page</div> }))
vi.mock('../pages/Timetable', () => ({ default: () => <div>Timetable Page</div> }))
vi.mock('../pages/Transport', () => ({ default: () => <div>Transport Page</div> }))
vi.mock('../pages/Assets', () => ({ default: () => <div>Assets Page</div> }))
vi.mock('../pages/Discipline', () => ({ default: () => <div>Discipline Page</div> }))
vi.mock('../pages/Library', () => ({ default: () => <div>Library Page</div> }))
vi.mock('../pages/ELearning', () => ({ default: () => <div>ELearning Page</div> }))
vi.mock('../pages/Wellness', () => ({ default: () => <div>Wellness Page</div> }))
vi.mock('../pages/Alumni', () => ({ default: () => <div>Alumni Page</div> }))
vi.mock('../pages/Infrastructure', () => ({ default: () => <div>Infrastructure Page</div> }))
vi.mock('../pages/Inspection', () => ({ default: () => <div>Inspection Page</div> }))
vi.mock('../pages/French', () => ({ default: () => <div>French Page</div> }))
vi.mock('../pages/CoCurricular', () => ({ default: () => <div>CoCurricular Page</div> }))
vi.mock('../pages/CPD', () => ({ default: () => <div>CPD Page</div> }))
vi.mock('../pages/Reports', () => ({ default: () => <div>Reports Page</div> }))
vi.mock('../components/common/Layout', () => ({ default: ({ children }) => <div data-testid="layout">{children}</div> }))

function renderWithProviders(ui, {
  preloadedState = {},
  store = configureStore({ reducer: { auth: authReducer }, preloadedState }),
  initialEntries = ['/'],
} = {}) {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={initialEntries}>
        {ui}
      </MemoryRouter>
    </Provider>
  )
}

describe('App Routing', () => {
  describe('unauthenticated users', () => {
    it('redirects to /login when accessing /', async () => {
      renderWithProviders(<App />, { initialEntries: ['/'] })
      await waitFor(() => expect(screen.getByTestId('login-page')).toBeInTheDocument())
    })

    it('redirects to /login when accessing /schools', async () => {
      renderWithProviders(<App />, { initialEntries: ['/schools'] })
      await waitFor(() => expect(screen.getByTestId('login-page')).toBeInTheDocument())
    })

    it('allows access to /login without auth', async () => {
      renderWithProviders(<App />, { initialEntries: ['/login'] })
      await waitFor(() => expect(screen.getByTestId('login-page')).toBeInTheDocument())
    })

    it('allows access to /forgot-password without auth', async () => {
      renderWithProviders(<App />, { initialEntries: ['/forgot-password'] })
      await waitFor(() => expect(screen.getByTestId('forgot-password-page')).toBeInTheDocument())
    })

    it('allows access to /reset-password without auth', async () => {
      renderWithProviders(<App />, { initialEntries: ['/reset-password'] })
      await waitFor(() => expect(screen.getByTestId('reset-password-page')).toBeInTheDocument())
    })
  })

  describe('authenticated users', () => {
    const authenticatedState = {
      auth: {
        user: { first_name: 'Test', role: 'SYSADMIN' },
        isAuthenticated: true,
        loading: false,
        error: null,
      },
    }

    it('shows dashboard when accessing /', async () => {
      renderWithProviders(<App />, { preloadedState: authenticatedState, initialEntries: ['/'] })
      await waitFor(() => expect(screen.getByTestId('dashboard-page')).toBeInTheDocument())
    })

    it('shows schools page when accessing /schools', async () => {
      renderWithProviders(<App />, { preloadedState: authenticatedState, initialEntries: ['/schools'] })
      await waitFor(() => expect(screen.getByTestId('schools-page')).toBeInTheDocument())
    })

    it('renders layout for protected routes', async () => {
      renderWithProviders(<App />, { preloadedState: authenticatedState, initialEntries: ['/'] })
      await waitFor(() => expect(screen.getByTestId('layout')).toBeInTheDocument())
    })

    it('still allows access to login page even when authenticated', async () => {
      renderWithProviders(<App />, { preloadedState: authenticatedState, initialEntries: ['/login'] })
      await waitFor(() => expect(screen.getByTestId('login-page')).toBeInTheDocument())
    })
  })

  describe('wildcard routes', () => {
    it('redirects unknown routes to /', async () => {
      const authenticatedState = {
        auth: {
          user: { first_name: 'Test', role: 'SYSADMIN' },
          isAuthenticated: true,
          loading: false,
          error: null,
        },
      }
      renderWithProviders(<App />, { preloadedState: authenticatedState, initialEntries: ['/nonexistent'] })
      await waitFor(() => expect(screen.getByTestId('dashboard-page')).toBeInTheDocument())
    })
  })
})
