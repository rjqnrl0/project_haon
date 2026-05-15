import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

export function FaceIDGuard() {
  const user = useAuthStore((s) => s.user)

  if (user && !user.faceRegistered) {
    return <Navigate to="/face-id/register" replace />
  }

  return <Outlet />
}
