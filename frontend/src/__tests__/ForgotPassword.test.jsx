import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import ForgotPassword from '../pages/ForgotPassword'

const mockPost = vi.fn()

vi.mock('../api/client', () => ({
  default: { post: (...args) => mockPost(...args) },
}))

function renderComponent() {
  return render(
    <MemoryRouter>
      <ForgotPassword />
    </MemoryRouter>
  )
}

describe('ForgotPassword Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title and description', () => {
    renderComponent()

    expect(screen.getByText('Forgot Password')).toBeInTheDocument()
    expect(screen.getByText(/enter your email address/i)).toBeInTheDocument()
  })

  it('renders email input field', () => {
    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    expect(emailInput).toBeInTheDocument()
    expect(emailInput).toHaveAttribute('type', 'email')
  })

  it('renders the submit button', () => {
    renderComponent()

    expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument()
  })

  it('renders "Back to Login" link', () => {
    renderComponent()

    const backLinks = screen.getAllByText(/back to login/i)
    expect(backLinks.length).toBeGreaterThanOrEqual(1)
    expect(backLinks[0].closest('a')).toHaveAttribute('href', '/login')
  })

  it('updates email field on input', () => {
    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    expect(emailInput.value).toBe('test@example.com')
  })

  it('calls API with email on form submission', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } })

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    const submitBtn = screen.getByRole('button', { name: /send reset link/i })

    fireEvent.change(emailInput, { target: { value: 'user@ediv.gov.ng' } })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith('/users/auth/forgot_password/', { email: 'user@ediv.gov.ng' })
    })
  })

  it('shows success message after successful submission', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } })

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    const submitBtn = screen.getByRole('button', { name: /send reset link/i })

    fireEvent.change(emailInput, { target: { value: 'user@ediv.gov.ng' } })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(screen.getByText(/if an account exists with/i)).toBeInTheDocument()
      expect(screen.getByText('user@ediv.gov.ng')).toBeInTheDocument()
    })
  })

  it('shows error message on API failure', async () => {
    mockPost.mockRejectedValueOnce({
      response: { data: { error: 'Server error occurred' } },
    })

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    const submitBtn = screen.getByRole('button', { name: /send reset link/i })

    fireEvent.change(emailInput, { target: { value: 'user@example.com' } })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(screen.getByText('Server error occurred')).toBeInTheDocument()
    })
  })

  it('shows default error message when API returns no error field', async () => {
    mockPost.mockRejectedValueOnce(new Error('Network Error'))

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    const submitBtn = screen.getByRole('button', { name: /send reset link/i })

    fireEvent.change(emailInput, { target: { value: 'user@example.com' } })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    })
  })

  it('shows loading state during submission', async () => {
    mockPost.mockReturnValueOnce(new Promise(() => {})) // never resolves

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    const submitBtn = screen.getByRole('button', { name: /send reset link/i })

    fireEvent.change(emailInput, { target: { value: 'user@example.com' } })
    fireEvent.click(submitBtn)

    // Button should be disabled and show spinner instead of text
    await waitFor(() => {
      expect(submitBtn).toBeDisabled()
    })
  })

  it('renders password reset instructions after success', async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true } })

    renderComponent()

    const emailInput = screen.getByLabelText(/email address/i)
    fireEvent.change(emailInput, { target: { value: 'user@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: /send reset link/i }))

    await waitFor(() => {
      expect(screen.getByText(/didn't receive the email/i)).toBeInTheDocument()
      expect(screen.getByText(/check your spam folder/i)).toBeInTheDocument()
    })
  })
})
