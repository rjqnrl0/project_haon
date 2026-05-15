import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useUIStore } from '../stores/uiStore'
import type { ClothingCategory } from '../types'

interface BodyImage {
  taskId: string
  s3Key: string
  fileHash: string
  previewUrl: string
}

interface ClothingItem {
  clothingId: string
  s3Key: string
  category: ClothingCategory
  previewUrl: string
}

export function useFitting() {
  const [bodyImage, setBodyImage] = useState<BodyImage | null>(null)
  const [clothingList, setClothingList] = useState<ClothingItem[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const showToast = useUIStore((s) => s.showToast)
  const navigate = useNavigate()

  const uploadBody = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post('/fitting/body/upload', formData)
      setBodyImage({
        taskId: data.task_id,
        s3Key: data.body_s3_key,
        fileHash: data.file_hash,
        previewUrl: URL.createObjectURL(file),
      })
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '업로드 실패' })
    }
  }

  const uploadClothing = async (file: File, category: ClothingCategory) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    try {
      const { data } = await api.post('/fitting/clothing/upload', formData)
      setClothingList((prev) => [
        ...prev,
        {
          clothingId: data.clothing_id,
          s3Key: data.s3_key,
          category: data.category,
          previewUrl: URL.createObjectURL(file),
        },
      ])
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '업로드 실패' })
    }
  }

  const removeClothing = (clothingId: string) => {
    setClothingList((prev) => prev.filter((c) => c.clothingId !== clothingId))
  }

  const executeFitting = async () => {
    if (!bodyImage) {
      showToast({ type: 'error', message: '전신 사진을 먼저 업로드해주세요' })
      return
    }
    setIsProcessing(true)
    try {
      const { data } = await api.post('/fitting/execute', {
        body_image_id: bodyImage.taskId,
        clothing_ids: clothingList.map((c) => c.clothingId),
      })
      setResultUrl(data.result_url)
      navigate(`/fitting/result/${data.task_id}`)
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '피팅 실행 실패' })
    } finally {
      setIsProcessing(false)
    }
  }

  return {
    bodyImage,
    clothingList,
    isProcessing,
    resultUrl,
    uploadBody,
    uploadClothing,
    removeClothing,
    executeFitting,
  }
}
