'use client'

import { motion, AnimatePresence } from 'framer-motion'
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
  success: 'border-t-status-success',
  error: 'border-t-status-error',
  warning: 'border-t-status-warning',
  info: 'border-t-accent-primary',
}

const toastVariants = {
  initial: { opacity: 0, y: 16, scale: 0.95 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -8, scale: 0.95, transition: { duration: 0.2 } },
}

export function Toaster() {
  const { toasts, removeToast } = useToastStore()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 md:top-4 md:bottom-auto" role="region" aria-label="Notifications">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => {
          const Icon = iconMap[toast.type]

          return (
            <motion.div
              key={toast.id}
              layout
              variants={toastVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              role="alert"
              aria-live="assertive"
              aria-atomic="true"
              className={cn(
                'flex w-80 items-start gap-3 rounded-lg border bg-bg-surface p-4 shadow-lg border-t-[3px]',
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
                className="shrink-0 text-text-tertiary hover:text-text-primary transition-colors duration-150"
                aria-label="Fermer"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
