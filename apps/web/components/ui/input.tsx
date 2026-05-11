import { cn } from '@vfs/utils'
import { forwardRef, type InputHTMLAttributes } from 'react'
import { AlertCircle } from 'lucide-react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs text-text-secondary tracking-widest uppercase"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'h-10 rounded-md border bg-bg-surface px-3 text-base text-text-primary placeholder:text-text-tertiary transition-colors duration-200',
            'focus:border-border-strong focus:shadow-[0_0_0_2px_rgba(212,168,83,0.2)] focus:outline-none',
            'disabled:cursor-not-allowed disabled:opacity-40',
            error
              ? 'border-status-error focus:shadow-[0_0_0_2px_rgba(139,58,56,0.2)]'
              : 'border-border-default',
            className,
          )}
          {...props}
        />
        {error && (
          <span className="flex items-center gap-1 text-xs text-status-error">
            <AlertCircle className="h-3 w-3" />
            {error}
          </span>
        )}
        {helperText && !error && (
          <span className="text-xs text-text-tertiary">{helperText}</span>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'
