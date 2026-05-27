import { create } from 'zustand'

interface ToastItem {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message?: string
  duration?: number
}

interface ToastState {
  toasts: ToastItem[]
  addToast: (toast: Omit<ToastItem, 'id'>) => void
  removeToast: (id: string) => void
}

let toastId = 0

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = `toast_${++toastId}`
    set((state) => ({
      toasts: [
        ...state.toasts.slice(-3), // Keep max 3
        { ...toast, id },
      ],
    }))

    const duration = toast.duration || (toast.type === 'error' ? 6000 : toast.type === 'success' ? 3000 : 4000)

    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }))
    }, duration)
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}))
