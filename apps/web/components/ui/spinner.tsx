import { cn } from '@vfs/utils'

interface SpinnerProps {
  size?: 'sm' | 'md'
  className?: string
}

export function Spinner({ size = 'sm', className }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Chargement"
      className={cn(
        'animate-spin-slow rounded-full border-2 border-border-default border-t-accent-primary',
        size === 'sm' && 'h-4 w-4',
        size === 'md' && 'h-6 w-6',
        className,
      )}
    />
  )
}
