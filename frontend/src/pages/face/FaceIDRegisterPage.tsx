import { useEffect } from 'react'
import { useFaceID } from '../../hooks/useFaceID'

export function FaceIDRegisterPage() {
  const {
    videoRef,
    capturedImage,
    isProcessing,
    startCamera,
    stopCamera,
    captureImage,
    registerFace,
    setCapturedImage,
  } = useFaceID()

  useEffect(() => {
    startCamera()
    return () => stopCamera()
  }, [startCamera, stopCamera])

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Face ID 등록</h2>
        <p className="mt-2 text-sm text-gray-500">
          정면을 바라보며 셀피를 촬영해주세요
        </p>
      </div>

      <div className="flex flex-col items-center gap-4">
        {!capturedImage ? (
          <>
            <div className="relative w-80 h-60 bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover scale-x-[-1]"
                data-testid="face-register-video"
              />
            </div>
            <button
              onClick={captureImage}
              className="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700"
              data-testid="face-register-capture-button"
            >
              촬영
            </button>
          </>
        ) : (
          <>
            <div className="w-80 h-60 bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={URL.createObjectURL(capturedImage)}
                alt="캡처된 셀피"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => { setCapturedImage(null); startCamera() }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                data-testid="face-register-retake-button"
              >
                재촬영
              </button>
              <button
                onClick={() => registerFace(capturedImage)}
                disabled={isProcessing}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                data-testid="face-register-confirm-button"
              >
                {isProcessing ? '등록 중...' : '등록 확인'}
              </button>
            </div>
          </>
        )}
      </div>

      <div className="text-center text-xs text-gray-400">
        <p>밝은 곳에서 정면을 바라봐주세요</p>
        <p>모자, 선글라스 등은 벗어주세요</p>
      </div>
    </div>
  )
}
