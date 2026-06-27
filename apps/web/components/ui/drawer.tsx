'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@vfs/utils'
import { useEffect, useRef } from 'react'
import { X } from 'lucide-react'

interface DrawerProps {
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

const sheetVariants = {
  hidden: { y: '100%' },
  visible: { y: 0, transition: { type: 'spring', damping: 28, stiffness: 300, mass: 0.8 } },
  exit: { y: '100%', transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] } },
}

export function Drawer({ open, onClose, title, children, className }: DrawerProps) {
  const contentRef = useRef<HTMLDivElement>(null)

  // Store the triggering element
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

  // Escape to close
  useEffect(() => {
    if (!open) return
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center sm:items-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'drawer-title' : undefined}
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
            variants={sheetVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={cn(
              'relative z-10 w-full rounded-t-2xl border border-border-default bg-bg-surface p-6 shadow-xl outline-none sm:mx-4 sm:max-w-lg sm:rounded-b-2xl',
              className,
            )}
          >
            {/* Drag handle (mobile visual cue) */}
            <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-border-strong sm:hidden" />

            {title && (
              <div className="mb-4 flex items-center justify-between">
                <h2 id="drawer-title" className="text-lg font-heading text-text-primary">
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
