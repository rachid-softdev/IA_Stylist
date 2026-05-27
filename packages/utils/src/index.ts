import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind classes with conflict resolution
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a number of bytes to a human-readable string
 */
export function formatBytes(bytes: number, decimals = 1): string {
  if (bytes <= 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`
}

/**
 * Format a duration in milliseconds to a human-readable string
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}

/**
 * Format a date to a relative string (e.g. "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  try {
    return then.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return then.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })
  }
}

/**
 * Truncate a string to a given length and add ellipsis
 */
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length).trim() + '…'
}

/**
 * Generate a random ID (not crypto-secure, for UI use)
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 11)
}

/**
 * Clamp a number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * Check if a file type is an allowed image format
 */
export function isAllowedImageType(type: string): boolean {
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  return allowed.includes(type)
}

/**
 * Get the job status color class
 */
export function getJobStatusColor(status: string): string {
  switch (status) {
    case 'queued':
      return 'text-gen-queued'
    case 'processing':
      return 'text-gen-processing'
    case 'done':
      return 'text-gen-done'
    case 'error':
      return 'text-gen-error'
    default:
      return 'text-text-tertiary'
  }
}

/**
 * Get the job status label in French
 */
export function getJobStatusLabel(status: string): string {
  switch (status) {
    case 'queued':
      return 'En attente'
    case 'processing':
      return 'En cours'
    case 'done':
      return 'Terminé'
    case 'error':
      return 'Erreur'
    case 'cancelled':
      return 'Annulé'
    default:
      return status
  }
}
