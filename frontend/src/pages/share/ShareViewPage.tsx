import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../lib/api'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'

export function ShareViewPage() {
  const { shareToken } = useParams()
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [isExpired, setIsExpired] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchShare() {
      try {
        const { data } = await api.get(`/share/${shareToken}`)
        setImageUrl(data.image_url)
      } catch (err: any) {
        if (err.response?.status === 404) {
          setIsExpired(true)
        }
      } finally {
        setIsLoading(false)
      }
    }
    fetchShare()
  }, [shareToken])

  if (isLoading) return <LoadingSpinner />

  if (isExpired) {
    return (
      <div className="text-center space-y-4">
        <h2 className="text-xl font-bold text-gray-900">링크 만료</h2>
        <p className="text-gray-500">이 공유 링크는 만료되었습니다</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-center">
      <h2 className="text-xl font-bold text-gray-900">V-Suitcase 피팅 결과</h2>
      {imageUrl && (
        <img src={imageUrl} alt="공유된 피팅 결과" className="max-w-sm mx-auto rounded-lg shadow-lg" />
      )}
      <a
        href="/"
        className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        V-Suitcase에서 나도 해보기
      </a>
    </div>
  )
}
