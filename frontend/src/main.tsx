import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import axios from 'axios'
import { useAuthStore } from './stores/authStore'

async function initAuth() {
  const refreshToken = localStorage.getItem('refreshToken')
  if (!refreshToken) return

  try {
    const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
    const user = {
      id: data.user.id,
      email: data.user.email,
      faceRegistered: data.user.face_registered,
    }
    useAuthStore.getState().setAuth(user, data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
  } catch {
    localStorage.removeItem('refreshToken')
  }
}

initAuth().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>,
  )
})
