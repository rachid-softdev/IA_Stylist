import { cn } from '@vfs/utils'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'card' | 'image'
}

export function Skeleton({ className, variant = 'text' }: SkeletonProps) {
  const baseClass = 'rounded animate-shimmer'

  const variants = {
    text: 'h-4 w-full',
    card: 'h-32 w-full',
    image: 'aspect-[3/4] w-full',
  }

  return (
    <div
      className={cn(baseClass, variants[variant], className)}
      aria-hidden="true"
    />
  )
}
