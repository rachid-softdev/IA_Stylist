import { cn } from '@vfs/utils'
import { getJobStatusLabel as getLabel } from '@vfs/utils'

interface BadgeProps {
  status: string
  className?: string
  children?: React.ReactNode
}

const colorMap: Record<string, string> = {
  queued: 'bg-gen-queued/10 text-gen-queued border-gen-queued/30',
  processing: 'bg-gen-processing/10 text-gen-processing border-gen-processing/30',
  done: 'bg-gen-done/10 text-gen-done border-gen-done/30',
  error: 'bg-gen-error/10 text-gen-error border-gen-error/30',
  cancelled: 'bg-text-tertiary/10 text-text-tertiary border-text-tertiary/30',
  active: 'bg-gen-done/10 text-gen-done border-gen-done/30',
  inactive: 'bg-text-tertiary/10 text-text-tertiary border-text-tertiary/30',
}

export function Badge({ status, className, children }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
        colorMap[status] || colorMap.done,
        className,
      )}
    >
      {children ?? getLabel(status)}
    </span>
  )
}
