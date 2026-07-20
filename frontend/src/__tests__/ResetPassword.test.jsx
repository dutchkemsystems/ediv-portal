import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import ResetPassword from '../pages/ResetPassword'

const mockPost = vi.fn()

vi.mock('../api/client', () => ({
  default: { post: (...args) => mockPost(...args) },
}))

function renderWithToken(token = 'valid-token-123') {
  const searchParams = token ? `?token=${token}` : ''
  return render(
    <MemoryRouter initialEntries={[`/reset-password${searchParams}`]}>
      <ResetPassword />
    </MemoryRouter>
  )
}

describe('ResetPassword Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('with valid token', () => {
    it('renders the reset password heading', () => {
      renderWithToken()
      expect(screen.getByRole('heading', { name: /reset password/i })).toBeInTheDocument()
    })

    it('renders the subtitle text', () => {
      renderWithToken()
      expect(screen.getByText(/enter your new password below/i)).toBeInTheDocument()
    })

    it('renders new password input field', () => {
      renderWithToken()
      const passwordFields = screen.getAllByLabelText(/new password/i)
      const passwordField = passwordFields[0]
      expect(passwordField).toBeInTheDocument()
      expect(passwordField).toHaveAttribute('type', 'password')
    })

    it('renders confirm password input field', () => {
      renderWithToken()
      const confirmField = screen.getByLabelText(/confirm new password/i)
      expect(confirmField).toBeInTheDocument()
      expect(confirmField).toHaveAttribute('type', 'password')
    })

    it('renders the reset password submit button', () => {
      renderWithToken()
      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      expect(resetBtn).toBeInTheDocument()
    })

    it('renders password requirements info', () => {
      renderWithToken()
      expect(screen.getByText(/password must be at least 12 characters/i)).toBeInTheDocument()
    })

    it('shows error when passwords do not match', async () => {
      renderWithToken()
      const passwordFields = screen.getAllByLabelText(/new password/i)
      const newPw = passwordFields[0]
      const confirmPw = screen.getByLabelText(/confirm new password/i)

      fireEvent.change(newPw, { target: { value: 'ValidPassword123!' } })
      fireEvent.change(confirmPw, { target: { value: 'DifferentPassword123!' } })

      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      fireEvent.click(resetBtn)

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match.')).toBeInTheDocument()
      })
    })

    it('shows error when password is too short', async () => {
      renderWithToken()
      const passwordFields = screen.getAllByLabelText(/new password/i)
      const newPw = passwordFields[0]
      const confirmPw = screen.getByLabelText(/confirm new password/i)

      fireEvent.change(newPw, { target: { value: 'Short1!' } })
      fireEvent.change(confirmPw, { target: { value: 'Short1!' } })

      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      fireEvent.click(resetBtn)

      await waitFor(() => {
        const matches = screen.getAllByText(/password must be at least 12 characters/i)
        expect(matches.length).toBeGreaterThanOrEqual(1)
      })
    })

    it('calls API on valid submission', async () => {
      mockPost.mockResolvedValueOnce({ data: { success: true } })
      renderWithToken()

      const passwordFields = screen.getAllByLabelText(/new password/i)
      const newPw = passwordFields[0]
      const confirmPw = screen.getByLabelText(/confirm new password/i)

      fireEvent.change(newPw, { target: { value: 'ValidPassword1234!' } })
      fireEvent.change(confirmPw, { target: { value: 'ValidPassword1234!' } })

      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      fireEvent.click(resetBtn)

      await waitFor(() => {
        expect(mockPost).toHaveBeenCalledWith('/users/auth/reset_password/', {
          token: 'valid-token-123',
          new_password: 'ValidPassword1234!',
          new_password_confirm: 'ValidPassword1234!',
        })
      })
    })

    it('shows success state after successful reset', async () => {
      mockPost.mockResolvedValueOnce({ data: { success: true } })
      renderWithToken()

      const passwordFields = screen.getAllByLabelText(/new password/i)
      const newPw = passwordFields[0]
      const confirmPw = screen.getByLabelText(/confirm new password/i)

      fireEvent.change(newPw, { target: { value: 'ValidPassword1234!' } })
      fireEvent.change(confirmPw, { target: { value: 'ValidPassword1234!' } })

      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      fireEvent.click(resetBtn)

      await waitFor(() => {
        expect(screen.getByText('Password Reset Successful')).toBeInTheDocument()
        expect(screen.getByText(/your password has been updated/i)).toBeInTheDocument()
      })
    })

    it('shows API error on failed reset', async () => {
      mockPost.mockRejectedValueOnce({
        response: { data: { error: 'Token has expired' } },
      })
      renderWithToken()

      const passwordFields = screen.getAllByLabelText(/new password/i)
      const newPw = passwordFields[0]
      const confirmPw = screen.getByLabelText(/confirm new password/i)

      fireEvent.change(newPw, { target: { value: 'ValidPassword1234!' } })
      fireEvent.change(confirmPw, { target: { value: 'ValidPassword1234!' } })

      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => /reset password/i.test(b.textContent) && b.type === 'submit')
      fireEvent.click(resetBtn)

      await waitFor(() => {
        expect(screen.getByText('Token has expired')).toBeInTheDocument()
      })
    })

    it('renders Back to Login link', () => {
      renderWithToken()
      const backLinks = screen.getAllByText('Back to Login')
      const link = backLinks[0].closest('a')
      expect(link).toHaveAttribute('href', '/login')
    })
  })

  describe('without token', () => {
    it('shows invalid reset link message when token is missing', () => {
      renderWithToken(null)
      expect(screen.getByText('Invalid Reset Link')).toBeInTheDocument()
      expect(screen.getByText(/this password reset link is invalid or missing a token/i)).toBeInTheDocument()
    })

    it('renders request new reset link button when token is missing', () => {
      renderWithToken(null)
      const requestLink = screen.getByText('Request New Reset Link')
      expect(requestLink).toBeInTheDocument()
      expect(requestLink.closest('a')).toHaveAttribute('href', '/forgot-password')
    })

    it('does not show the password form when token is missing', () => {
      renderWithToken(null)
      expect(screen.queryByLabelText(/confirm new password/i)).not.toBeInTheDocument()
    })
  })
})
