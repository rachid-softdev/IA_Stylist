'use client'

import { cn } from '@vfs/utils'
import { useToastStore } from '@/stores/toast-store'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const iconMap = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
}

const colorMap = {
  success: 'border-l-status-success',
  error: 'border-l-status-error',
  warning: 'border-l-status-warning',
  info: 'border-l-accent-primary',
}

export function Toaster() {
  const { toasts, removeToast } = useToastStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 md:top-4 md:bottom-auto" role="region" aria-label="Notifications">
      {toasts.map((toast) => {
        const Icon = iconMap[toast.type]

        return (
          <div
            key={toast.id}
            role="alert"
            aria-live="assertive"
            aria-atomic="true"
            className={cn(
              'flex w-80 items-start gap-3 rounded-lg border bg-bg-surface p-4 shadow-lg animate-slide-up border-l-[3px]',
              colorMap[toast.type],
            )}
          >
            <Icon className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-text-primary">{toast.title}</p>
              {toast.message && (
                <p className="text-xs text-text-secondary">{toast.message}</p>
              )}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="shrink-0 text-text-tertiary hover:text-text-primary"
              aria-label="Fermer"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
