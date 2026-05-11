'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { GenerationJob } from '@vfs/shared-types'

export default function HistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['history'],
    queryFn: async () => {
      const res = await api.get<GenerationJob[]>('/dressing/history')
      return res
    },
  })

  const jobs = data?.data || []

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Historique</h1>
        <p className="mt-1 text-text-secondary">Toutes vos générations</p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="py-20 text-center">
          <p className="text-text-secondary">Aucune génération pour le moment</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <Card key={job.id} hover>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {job.job_type === 'image' ? 'Try-On Image' : job.job_type === 'video' ? 'Vidéo' : 'Lookbook'}
                  </p>
                  <p className="text-xs text-text-tertiary">
                    {new Date(job.created_at).toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'short',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-text-secondary">
                    {job.credits_used} crédit{job.credits_used > 1 ? 's' : ''}
                  </span>
                  <span
                    className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${
                      job.status === 'done'
                        ? 'border-gen-done/30 bg-gen-done/10 text-gen-done'
                        : job.status === 'error'
                          ? 'border-gen-error/30 bg-gen-error/10 text-gen-error'
                          : 'border-text-tertiary/30 bg-text-tertiary/10 text-text-tertiary'
                    }`}
                  >
                    {job.status === 'done' ? 'Terminé' : job.status === 'error' ? 'Erreur' : job.status}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
