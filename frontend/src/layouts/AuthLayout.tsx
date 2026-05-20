import { Outlet, NavLink, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export function AuthLayout() {
  const logout = useAuthStore((s) => s.logout)

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors">H-Suitcase</Link>
          <nav className="hidden md:flex gap-6">
            <NavLink to="/fitting" className={({ isActive }) => isActive ? 'text-blue-600 font-medium' : 'text-gray-600'}>
              피팅
            </NavLink>
            <NavLink to="/recommend" className={({ isActive }) => isActive ? 'text-blue-600 font-medium' : 'text-gray-600'}>
              추천
            </NavLink>
          </nav>
          <button
            onClick={logout}
            className="text-sm text-gray-500 hover:text-gray-700"
            data-testid="auth-layout-logout-button"
          >
            로그아웃
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 bg-white border-t flex justify-around py-2">
        <NavLink to="/fitting" className={({ isActive }) => isActive ? 'text-blue-600' : 'text-gray-400'}>
          피팅
        </NavLink>
        <NavLink to="/recommend" className={({ isActive }) => isActive ? 'text-blue-600' : 'text-gray-400'}>
          추천
        </NavLink>
      </nav>
    </div>
  )
}
