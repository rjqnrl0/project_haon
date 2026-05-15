import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from '../authStore'

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    })
  })

  it('initial state is unauthenticated', () => {
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('setAuth stores user and token', () => {
    const user = { id: '1', email: 'test@test.com', faceRegistered: false }
    useAuthStore.getState().setAuth(user, 'token-123')

    const state = useAuthStore.getState()
    expect(state.user).toEqual(user)
    expect(state.accessToken).toBe('token-123')
    expect(state.isAuthenticated).toBe(true)
  })

  it('logout clears all state', () => {
    const removeItem = vi.spyOn(Storage.prototype, 'removeItem')
    const user = { id: '1', email: 'test@test.com', faceRegistered: true }
    useAuthStore.getState().setAuth(user, 'token-123')

    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(removeItem).toHaveBeenCalledWith('refreshToken')
    removeItem.mockRestore()
  })

  it('setAccessToken updates token only', () => {
    const user = { id: '1', email: 'test@test.com', faceRegistered: false }
    useAuthStore.getState().setAuth(user, 'old-token')
    useAuthStore.getState().setAccessToken('new-token')

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('new-token')
    expect(state.user).toEqual(user)
    expect(state.isAuthenticated).toBe(true)
  })
})
