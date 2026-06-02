import { create } from 'zustand'

export interface ToastItem {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
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
    const id = `toast-${++toastId}`
    set((state) => ({ toasts: [...state.toasts, { ...toast, id }] }))
    const duration = toast.duration ?? 3000
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
      }, duration)
    }
  },
  removeToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}))

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore()

  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  }

  const colorMap = {
    success: 'var(--color-accent)',
    error: 'var(--color-danger)',
    warning: 'var(--color-warning)',
    info: 'var(--color-text-secondary)',
  }

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2" style={{ maxWidth: '380px' }}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="animate-toast-in flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg"
          style={{
            background: 'var(--color-bg-secondary)',
            border: '1px solid var(--color-border)',
            borderLeft: `3px solid ${colorMap[toast.type]}`,
          }}
        >
          <span
            className="text-sm font-bold flex-shrink-0"
            style={{ color: colorMap[toast.type] }}
          >
            {iconMap[toast.type]}
          </span>
          <span className="text-sm flex-1" style={{ color: 'var(--color-text-primary)' }}>
            {toast.message}
          </span>
          <button
            onClick={() => removeToast(toast.id)}
            className="flex-shrink-0 p-0.5 rounded transition-colors"
            style={{ color: 'var(--color-text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-text-primary)' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-muted)' }}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}

export function useToast() {
  const addToast = useToastStore((s) => s.addToast)
  return {
    success: (message: string) => addToast({ type: 'success', message }),
    error: (message: string) => addToast({ type: 'error', message, duration: 5000 }),
    warning: (message: string) => addToast({ type: 'warning', message }),
    info: (message: string) => addToast({ type: 'info', message }),
  }
}
