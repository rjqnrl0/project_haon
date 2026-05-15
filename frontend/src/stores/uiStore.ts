import { create } from 'zustand'

interface ToastMessage {
  type: 'success' | 'error' | 'warning'
  message: string
}

interface UIState {
  isLoading: boolean
  toast: ToastMessage | null
  setLoading: (loading: boolean) => void
  showToast: (toast: ToastMessage) => void
  hideToast: () => void
}

export const useUIStore = create<UIState>((set) => ({
  isLoading: false,
  toast: null,

  setLoading: (loading) => set({ isLoading: loading }),

  showToast: (toast) => {
    set({ toast })
    setTimeout(() => set({ toast: null }), 3000)
  },

  hideToast: () => set({ toast: null }),
}))
