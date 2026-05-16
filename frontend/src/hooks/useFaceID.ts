import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import { useUIStore } from '../stores/uiStore'

export function useFaceID() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [capturedImage, setCapturedImage] = useState<Blob | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const setAuth = useAuthStore((s) => s.setAuth)
  const accessToken = useAuthStore((s) => s.accessToken)
  const showToast = useUIStore((s) => s.showToast)

  const startCamera = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { min: 640 }, height: { min: 480 } },
    })
    streamRef.current = stream
    if (videoRef.current) {
      videoRef.current.srcObject = stream
    }
  }, [])

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
  }, [])

  const captureImage = useCallback(() => {
    if (!videoRef.current) return null

    const canvas = document.createElement('canvas')
    canvas.width = videoRef.current.videoWidth
    canvas.height = videoRef.current.videoHeight
    const ctx = canvas.getContext('2d')!
    ctx.translate(canvas.width, 0)
    ctx.scale(-1, 1)
    ctx.drawImage(videoRef.current, 0, 0)

    canvas.toBlob(
      (blob) => {
        if (blob) setCapturedImage(blob)
      },
      'image/jpeg',
      0.8,
    )
  }, [])

  const registerFace = useCallback(async (imageBlob: Blob) => {
    setIsProcessing(true)
    try {
      const formData = new FormData()
      formData.append('file', imageBlob, 'selfie.jpg')
      await api.post('/face/register', formData)

      if (user && accessToken) {
        setAuth({ ...user, faceRegistered: true }, accessToken)
      }
      showToast({ type: 'success', message: '얼굴 등록이 완료되었습니다' })
      navigate('/fitting')
    } catch (err: any) {
      showToast({ type: 'error', message: err.response?.data?.detail || '얼굴 등록 실패' })
    } finally {
      setIsProcessing(false)
    }
  }, [user, accessToken, setAuth, showToast, navigate])

  return {
    videoRef,
    capturedImage,
    isProcessing,
    startCamera,
    stopCamera,
    captureImage,
    registerFace,
    setCapturedImage,
  }
}
