import { Button } from '@/components/ui/button'
import { Sparkles, Coins } from 'lucide-react'

interface GenerateButtonProps {
  onClick: () => void
  disabled: boolean
  credits: number
}

export function GenerateButton({ onClick, disabled, credits }: GenerateButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      size="lg"
      iconLeft={<Sparkles className="h-4 w-4" />}
      iconRight={
        <span className="flex items-center gap-1 text-sm opacity-70">
          <Coins className="h-3 w-3" />
          {credits}
        </span>
      }
      className="w-full sm:w-auto"
    >
      Générer {!disabled && `— ${credits} crédit${credits > 1 ? 's' : ''}`}
    </Button>
  )
}
