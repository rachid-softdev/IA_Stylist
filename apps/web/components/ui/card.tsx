import { cn } from '@vfs/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

export function Card({ children, className, hover = true }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border-default bg-bg-surface p-6',
        hover && 'transition-all duration-200 hover:border-border-strong hover:shadow-md',
        className,
      )}
    >
      {children}
    </div>
  )
}
