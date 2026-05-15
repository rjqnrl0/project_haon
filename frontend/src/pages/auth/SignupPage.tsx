import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const { signUp, isLoading } = useAuth()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('비밀번호는 8자 이상이어야 합니다')
      return
    }
    if (password !== confirmPassword) {
      setError('비밀번호가 일치하지 않습니다')
      return
    }

    signUp(email, password)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center text-gray-900">회원가입</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">이메일</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="email@example.com"
          required
          data-testid="signup-email-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">비밀번호</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="8자 이상, 영문+숫자+특수문자"
          required
          data-testid="signup-password-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">비밀번호 확인</label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="비밀번호 재입력"
          required
          data-testid="signup-confirm-password-input"
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        data-testid="signup-submit-button"
      >
        {isLoading ? '가입 중...' : '회원가입'}
      </button>

      <p className="text-center text-sm text-gray-500">
        이미 계정이 있으신가요?{' '}
        <Link to="/login" className="text-blue-600 hover:underline">
          로그인
        </Link>
      </p>
    </form>
  )
}
