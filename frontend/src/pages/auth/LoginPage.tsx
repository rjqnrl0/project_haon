import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading } = useAuth()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    login(email, password)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center text-gray-900">로그인</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">이메일</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="email@example.com"
          required
          data-testid="login-email-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">비밀번호</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="비밀번호"
          required
          data-testid="login-password-input"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        data-testid="login-submit-button"
      >
        {isLoading ? '로그인 중...' : '로그인'}
      </button>

      <p className="text-center text-sm text-gray-500">
        계정이 없으신가요?{' '}
        <Link to="/signup" className="text-blue-600 hover:underline">
          회원가입
        </Link>
      </p>
    </form>
  )
}
