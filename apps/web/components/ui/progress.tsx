import { cn } from '@vfs/utils'

interface ProgressProps {
  value: number
  max?: number
  label?: string
  className?: string
}

export function Progress({ value, max = 100, label, className }: ProgressProps) {
  const percent = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <div className="h-0.5 w-full overflow-hidden rounded-full bg-bg-elevated">
        <div
          className="h-full rounded-full bg-accent-primary transition-all duration-300 ease-out animate-shimmer"
          style={{ width: `${percent}%` }}
        />
      </div>
      {label && (
        <span className="font-mono text-xs text-text-secondary">
          {label}
        </span>
      )}
    </div>
  )
}
