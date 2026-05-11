import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@vfs/utils'
import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg-base disabled:pointer-events-none disabled:opacity-40 active:scale-[0.97]',
  {
    variants: {
      variant: {
        primary:
          'bg-accent-primary text-text-inverse hover:brightness-110 shadow-sm',
        secondary:
          'border border-border-default text-text-primary hover:bg-bg-overlay',
        ghost: 'text-text-secondary hover:text-text-primary hover:bg-bg-overlay',
        destructive:
          'text-status-error border border-status-error hover:bg-status-error/10',
        loading:
          'bg-accent-primary text-text-inverse opacity-70 cursor-wait',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-md',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  },
)

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
  iconLeft?: React.ReactNode
  iconRight?: React.ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      loading,
      iconLeft,
      iconRight,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        className={cn(
          buttonVariants({
            variant: loading ? 'loading' : variant,
            size,
          }),
          className,
        )}
        disabled={isDisabled}
        {...props}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin-slow" />
        ) : (
          iconLeft
        )}
        {children}
        {!loading && iconRight}
      </button>
    )
  },
)

Button.displayName = 'Button'
