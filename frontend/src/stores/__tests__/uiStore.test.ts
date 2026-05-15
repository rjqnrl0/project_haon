import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useUIStore } from '../uiStore'

describe('uiStore', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    useUIStore.setState({ isLoading: false, toast: null })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('initial state', () => {
    const state = useUIStore.getState()
    expect(state.isLoading).toBe(false)
    expect(state.toast).toBeNull()
  })

  it('setLoading updates loading state', () => {
    useUIStore.getState().setLoading(true)
    expect(useUIStore.getState().isLoading).toBe(true)

    useUIStore.getState().setLoading(false)
    expect(useUIStore.getState().isLoading).toBe(false)
  })

  it('showToast sets toast message', () => {
    useUIStore.getState().showToast({ type: 'success', message: 'Done!' })
    const state = useUIStore.getState()
    expect(state.toast).toEqual({ type: 'success', message: 'Done!' })
  })

  it('showToast auto-clears after 3 seconds', () => {
    useUIStore.getState().showToast({ type: 'error', message: 'Failed' })
    expect(useUIStore.getState().toast).not.toBeNull()

    vi.advanceTimersByTime(3000)
    expect(useUIStore.getState().toast).toBeNull()
  })

  it('hideToast clears toast immediately', () => {
    useUIStore.getState().showToast({ type: 'warning', message: 'Warning' })
    useUIStore.getState().hideToast()
    expect(useUIStore.getState().toast).toBeNull()
  })
})
