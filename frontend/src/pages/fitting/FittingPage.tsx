import { useState } from 'react'
import { FileUpload } from '../../components/common/FileUpload'
import { ImagePreview } from '../../components/common/ImagePreview'
import { LoadingSpinner } from '../../components/common/LoadingSpinner'
import { useFitting } from '../../hooks/useFitting'
import { CLOTHING_CATEGORIES } from '../../constants'
import type { ClothingCategory } from '../../types'

export function FittingPage() {
  const {
    bodyImage,
    clothingList,
    isProcessing,
    uploadBody,
    uploadClothing,
    removeClothing,
    executeFitting,
  } = useFitting()
  const [selectedCategory, setSelectedCategory] = useState<ClothingCategory>('top')

  if (isProcessing) {
    return <LoadingSpinner message="AI가 옷을 입혀보고 있어요..." />
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">가상 피팅</h2>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Body image section */}
        <div className="space-y-3">
          <h3 className="font-medium text-gray-700">전신 사진</h3>
          {bodyImage ? (
            <ImagePreview src={bodyImage.previewUrl} onRemove={() => window.location.reload()} />
          ) : (
            <FileUpload onFileSelect={uploadBody} label="전신 사진을 업로드하세요" />
          )}
        </div>

        {/* Clothing section */}
        <div className="space-y-3">
          <h3 className="font-medium text-gray-700">의류</h3>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as ClothingCategory)}
            className="w-full px-3 py-2 border rounded-lg"
            data-testid="fitting-category-select"
          >
            {CLOTHING_CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>

          <FileUpload
            onFileSelect={(file) => uploadClothing(file, selectedCategory)}
            label="의류 이미지를 업로드하세요"
          />

          {clothingList.length > 0 && (
            <div className="grid grid-cols-3 gap-2">
              {clothingList.map((item) => (
                <div key={item.clothingId} className="relative">
                  <img src={item.previewUrl} alt={item.category} className="w-full h-24 object-cover rounded" />
                  <span className="absolute top-1 left-1 text-xs bg-black/50 text-white px-1 rounded">
                    {CLOTHING_CATEGORIES.find((c) => c.value === item.category)?.label}
                  </span>
                  <button
                    onClick={() => removeClothing(item.clothingId)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-5 h-5 text-xs"
                    data-testid={`fitting-remove-clothing-${item.clothingId}`}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <button
        onClick={executeFitting}
        disabled={!bodyImage || clothingList.length === 0}
        className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        data-testid="fitting-execute-button"
      >
        피팅 실행
      </button>
    </div>
  )
}
