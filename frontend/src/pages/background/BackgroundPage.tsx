import { useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../lib/api'
import { FileUpload } from '../../components/common/FileUpload'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'
import { useUIStore } from '../../stores/uiStore'

export function BackgroundPage() {
  const { resultId } = useParams()
  const [mode, setMode] = useState<'text' | 'upload'>('text')
  const [prompt, setPrompt] = useState('')
  const [backgrounds, setBackgrounds] = useState<any[]>([])
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const showToast = useUIStore((s) => s.showToast)

  const searchBackgrounds = async () => {
    if (!prompt.trim()) return
    setIsLoading(true)
    try {
      const { data } = await api.get('/background/search', { params: { prompt } })
      setBackgrounds(data)
    } catch {
      showToast({ type: 'error', message: '배경 검색 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  const applyTextBackground = async () => {
    setIsLoading(true)
    try {
      const { data } = await api.post('/background/text', {
        source_task_id: resultId,
        prompt,
      })
      setResultUrl(data.result_url)
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '배경 적용 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  const uploadBackground = async (file: File) => {
    setIsLoading(true)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post(`/background/upload/${resultId}`, formData)
      setResultUrl(data.result_url)
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '배경 적용 실패' })
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) return <LoadingSpinner message="배경을 합성하고 있어요..." />

  if (resultUrl) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">배경 변경 결과</h2>
        <img src={resultUrl} alt="배경 합성 결과" className="max-w-lg mx-auto rounded-lg shadow-lg" />
        <div className="flex justify-center gap-3">
          <button onClick={() => setResultUrl(null)} className="px-4 py-2 bg-gray-200 rounded-lg">
            다른 배경 시도
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">배경 변경</h2>

      <div className="flex gap-2">
        <button
          onClick={() => setMode('text')}
          className={`px-4 py-2 rounded-lg ${mode === 'text' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          data-testid="background-text-tab"
        >
          텍스트로 생성
        </button>
        <button
          onClick={() => setMode('upload')}
          className={`px-4 py-2 rounded-lg ${mode === 'upload' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          data-testid="background-upload-tab"
        >
          이미지 업로드
        </button>
      </div>

      {mode === 'text' ? (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              maxLength={200}
              placeholder="원하는 배경을 설명해주세요 (예: 파리 에펠탑 앞)"
              className="flex-1 px-3 py-2 border rounded-lg"
              data-testid="background-prompt-input"
            />
            <button onClick={searchBackgrounds} className="px-4 py-2 bg-blue-600 text-white rounded-lg" data-testid="background-search-button">
              검색
            </button>
          </div>
          <p className="text-xs text-gray-400">{prompt.length}/200</p>

          {backgrounds.length > 0 && (
            <div className="grid grid-cols-5 gap-2">
              {backgrounds.map((bg: any) => (
                <img key={bg.id} src={bg.thumbnail || bg.url} alt={bg.description} className="w-full h-20 object-cover rounded cursor-pointer hover:ring-2 ring-blue-500" onClick={applyTextBackground} />
              ))}
            </div>
          )}

          <button onClick={applyTextBackground} disabled={!prompt} className="w-full py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50" data-testid="background-apply-button">
            배경 적용
          </button>
        </div>
      ) : (
        <FileUpload onFileSelect={uploadBackground} label="배경 이미지를 업로드하세요" />
      )}
    </div>
  )
}
