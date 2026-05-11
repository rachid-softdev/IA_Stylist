import { cn } from '@vfs/utils'

interface AvatarProps {
  src?: string | null
  fallback?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Avatar({ src, fallback, size = 'md', className }: AvatarProps) {
  const sizeClasses = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
  }

  if (src) {
    return (
      <img
        src={src}
        alt={fallback || 'Avatar'}
        className={cn('rounded-full object-cover', sizeClasses[size], className)}
      />
    )
  }

  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full bg-bg-elevated text-text-secondary font-medium',
        sizeClasses[size],
        className,
      )}
    >
      {fallback?.charAt(0).toUpperCase() || '?'}
    </div>
  )
}
