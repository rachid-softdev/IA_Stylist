import { Progress } from '@/components/ui/progress'
import type { JobStatus } from '@vfs/shared-types'

interface JobProgressProps {
  jobId: string
  status: JobStatus | null
}

const statusMessages: Record<string, string> = {
  queued: 'En attente dans la file...',
  processing: 'Analyse du vêtement et de la pose...',
  done: 'Génération terminée !',
  error: 'Erreur lors de la génération',
}

export function JobProgress({ jobId, status }: JobProgressProps) {
  const message = statusMessages[status || 'queued'] || 'Préparation...'
  const isProcessing = status === 'processing'

  return (
    <div
      role="status"
      aria-label="Génération en cours"
      aria-live="polite"
      className={`rounded-lg border bg-bg-surface p-8 text-center transition-all duration-300 ${
        isProcessing
          ? 'border-accent-primary/30 animate-pulse-glow'
          : 'border-border-default'
      }`}
    >
      <Progress
        indeterminate
        label={message}
        className="mx-auto max-w-xs"
      />
      <p className="mt-3 font-mono text-xs text-text-tertiary">
        Job #{jobId.slice(0, 8)}
      </p>
    </div>
  )
}
