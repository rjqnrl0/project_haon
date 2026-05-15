import { useUIStore } from '../../stores/uiStore'

export function Toast() {
  const toast = useUIStore((s) => s.toast)
  const hideToast = useUIStore((s) => s.hideToast)

  if (!toast) return null

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
  }[toast.type]

  return (
    <div className="fixed top-4 right-4 z-50" data-testid="toast">
      <div className={`${bgColor} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-2`}>
        <span>{toast.message}</span>
        <button onClick={hideToast} className="ml-2 text-white/80 hover:text-white">
          &times;
        </button>
      </div>
    </div>
  )
}
