import { cn } from '@vfs/utils'

interface ProgressProps {
  value?: number
  max?: number
  label?: string
  className?: string
  indeterminate?: boolean
}

export function Progress({ value, max = 100, label, className, indeterminate }: ProgressProps) {
  const percent = value != null ? Math.min(100, Math.max(0, (value / max) * 100)) : 0

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <div className="h-0.5 w-full overflow-hidden rounded-full bg-bg-elevated">
        <div
          className={cn(
            'h-full rounded-full',
            indeterminate
              ? 'w-1/3 animate-progress-indeterminate bg-accent-primary'
              : 'bg-accent-primary transition-all duration-300 ease-out',
          )}
          style={!indeterminate ? { width: `${percent}%` } : undefined}
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
