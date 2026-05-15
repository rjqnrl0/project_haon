import { useState } from 'react'
import api from '../../lib/api'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'
import { useUIStore } from '../../stores/uiStore'
import { POPULAR_CITIES } from '../../constants'

export function RecommendPage() {
  const [tab, setTab] = useState<'size' | 'weather'>('weather')
  const [city, setCity] = useState('')
  const [suggestions, setSuggestions] = useState<typeof POPULAR_CITIES[number][]>([])
  const [weatherResult, setWeatherResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const showToast = useUIStore((s) => s.showToast)

  const handleCityChange = (value: string) => {
    setCity(value)
    if (value.length > 0) {
      const filtered = POPULAR_CITIES.filter(
        (c) => c.nameKo.includes(value) || c.nameEn.toLowerCase().includes(value.toLowerCase())
      )
      setSuggestions(filtered)
    } else {
      setSuggestions([])
    }
  }

  const getWeatherCodi = async (cityName?: string) => {
    const target = cityName || city
    if (!target.trim()) return
    setIsLoading(true)
    try {
      const { data } = await api.post('/recommend/weather', { city: target })
      setWeatherResult(data)
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '추천 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) return <LoadingSpinner message="추천을 생성하고 있어요..." />

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">AI 추천</h2>

      <div className="flex gap-2">
        <button
          onClick={() => setTab('weather')}
          className={`px-4 py-2 rounded-lg ${tab === 'weather' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          data-testid="recommend-weather-tab"
        >
          날씨 코디
        </button>
        <button
          onClick={() => setTab('size')}
          className={`px-4 py-2 rounded-lg ${tab === 'size' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          data-testid="recommend-size-tab"
        >
          사이즈 추천
        </button>
      </div>

      {tab === 'weather' && (
        <div className="space-y-4">
          <div className="relative">
            <input
              value={city}
              onChange={(e) => handleCityChange(e.target.value)}
              placeholder="여행지를 입력하세요"
              className="w-full px-3 py-2 border rounded-lg"
              data-testid="recommend-city-input"
            />
            {suggestions.length > 0 && (
              <ul className="absolute z-10 w-full bg-white border rounded-lg mt-1 shadow-lg max-h-40 overflow-y-auto">
                {suggestions.map((s) => (
                  <li
                    key={s.nameEn}
                    className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                    onClick={() => { setCity(s.nameEn); setSuggestions([]) }}
                  >
                    {s.nameKo} ({s.nameEn})
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {POPULAR_CITIES.slice(0, 5).map((c) => (
              <button
                key={c.nameEn}
                onClick={() => { setCity(c.nameEn); getWeatherCodi(c.nameEn) }}
                className="px-3 py-1 text-sm bg-gray-100 rounded-full hover:bg-gray-200"
              >
                {c.nameKo}
              </button>
            ))}
          </div>

          <button onClick={() => getWeatherCodi()} disabled={!city} className="w-full py-2 bg-green-600 text-white rounded-lg disabled:opacity-50" data-testid="recommend-weather-submit">
            코디 추천 받기
          </button>

          {weatherResult && (
            <div className="bg-white rounded-lg border p-4 space-y-3">
              <h3 className="font-bold text-lg">{weatherResult.city} 날씨 코디</h3>
              <p className="text-gray-700">{weatherResult.codi_advice}</p>
              <div>
                <h4 className="font-medium text-sm text-gray-500">필수 아이템</h4>
                <div className="flex flex-wrap gap-2 mt-1">
                  {weatherResult.essential_items?.map((item: string) => (
                    <span key={item} className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-sm text-gray-500">{weatherResult.additional_tips}</p>
            </div>
          )}
        </div>
      )}

      {tab === 'size' && (
        <div className="bg-white rounded-lg border p-4">
          <p className="text-gray-500 text-center">피팅 결과 페이지에서 "사이즈 추천" 버튼을 눌러주세요</p>
        </div>
      )}
    </div>
  )
}
