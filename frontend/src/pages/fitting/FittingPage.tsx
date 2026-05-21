import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { FileUpload } from '../../components/common/FileUpload'
import { ImagePreview } from '../../components/common/ImagePreview'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'
import { useUIStore } from '../../stores/uiStore'
import { DUTY_FREE_PRODUCTS } from '../../constants'
import { DESTINATIONS } from '../../constants/destinations'
import type { DutyFreeProduct, Attraction } from '../../types'
import api from '../../lib/api'

type Mode = 'select' | 'ai-recommend'
type Step = 'destination' | 'mode' | 'clothing' | 'attraction' | 'photo' | 'result'

interface FittingResult {
  task_id: string
  result_url: string
  clothing_info: DutyFreeProduct[]
}

export function FittingPage() {
  const [searchParams] = useSearchParams()
  const arrival = searchParams.get('arrival') || ''
  const initialDestination = searchParams.get('destination') || ''

  const [step, setStep] = useState<Step>('destination')
  const [destination, setDestination] = useState(initialDestination)
  const [mode, setMode] = useState<Mode | null>(null)
  const [selectedProducts, setSelectedProducts] = useState<DutyFreeProduct[]>([])
  const [aiRecommendation, setAiRecommendation] = useState<{ items: DutyFreeProduct[]; advice: string } | null>(null)
  const [attractions, setAttractions] = useState<Attraction[]>([])
  const [selectedAttraction, setSelectedAttraction] = useState<Attraction | null>(null)
  const [bodyImageId, setBodyImageId] = useState<string | null>(null)
  const [bodyPreview, setBodyPreview] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [fittingProgress, setFittingProgress] = useState(0)
  const [fittingStage, setFittingStage] = useState('')
  const [isFittingInProgress, setIsFittingInProgress] = useState(false)
  const progressTimer = useRef<ReturnType<typeof setInterval> | null>(null)
  const [fittingResult, setFittingResult] = useState<FittingResult | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [weatherInfo, setWeatherInfo] = useState<{ temp: number; condition: string; description: string; city: string } | null>(null)
  const showToast = useUIStore((s) => s.showToast)

  const FITTING_STAGES = [
    { at: 0, msg: '전신 사진을 분석하고 있어요...' },
    { at: 10, msg: '인물 특징을 파악하고 있어요...' },
    { at: 20, msg: '선택한 의류를 준비하고 있어요...' },
    { at: 35, msg: 'AI가 의류를 피팅하고 있어요...' },
    { at: 55, msg: '배경을 분석하고 있어요...' },
    { at: 70, msg: '관광지 배경을 합성하고 있어요...' },
    { at: 85, msg: '최종 결과를 생성하고 있어요...' },
    { at: 95, msg: '거의 완료됐어요!' },
  ]

  const startFittingProgress = () => {
    setIsFittingInProgress(true)
    setFittingProgress(0)
    setFittingStage(FITTING_STAGES[0].msg)
    let current = 0
    progressTimer.current = setInterval(() => {
      current += 1
      if (current >= 95) {
        current = 95
      }
      setFittingProgress(current)
      const stage = [...FITTING_STAGES].reverse().find((s) => current >= s.at)
      if (stage) setFittingStage(stage.msg)
    }, 800)
  }

  const stopFittingProgress = () => {
    if (progressTimer.current) {
      clearInterval(progressTimer.current)
      progressTimer.current = null
    }
    setFittingProgress(100)
    setFittingStage('완료!')
    setTimeout(() => setIsFittingInProgress(false), 500)
  }

  useEffect(() => {
    return () => {
      if (progressTimer.current) clearInterval(progressTimer.current)
    }
  }, [])

  const selectedDest = DESTINATIONS.find((d) => d.id === destination)
  const destinationLabel = selectedDest?.nameKo || destination

  const fetchWeather = async (dest: string) => {
    try {
      const { data } = await api.post('/recommend/weather-simple', { destination: dest, arrival })
      setWeatherInfo(data)
    } catch {
      // 날씨 조회 실패해도 플로우에 영향 없음
    }
  }

  const handleModeSelect = async (selectedMode: Mode) => {
    setMode(selectedMode)
    if (selectedMode === 'ai-recommend') {
      setIsLoading(true)
      setLoadingMessage('AI가 날씨와 여행지에 맞는 코디를 추천하고 있어요...')
      try {
        const { data } = await api.post('/recommend/dutyfree-codi', { destination, arrival })
        const items = data.recommended_items.map((p: any) => ({
          id: p.id,
          brand: p.brand,
          name: p.name,
          category: p.category,
          price: p.price,
          discountPrice: p.discount_price || p.discountPrice,
          imageUrl: p.image_url || p.imageUrl,
          description: p.description,
        }))
        setAiRecommendation({ items, advice: data.codi_advice })
        setSelectedProducts(items)
      } catch (err: any) {
        showToast({ type: 'error', message: err.response?.data?.detail || 'AI 추천 실패' })
        setStep('mode')
        return
      } finally {
        setIsLoading(false)
      }
    }
    setStep('clothing')
  }

  const handleClothingNext = async () => {
    if (selectedProducts.length === 0) {
      showToast({ type: 'error', message: '의류를 1개 이상 선택해주세요' })
      return
    }
    setIsLoading(true)
    setLoadingMessage(`${destinationLabel}의 인기 관광지를 찾고 있어요...`)
    try {
      const { data } = await api.post('/recommend/attractions', { destination })
      setAttractions(data.attractions.map((a: any) => ({
        name: a.name,
        nameKo: a.name_ko || a.nameKo,
        description: a.description,
        imageKeyword: a.image_keyword || a.imageKeyword,
      })))
    } catch {
      const fallbackAttractions: Record<string, Attraction[]> = {
        'tokyo': [
          { name: 'Shibuya Crossing', nameKo: '시부야 교차로', description: '세계에서 가장 붐비는 교차로', imageKeyword: 'shibuya crossing tokyo' },
          { name: 'Tokyo Tower', nameKo: '도쿄 타워', description: '도쿄의 상징적 타워', imageKeyword: 'tokyo tower' },
          { name: 'Senso-ji Temple', nameKo: '센소지', description: '아사쿠사의 역사적 사찰', imageKeyword: 'sensoji temple' },
          { name: 'Meiji Shrine', nameKo: '메이지 신궁', description: '도심 속 신사', imageKeyword: 'meiji shrine tokyo' },
          { name: 'Akihabara', nameKo: '아키하바라', description: '팝컬처의 거리', imageKeyword: 'akihabara tokyo' },
        ],
        'bangkok': [
          { name: 'Grand Palace', nameKo: '왕궁', description: '태국 왕실 궁전', imageKeyword: 'grand palace bangkok' },
          { name: 'Wat Arun', nameKo: '왓 아룬', description: '새벽의 사원', imageKeyword: 'wat arun bangkok' },
          { name: 'Khao San Road', nameKo: '카오산 로드', description: '여행자의 거리', imageKeyword: 'khao san road' },
          { name: 'Chatuchak Market', nameKo: '짜뚜짝 시장', description: '세계 최대 주말 시장', imageKeyword: 'chatuchak market' },
          { name: 'Wat Pho', nameKo: '왓 포', description: '와불이 있는 사원', imageKeyword: 'wat pho bangkok' },
        ],
        'paris': [
          { name: 'Eiffel Tower', nameKo: '에펠탑', description: '파리의 상징', imageKeyword: 'eiffel tower' },
          { name: 'Louvre Museum', nameKo: '루브르 박물관', description: '세계 최대 미술관', imageKeyword: 'louvre' },
          { name: 'Champs-Élysées', nameKo: '샹젤리제', description: '파리의 대표 거리', imageKeyword: 'champs elysees' },
          { name: 'Montmartre', nameKo: '몽마르뜨', description: '예술가의 언덕', imageKeyword: 'montmartre' },
          { name: 'Seine River', nameKo: '센강', description: '파리를 가로지르는 강', imageKeyword: 'seine river' },
        ],
        'london': [
          { name: 'Big Ben', nameKo: '빅벤', description: '영국 국회의사당 시계탑', imageKeyword: 'big ben london' },
          { name: 'Tower Bridge', nameKo: '타워 브리지', description: '런던의 상징적 다리', imageKeyword: 'tower bridge london' },
          { name: 'Buckingham Palace', nameKo: '버킹엄 궁전', description: '영국 왕실 궁전', imageKeyword: 'buckingham palace' },
          { name: 'London Eye', nameKo: '런던 아이', description: '템즈강변 대관람차', imageKeyword: 'london eye' },
          { name: 'Hyde Park', nameKo: '하이드 파크', description: '런던 중심부 공원', imageKeyword: 'hyde park london' },
        ],
        'new york': [
          { name: 'Times Square', nameKo: '타임스 스퀘어', description: '뉴욕의 화려한 중심지', imageKeyword: 'times square new york' },
          { name: 'Central Park', nameKo: '센트럴 파크', description: '맨해튼의 거대한 공원', imageKeyword: 'central park new york' },
          { name: 'Statue of Liberty', nameKo: '자유의 여신상', description: '미국의 상징', imageKeyword: 'statue of liberty' },
          { name: 'Brooklyn Bridge', nameKo: '브루클린 브리지', description: '역사적인 현수교', imageKeyword: 'brooklyn bridge new york' },
          { name: 'Empire State Building', nameKo: '엠파이어 스테이트 빌딩', description: '뉴욕 스카이라인의 아이콘', imageKeyword: 'empire state building' },
        ],
        'bali': [
          { name: 'Tanah Lot Temple', nameKo: '따나롯 사원', description: '바다 위 절벽 사원', imageKeyword: 'tanah lot bali' },
          { name: 'Ubud Rice Terraces', nameKo: '우붓 라이스 테라스', description: '초록빛 계단식 논', imageKeyword: 'rice terrace bali' },
          { name: 'Uluwatu Temple', nameKo: '울루와뚜 사원', description: '절벽 위 힌두 사원', imageKeyword: 'uluwatu temple bali' },
          { name: 'Kuta Beach', nameKo: '쿠타 비치', description: '발리 대표 해변', imageKeyword: 'kuta beach bali' },
          { name: 'Sacred Monkey Forest', nameKo: '몽키 포레스트', description: '원숭이와 고대 사원의 숲', imageKeyword: 'monkey forest ubud' },
        ],
      }
      setAttractions(fallbackAttractions[destination] || fallbackAttractions['paris'])
    } finally {
      setIsLoading(false)
      setStep('attraction')
    }
  }

  const handleAttractionNext = () => {
    if (!selectedAttraction) {
      showToast({ type: 'error', message: '관광지를 선택해주세요' })
      return
    }
    setStep('photo')
  }

  const handleBodyUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post('/fitting/body/upload', formData)
      setBodyImageId(data.task_id)
      setBodyPreview(URL.createObjectURL(file))
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '업로드 실패' })
    }
  }

  const handleExecuteFitting = async () => {
    if (!bodyImageId || !selectedAttraction) return

    startFittingProgress()

    const clothingUploadIds: string[] = []
    for (const product of selectedProducts) {
      try {
        const imgResp = await fetch(product.imageUrl)
        const blob = await imgResp.blob()
        const formData = new FormData()
        formData.append('file', blob, `${product.id}.jpg`)
        formData.append('category', product.category)
        const { data } = await api.post('/fitting/clothing/upload', formData)
        clothingUploadIds.push(data.clothing_id)
      } catch (err) {
        showToast({ type: 'error', message: `의류 업로드 실패: ${product.name}` })
      }
    }

    try {
      const { data } = await api.post('/fitting/execute-with-background', {
        body_image_id: bodyImageId,
        clothing_ids: clothingUploadIds,
        product_ids: selectedProducts.map((p) => p.id),
        attraction: selectedAttraction.name,
        destination,
      })
      const clothingInfo = (data.clothing_info || []).map((p: any) => ({
        id: p.id,
        brand: p.brand,
        name: p.name,
        category: p.category,
        price: p.price,
        discountPrice: p.discount_price || p.discountPrice,
        imageUrl: p.image_url || p.imageUrl,
        description: p.description,
      }))
      stopFittingProgress()
      setFittingResult({
        task_id: data.task_id,
        result_url: data.result_url,
        clothing_info: clothingInfo.length > 0 ? clothingInfo : selectedProducts,
      })
      setStep('result')
    } catch (err: any) {
      stopFittingProgress()
      showToast({ type: 'error', message: err.response?.data?.detail || '피팅 실행 실패' })
    }
  }

  const formatPrice = (price: number) => price.toLocaleString('ko-KR') + '원'

  const filteredProducts = categoryFilter === 'all'
    ? DUTY_FREE_PRODUCTS
    : DUTY_FREE_PRODUCTS.filter((p) => p.category === categoryFilter)

  const toggleProduct = (product: DutyFreeProduct) => {
    setSelectedProducts((prev) => {
      const exists = prev.find((p) => p.id === product.id)
      if (exists) return prev.filter((p) => p.id !== product.id)
      if (prev.length >= 3) {
        showToast({ type: 'error', message: '최대 3개까지 선택 가능합니다' })
        return prev
      }
      return [...prev, product]
    })
  }

  if (isFittingInProgress) {
    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-6">
        <div className="w-16 h-16 relative">
          <div className="absolute inset-0 border-4 border-blue-100 rounded-full" />
          <div
            className="absolute inset-0 border-4 border-blue-600 rounded-full animate-spin"
            style={{ borderTopColor: 'transparent', borderRightColor: 'transparent' }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold text-blue-600">{fittingProgress}%</span>
          </div>
        </div>

        <div className="w-full max-w-sm">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${fittingProgress}%` }}
            />
          </div>
        </div>

        <p className="text-sm text-gray-600 animate-pulse">{fittingStage}</p>

        <p className="text-xs text-gray-400 mt-4">
          AI가 열심히 작업 중이에요. 약 30~60초 정도 소요됩니다.
        </p>
      </div>
    )
  }

  if (isLoading) {
    return <LoadingSpinner message={loadingMessage} />
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4">
        <h2 className="text-xl font-bold text-gray-800">H-Suitcase 가상 피팅</h2>
        <p className="text-sm text-gray-600 mt-1">
          {destination ? (
            <>여행지: <span className="font-semibold text-blue-700">{destinationLabel}</span></>
          ) : (
            <>여행지를 선택해주세요</>
          )}
          {arrival && (
            <> | 도착: <span className="font-semibold text-blue-700">{new Date(arrival).toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span></>
          )}
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-1 text-xs">
        {['여행지', '모드 선택', '의류 선택', '관광지', '전신 사진', '결과'].map((label, i) => {
          const steps: Step[] = ['destination', 'mode', 'clothing', 'attraction', 'photo', 'result']
          const isActive = steps.indexOf(step) >= i
          return (
            <div key={label} className="flex items-center gap-1">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isActive ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                {i + 1}
              </div>
              <span className={`hidden sm:inline ${isActive ? 'text-blue-700 font-medium' : 'text-gray-400'}`}>{label}</span>
              {i < 5 && <div className={`w-4 h-0.5 ${isActive ? 'bg-blue-600' : 'bg-gray-200'}`} />}
            </div>
          )
        })}
      </div>

      {/* Step: Destination Selection */}
      {step === 'destination' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">어디로 여행하시나요?</h3>
          <p className="text-sm text-gray-500">여행지에 맞는 코디와 배경을 추천해드려요</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {DESTINATIONS.map((dest) => (
              <button
                key={dest.id}
                onClick={() => {
                  setDestination(dest.id)
                  fetchWeather(dest.id)
                  setStep('mode')
                }}
                className="relative overflow-hidden rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all group"
              >
                <img
                  src={dest.imageUrl}
                  alt={dest.nameKo}
                  className="w-full h-32 object-cover group-hover:scale-105 transition-transform"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-3 text-white text-left">
                  <p className="text-lg font-bold">{dest.emoji} {dest.nameKo}</p>
                  <p className="text-xs opacity-80">{dest.nameEn}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step: Mode Selection */}
      {step === 'mode' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">어떤 방법으로 피팅해볼까요?</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <button
              onClick={() => handleModeSelect('select')}
              className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
            >
              <div className="text-2xl mb-2">🛍️</div>
              <h4 className="font-bold text-lg">면세점 의류 직접 선택</h4>
              <p className="text-sm text-gray-500 mt-1">면세점 인기 의류 중에서 직접 골라 가상 피팅해보세요</p>
            </button>
            <button
              onClick={() => handleModeSelect('ai-recommend')}
              className="p-6 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-all text-left"
            >
              <div className="text-2xl mb-2">✨</div>
              <h4 className="font-bold text-lg">AI 코디 추천</h4>
              <p className="text-sm text-gray-500 mt-1">{destinationLabel} 날씨에 맞는 코디를 AI가 추천해드려요</p>
            </button>
          </div>
        </div>
      )}

      {/* Step: Clothing Selection (Manual) */}
      {step === 'clothing' && mode === 'select' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">면세점 의류 선택 <span className="text-sm font-normal text-gray-500">(최대 3개)</span></h3>
            <button onClick={() => { setStep('mode'); setSelectedProducts([]) }} className="text-sm text-gray-500 hover:text-gray-700">← 뒤로</button>
          </div>

          {/* Weather Card */}
          {weatherInfo && (
            <div className="bg-gradient-to-r from-sky-50 to-blue-50 border border-sky-200 rounded-xl p-4 flex items-center gap-3">
              <span className="text-3xl">
                {weatherInfo.condition === 'Clear' ? '☀️' : weatherInfo.condition === 'Clouds' ? '☁️' : weatherInfo.condition === 'Rain' || weatherInfo.condition === 'Drizzle' ? '🌧️' : weatherInfo.condition === 'Snow' ? '❄️' : weatherInfo.condition === 'Thunderstorm' ? '⛈️' : '🌤️'}
              </span>
              <div>
                <p className="font-semibold text-gray-800">
                  {destinationLabel} <span className="text-blue-600">{weatherInfo.temp}°C</span> {weatherInfo.description}
                </p>
                <p className="text-xs text-gray-500">도착일 날씨 기준으로 의류를 선택해보세요</p>
              </div>
            </div>
          )}

          {/* Category Filter */}
          <div className="flex gap-2 flex-wrap">
            {[{ value: 'all', label: '전체' }, { value: 'top', label: '상의' }, { value: 'bottom', label: '하의' }, { value: 'outer', label: '아우터' }, { value: 'dress', label: '원피스' }].map((cat) => (
              <button
                key={cat.value}
                onClick={() => setCategoryFilter(cat.value)}
                className={`px-3 py-1.5 text-sm rounded-full ${categoryFilter === cat.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {filteredProducts.map((product) => {
              const isSelected = selectedProducts.some((p) => p.id === product.id)
              return (
                <button
                  key={product.id}
                  onClick={() => toggleProduct(product)}
                  className={`relative rounded-xl overflow-hidden border-2 transition-all ${isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <img src={product.imageUrl} alt={product.name} className="w-full h-40 object-cover" />
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-bold">✓</span>
                    </div>
                  )}
                  <div className="p-2">
                    <p className="text-xs text-gray-500 font-medium">{product.brand}</p>
                    <p className="text-sm font-medium truncate">{product.name}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-xs line-through text-gray-400">{formatPrice(product.price)}</span>
                      <span className="text-sm font-bold text-red-600">{formatPrice(product.discountPrice)}</span>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Selected Items Summary */}
          {selectedProducts.length > 0 && (
            <div className="sticky bottom-0 bg-white border-t p-4 -mx-4 rounded-t-xl shadow-lg">
              <div className="flex items-center gap-2 mb-2">
                {selectedProducts.map((p) => (
                  <div key={p.id} className="flex items-center gap-1 bg-blue-50 px-2 py-1 rounded-full text-xs">
                    <span>{p.brand}</span>
                    <button onClick={() => toggleProduct(p)} className="text-red-500 font-bold">×</button>
                  </div>
                ))}
              </div>
              <button
                onClick={handleClothingNext}
                className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
              >
                다음: 관광지 선택 ({selectedProducts.length}개 선택)
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step: AI Recommendation Result */}
      {step === 'clothing' && mode === 'ai-recommend' && aiRecommendation && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">AI 추천 코디</h3>
            <button onClick={() => { setStep('mode'); setSelectedProducts([]); setAiRecommendation(null) }} className="text-sm text-gray-500 hover:text-gray-700">← 뒤로</button>
          </div>

          {/* Weather Card */}
          {weatherInfo && (
            <div className="bg-gradient-to-r from-sky-50 to-blue-50 border border-sky-200 rounded-xl p-4 flex items-center gap-3">
              <span className="text-3xl">
                {weatherInfo.condition === 'Clear' ? '☀️' : weatherInfo.condition === 'Clouds' ? '☁️' : weatherInfo.condition === 'Rain' || weatherInfo.condition === 'Drizzle' ? '🌧️' : weatherInfo.condition === 'Snow' ? '❄️' : weatherInfo.condition === 'Thunderstorm' ? '⛈️' : '🌤️'}
              </span>
              <div>
                <p className="font-semibold text-gray-800">
                  {destinationLabel} <span className="text-blue-600">{weatherInfo.temp}°C</span> {weatherInfo.description}
                </p>
                <p className="text-xs text-gray-500">도착일 날씨 기준으로 의류를 선택해보세요</p>
              </div>
            </div>
          )}

          <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
            <p className="text-sm text-purple-800">{aiRecommendation.advice}</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {aiRecommendation.items.map((product) => (
              <div key={product.id} className="border-2 border-purple-300 rounded-xl overflow-hidden bg-white">
                <img src={product.imageUrl} alt={product.name} className="w-full h-44 object-cover" />
                <div className="p-3">
                  <p className="text-xs text-gray-500 font-medium">{product.brand}</p>
                  <p className="text-sm font-bold">{product.name}</p>
                  <p className="text-xs text-gray-500 mt-1">{product.description}</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="text-xs line-through text-gray-400">{formatPrice(product.price)}</span>
                    <span className="text-sm font-bold text-red-600">{formatPrice(product.discountPrice)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleClothingNext}
            className="w-full py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
          >
            이 코디로 피팅하기 →
          </button>
        </div>
      )}

      {/* Step: Attraction Selection */}
      {step === 'attraction' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">피팅 배경 관광지를 선택하세요</h3>
            <button onClick={() => setStep('clothing')} className="text-sm text-gray-500 hover:text-gray-700">← 뒤로</button>
          </div>
          <p className="text-sm text-gray-500">선택한 관광지가 가상 피팅의 배경이 됩니다</p>

          <div className="grid gap-3">
            {attractions.map((attr) => {
              const isSelected = selectedAttraction?.name === attr.name
              return (
                <button
                  key={attr.name}
                  onClick={() => setSelectedAttraction(attr)}
                  className={`flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                    {attr.nameKo?.charAt(0) || attr.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium">{attr.nameKo || attr.name}</p>
                    <p className="text-sm text-gray-500 truncate">{attr.description}</p>
                  </div>
                  {isSelected && <span className="text-blue-600 font-bold text-lg">✓</span>}
                </button>
              )
            })}
          </div>

          <button
            onClick={handleAttractionNext}
            disabled={!selectedAttraction}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음: 전신 사진 업로드
          </button>
        </div>
      )}

      {/* Step: Photo Upload & Execute */}
      {step === 'photo' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">전신 사진을 업로드하세요</h3>
            <button onClick={() => setStep('attraction')} className="text-sm text-gray-500 hover:text-gray-700">← 뒤로</button>
          </div>

          {/* Summary */}
          <div className="bg-gray-50 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">의류:</span>
              <div className="flex gap-1 flex-wrap">
                {selectedProducts.map((p) => (
                  <span key={p.id} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs">{p.brand} {p.name}</span>
                ))}
              </div>
            </div>
            <div className="text-sm">
              <span className="text-gray-500">배경:</span> <span className="font-medium">{selectedAttraction?.nameKo || selectedAttraction?.name}</span>
            </div>
          </div>

          {bodyPreview ? (
            <div className="space-y-3">
              <ImagePreview src={bodyPreview} onRemove={() => { setBodyImageId(null); setBodyPreview(null) }} />
              <button
                onClick={handleExecuteFitting}
                className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-indigo-700 shadow-lg"
              >
                🎨 가상 피팅 실행
              </button>
            </div>
          ) : (
            <FileUpload onFileSelect={handleBodyUpload} label="전신 사진을 업로드하세요 (정면, 전신이 보이는 사진)" />
          )}
        </div>
      )}

      {/* Step: Result */}
      {step === 'result' && fittingResult && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-center">가상 피팅 완료!</h3>

          {fittingResult.result_url && (
            <div className="flex justify-center">
              <img
                src={fittingResult.result_url}
                alt="피팅 결과"
                className="max-w-md w-full rounded-xl shadow-xl"
              />
            </div>
          )}

          {/* Clothing Info Cards */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-700">착용 의류 정보</h4>
            <div className="grid gap-3">
              {(fittingResult.clothing_info.length > 0 ? fittingResult.clothing_info : selectedProducts).map((item) => (
                <a
                  key={item.id}
                  href={`https://${window.innerWidth <= 768 ? 'm.' : ''}kor.lottedfs.com/kr/search?comSearchWord=${(item.brand + ' ' + item.name).replace(/\s+/g, '+')}&comCollection=&comTcatCD=&comMcatCD=&comScatCD=&comPriceMin=&comPriceMax=&comErpPrdGenVal_YN=&comHsaleIcon_YN=&comSaleIcon_YN=&comCpnIcon_YN=&comSvmnIcon_YN=&comGiftIcon_YN=&comMblSpprcIcon_YN=&comSpell_YN=&listCount=&returnUrl=&prd_moreListYn=&prd_curPageNo=&brandSearchWord=&korBrandList=&engBrandList=`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex gap-3 p-3 bg-white border rounded-xl hover:border-red-300 hover:shadow-md transition-all"
                >
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
                </a>
              ))}
            </div>
          </div>

          {/* CTA Button */}
          <a
            href={`https://${window.innerWidth <= 768 ? 'm.' : ''}kor.lottedfs.com/kr/search?comSearchWord=${((fittingResult.clothing_info.length > 0 ? fittingResult.clothing_info : selectedProducts)[0]?.brand + ' ' + (fittingResult.clothing_info.length > 0 ? fittingResult.clothing_info : selectedProducts)[0]?.name).replace(/\s+/g, '+')}&comCollection=&comTcatCD=&comMcatCD=&comScatCD=&comPriceMin=&comPriceMax=&comErpPrdGenVal_YN=&comHsaleIcon_YN=&comSaleIcon_YN=&comCpnIcon_YN=&comSvmnIcon_YN=&comGiftIcon_YN=&comMblSpprcIcon_YN=&comSpell_YN=&listCount=&returnUrl=&prd_moreListYn=&prd_curPageNo=&brandSearchWord=&korBrandList=&engBrandList=`}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-xl font-bold text-center text-lg hover:from-red-600 hover:to-pink-600 shadow-lg"
          >
            🎁 이 착장 그대로 면세점에서 15% 할인받기
          </a>

          {/* Retry Button */}
          <button
            onClick={() => {
              setStep('destination')
              setDestination('')
              setMode(null)
              setSelectedProducts([])
              setAiRecommendation(null)
              setSelectedAttraction(null)
              setBodyImageId(null)
              setBodyPreview(null)
              setFittingResult(null)
            }}
            className="w-full py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200"
          >
            다시 피팅하기
          </button>
        </div>
      )}
    </div>
  )
}
