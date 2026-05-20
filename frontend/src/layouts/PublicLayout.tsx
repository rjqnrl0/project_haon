import { Outlet, Link } from 'react-router-dom'

export function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="mb-8">
        <Link to="/" className="text-3xl font-bold text-gray-900 hover:text-blue-600 transition-colors">H-Suitcase</Link>
      </div>
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
        <Outlet />
      </div>
      <footer className="mt-8 text-sm text-gray-400">
        &copy; 2026 H-Suitcase
      </footer>
    </div>
  )
}
