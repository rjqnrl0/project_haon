import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { LoginPage } from '../LoginPage'

vi.mock('../../../hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    isLoading: false,
  }),
}))

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  )
}

describe('LoginPage', () => {
  it('renders email and password inputs', () => {
    renderLoginPage()
    expect(screen.getByTestId('login-email-input')).toBeInTheDocument()
    expect(screen.getByTestId('login-password-input')).toBeInTheDocument()
  })

  it('renders submit button', () => {
    renderLoginPage()
    expect(screen.getByTestId('login-submit-button')).toBeInTheDocument()
    expect(screen.getByTestId('login-submit-button')).toHaveTextContent('로그인')
  })

  it('renders signup link', () => {
    renderLoginPage()
    expect(screen.getByText('회원가입')).toBeInTheDocument()
  })

  it('allows typing in email field', async () => {
    renderLoginPage()
    const emailInput = screen.getByTestId('login-email-input')
    await userEvent.type(emailInput, 'test@example.com')
    expect(emailInput).toHaveValue('test@example.com')
  })

  it('allows typing in password field', async () => {
    renderLoginPage()
    const passwordInput = screen.getByTestId('login-password-input')
    await userEvent.type(passwordInput, 'secret123')
    expect(passwordInput).toHaveValue('secret123')
  })
})
