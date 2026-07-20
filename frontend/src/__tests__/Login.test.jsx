import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import authReducer from '../store/authSlice'
import Login from '../pages/Login'

vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

function renderWithProviders(ui, { preloadedState = {}, store = configureStore({
  reducer: { auth: authReducer },
  preloadedState,
}) } = {}) {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </Provider>
  )
}

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form with email and password fields', () => {
    renderWithProviders(<Login />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('renders the portal title and subtitle', () => {
    renderWithProviders(<Login />)

    expect(screen.getByText('Education District IV')).toBeInTheDocument()
    expect(screen.getByText('Portal Login')).toBeInTheDocument()
  })

  it('renders Forgot Password link', () => {
    renderWithProviders(<Login />)

    const forgotLink = screen.getByText('Forgot Password?')
    expect(forgotLink).toBeInTheDocument()
    expect(forgotLink.closest('a')).toHaveAttribute('href', '/forgot-password')
  })

  it('updates email and password fields on input', () => {
    renderWithProviders(<Login />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })

    expect(emailInput.value).toBe('test@example.com')
    expect(passwordInput.value).toBe('password123')
  })

  it('shows loading state while login is in progress', () => {
    renderWithProviders(<Login />, {
      preloadedState: {
        auth: { loading: true, error: null, isAuthenticated: false, user: null },
      },
    })

    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })

  it('displays error message when login fails', () => {
    renderWithProviders(<Login />, {
      preloadedState: {
        auth: { loading: false, error: 'Invalid credentials', isAuthenticated: false, user: null },
      },
    })

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveClass('MuiAlert-root')
  })

  it('allows closing the error alert', () => {
    renderWithProviders(<Login />, {
      preloadedState: {
        auth: { loading: false, error: 'Something went wrong', isAuthenticated: false, user: null },
      },
    })

    const alert = screen.getByRole('alert')
    const closeBtn = alert.querySelector('button')
    fireEvent.click(closeBtn)

    // After clicking close, clearError should be dispatched
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('disables login button when loading', () => {
    renderWithProviders(<Login />, {
      preloadedState: {
        auth: { loading: true, error: null, isAuthenticated: false, user: null },
      },
    })

    // When loading, the button shows CircularProgress instead of text
    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })

  it('renders email field with correct type', () => {
    renderWithProviders(<Login />)

    const emailInput = screen.getByLabelText(/email/i)
    expect(emailInput).toHaveAttribute('type', 'email')
  })

  it('renders password field with correct type', () => {
    renderWithProviders(<Login />)

    const passwordInput = screen.getByLabelText(/password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')
  })
})
