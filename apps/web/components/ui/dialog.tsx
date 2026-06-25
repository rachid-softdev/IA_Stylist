'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@vfs/utils'
import { useCallback, useEffect, useRef } from 'react'
import { X } from 'lucide-react'

interface DialogProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  className?: string
}

const overlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
}

const contentVariants = {
  hidden: { opacity: 0, y: 24, scale: 0.96 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: 16, scale: 0.96, transition: { duration: 0.2 } },
}

/** Query all focusable elements within a container */
function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selectors = [
    'a[href]', 'button:not([disabled])', 'input:not([disabled])',
    'select:not([disabled])', 'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ]
  return Array.from(container.querySelectorAll<HTMLElement>(selectors.join(',')))
}

export function Dialog({ open, onClose, title, children, className }: DialogProps) {
  const contentRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLElement | null>(null)

  // Store the triggering element on open
  useEffect(() => {
    if (open) {
      triggerRef.current = document.activeElement as HTMLElement
    }
    return () => {
      // Restore focus on close — but only if dialog was open
      if (!open && triggerRef.current && typeof triggerRef.current.focus === 'function') {
        triggerRef.current.focus()
        triggerRef.current = null
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  // Focus trap
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key !== 'Tab' || !contentRef.current) return

    const focusable = getFocusableElements(contentRef.current)
    if (focusable.length === 0) {
      e.preventDefault()
      return
    }

    const first = focusable[0] as HTMLElement
    const last = focusable[focusable.length - 1] as HTMLElement

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }, [])

  useEffect(() => {
    if (!open) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleEscape)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open, onClose, handleKeyDown])

  // Auto-focus first element on open
  useEffect(() => {
    if (open && contentRef.current) {
      const focusable = getFocusableElements(contentRef.current)
      // Small RAF to let the animation start before focusing
      requestAnimationFrame(() => {
        if (focusable.length > 0) {
          focusable[0]!.focus()
        } else {
          contentRef.current?.focus()
        }
      })
    }
  }, [open])

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

  return (
    <AnimatePresence>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'dialog-title' : undefined}
        >
          <motion.div
            className="absolute inset-0 bg-black/60"
            variants={overlayVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={onClose}
          />
          <motion.div
            ref={contentRef}
            tabIndex={-1}
            variants={contentVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={cn(
              'relative z-10 w-full max-w-lg rounded-xl border border-border-default bg-bg-surface p-6 shadow-xl outline-none',
              className,
            )}
          >
            {title && (
              <div className="mb-4 flex items-center justify-between">
                <h2 id="dialog-title" className="text-lg font-heading text-text-primary">
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="rounded p-1 text-text-tertiary hover:bg-bg-overlay hover:text-text-primary transition-colors duration-150"
                  aria-label="Fermer"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
