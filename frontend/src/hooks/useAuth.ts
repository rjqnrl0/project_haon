import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import { useUIStore } from '../stores/uiStore'

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const logout = useAuthStore((s) => s.logout)
  const showToast = useUIStore((s) => s.showToast)
  const navigate = useNavigate()

  const signUp = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const { data } = await api.post('/auth/signup', { email, password })
      localStorage.setItem('refreshToken', data.refresh_token)
      setAuth(data.user, data.access_token)
      navigate('/face-id/register')
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '회원가입 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('refreshToken', data.refresh_token)
      setAuth(data.user, data.access_token)

      if (!data.user.face_registered) {
        navigate('/face-id/register')
      } else {
        navigate('/fitting')
      }
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '로그인 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // logout even if API fails
    }
    logout()
    navigate('/login')
  }

  return { signUp, login, logout: handleLogout, isLoading }
}
