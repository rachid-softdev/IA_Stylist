import { Progress } from '@/components/ui/progress'
import { Spinner } from '@/components/ui/spinner'
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
  const percent = status === 'queued' ? 10 : status === 'processing' ? 60 : status === 'done' ? 100 : 0

  const isProcessing = status === 'processing'

  return (
    <div
      role="status"
      aria-label="Génération en cours"
      aria-live="polite"
      className={`rounded-lg border border-border-default bg-bg-surface p-8 text-center transition-all duration-300 ${
        isProcessing ? 'animate-pulse-glow border-accent-primary/30' : ''
      }`}
    >
      <div className="mb-6 flex justify-center">
        <Spinner size="md" />
      </div>
      <Progress
        value={percent}
        max={100}
        label={message}
        className="mx-auto max-w-xs"
      />
      <p className="mt-3 font-mono text-xs text-text-tertiary">
        Job #{jobId.slice(0, 8)}
      </p>
    </div>
  )
}
