import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { SignupPage } from '../SignupPage'

vi.mock('../../../hooks/useAuth', () => ({
  useAuth: () => ({
    signUp: vi.fn(),
    isLoading: false,
  }),
}))

function renderSignupPage() {
  return render(
    <MemoryRouter>
      <SignupPage />
    </MemoryRouter>
  )
}

describe('SignupPage', () => {
  it('renders all form fields', () => {
    renderSignupPage()
    expect(screen.getByTestId('signup-email-input')).toBeInTheDocument()
    expect(screen.getByTestId('signup-password-input')).toBeInTheDocument()
    expect(screen.getByTestId('signup-confirm-password-input')).toBeInTheDocument()
  })

  it('renders submit button', () => {
    renderSignupPage()
    expect(screen.getByTestId('signup-submit-button')).toHaveTextContent('회원가입')
  })

  it('shows error when password too short', async () => {
    renderSignupPage()
    await userEvent.type(screen.getByTestId('signup-email-input'), 'test@test.com')
    await userEvent.type(screen.getByTestId('signup-password-input'), 'short')
    await userEvent.type(screen.getByTestId('signup-confirm-password-input'), 'short')
    await userEvent.click(screen.getByTestId('signup-submit-button'))

    expect(screen.getByText('비밀번호는 8자 이상이어야 합니다')).toBeInTheDocument()
  })

  it('shows error when passwords do not match', async () => {
    renderSignupPage()
    await userEvent.type(screen.getByTestId('signup-email-input'), 'test@test.com')
    await userEvent.type(screen.getByTestId('signup-password-input'), 'password123!')
    await userEvent.type(screen.getByTestId('signup-confirm-password-input'), 'different123!')
    await userEvent.click(screen.getByTestId('signup-submit-button'))

    expect(screen.getByText('비밀번호가 일치하지 않습니다')).toBeInTheDocument()
  })

  it('renders login link', () => {
    renderSignupPage()
    expect(screen.getByText('로그인')).toBeInTheDocument()
  })
})
