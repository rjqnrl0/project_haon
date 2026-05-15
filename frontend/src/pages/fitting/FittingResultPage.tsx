import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'

export function FittingResultPage() {
  const { resultId } = useParams()
  const navigate = useNavigate()
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchResult() {
      try {
        const { data } = await api.get(`/fitting/result/${resultId}`)
        setResultUrl(data.result_url)
      } catch {
        // handle error
      } finally {
        setIsLoading(false)
      }
    }
    fetchResult()
  }, [resultId])

  if (isLoading) return <LoadingSpinner message="결과를 불러오는 중..." />

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">피팅 결과</h2>

      {resultUrl && (
        <div className="flex justify-center">
          <img src={resultUrl} alt="피팅 결과" className="max-w-lg rounded-lg shadow-lg" />
        </div>
      )}

      <div className="flex flex-wrap gap-3 justify-center">
        <button
          onClick={() => navigate(`/background/${resultId}`)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          data-testid="fitting-result-background-button"
        >
          배경 변경
        </button>
        <button
          onClick={() => navigate(`/recommend`)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          data-testid="fitting-result-recommend-button"
        >
          사이즈 추천
        </button>
        <button
          onClick={() => navigate('/fitting')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          data-testid="fitting-result-retry-button"
        >
          다시 피팅
        </button>
      </div>
    </div>
  )
}
