import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'
import type { DutyFreeProduct } from '../../types'

export function FittingResultPage() {
  const { resultId } = useParams()
  const navigate = useNavigate()
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [clothingInfo, setClothingInfo] = useState<DutyFreeProduct[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchResult() {
      try {
        const { data } = await api.get(`/fitting/result/${resultId}`)
        setResultUrl(data.result_url)
        if (data.clothing_info) {
          setClothingInfo(data.clothing_info)
        }
      } catch {
        // handle error
      } finally {
        setIsLoading(false)
      }
    }
    fetchResult()
  }, [resultId])

  const formatPrice = (price: number) => price.toLocaleString('ko-KR') + '원'

  if (isLoading) return <LoadingSpinner message="결과를 불러오는 중..." />

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">피팅 결과</h2>

      {resultUrl && (
        <div className="flex justify-center">
          <img src={resultUrl} alt="피팅 결과" className="max-w-lg rounded-lg shadow-lg" />
        </div>
      )}

      {clothingInfo.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">착용 의류 정보</h4>
          <div className="grid gap-3">
            {clothingInfo.map((item) => (
              <div key={item.id} className="flex gap-3 p-3 bg-white border rounded-xl">
                <img src={item.imageUrl} alt={item.name} className="w-16 h-16 object-cover rounded-lg" />
                <div className="flex-1">
                  <p className="text-xs text-gray-500">{item.brand}</p>
                  <p className="font-medium text-sm">{item.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs line-through text-gray-400">{formatPrice(item.price)}</span>
                    <span className="text-sm font-bold text-red-600">{formatPrice(item.discountPrice)}</span>
                    <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">15% OFF</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <a
            href="https://kor.lottedfs.com"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-xl font-bold text-center text-lg hover:from-red-600 hover:to-pink-600 shadow-lg"
          >
            🎁 이 착장 그대로 면세점에서 15% 할인받기
          </a>
        </div>
      )}

      <div className="flex flex-wrap gap-3 justify-center">
        <button
          onClick={() => navigate(`/background/${resultId}`)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          배경 변경
        </button>
        <button
          onClick={() => navigate('/fitting')}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
        >
          다시 피팅
        </button>
      </div>
    </div>
  )
}
