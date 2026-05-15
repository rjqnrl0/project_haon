import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { RecommendPage } from '../RecommendPage'

vi.mock('../../../lib/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

vi.mock('../../../stores/uiStore', () => ({
  useUIStore: () => vi.fn(),
}))

function renderRecommendPage() {
  return render(
    <MemoryRouter>
      <RecommendPage />
    </MemoryRouter>
  )
}

describe('RecommendPage', () => {
  it('renders weather and size tab buttons', () => {
    renderRecommendPage()
    expect(screen.getByTestId('recommend-weather-tab')).toBeInTheDocument()
    expect(screen.getByTestId('recommend-size-tab')).toBeInTheDocument()
  })

  it('weather tab is active by default', () => {
    renderRecommendPage()
    expect(screen.getByTestId('recommend-city-input')).toBeInTheDocument()
  })

  it('shows city input in weather tab', () => {
    renderRecommendPage()
    const input = screen.getByTestId('recommend-city-input')
    expect(input).toHaveAttribute('placeholder', '여행지를 입력하세요')
  })

  it('submit button is disabled when city is empty', () => {
    renderRecommendPage()
    const button = screen.getByTestId('recommend-weather-submit')
    expect(button).toBeDisabled()
  })

  it('submit button becomes enabled when city is entered', async () => {
    renderRecommendPage()
    await userEvent.type(screen.getByTestId('recommend-city-input'), 'Tokyo')
    const button = screen.getByTestId('recommend-weather-submit')
    expect(button).not.toBeDisabled()
  })

  it('switching to size tab shows guidance message', async () => {
    renderRecommendPage()
    await userEvent.click(screen.getByTestId('recommend-size-tab'))
    expect(screen.getByText(/피팅 결과 페이지에서/)).toBeInTheDocument()
  })
})
