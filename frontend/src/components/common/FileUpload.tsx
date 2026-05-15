import { useCallback, useRef, useState } from 'react'
import { MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES } from '../../constants'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number
  label?: string
}

export function FileUpload({
  onFileSelect,
  accept = 'image/jpeg,image/png,image/webp',
  maxSize = MAX_FILE_SIZE,
  label = '이미지를 드래그하거나 클릭하여 업로드',
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateAndSelect = useCallback((file: File) => {
    setError(null)
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setError('JPG, PNG, WebP 파일만 지원합니다')
      return
    }
    if (file.size > maxSize) {
      setError('파일 크기가 10MB를 초과합니다')
      return
    }
    onFileSelect(file)
  }, [onFileSelect, maxSize])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) validateAndSelect(file)
  }, [validateAndSelect])

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      data-testid="file-upload-dropzone"
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) validateAndSelect(file)
        }}
      />
      <p className="text-gray-500">{label}</p>
      <p className="text-xs text-gray-400 mt-2">JPG, PNG, WebP (최대 10MB)</p>
      {error && <p className="text-sm text-red-500 mt-2">{error}</p>}
    </div>
  )
}
