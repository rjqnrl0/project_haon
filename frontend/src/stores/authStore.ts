import { create } from 'zustand'
import type { User } from '../types'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, accessToken: string) => void
  logout: () => void
  setAccessToken: (token: string) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  setAuth: (user, accessToken) => {
    set({ user, accessToken, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('refreshToken')
    set({ user: null, accessToken: null, isAuthenticated: false })
  },

  setAccessToken: (token) => {
    set({ accessToken: token })
  },
}))
