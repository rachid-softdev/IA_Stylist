'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Clock } from 'lucide-react'
import type { GenerationJob } from '@vfs/shared-types'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const item = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
}

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
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Historique</h1>
        <p className="mt-1 text-text-secondary">Toutes vos générations</p>
      </motion.div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <motion.div variants={item} className="py-20 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent-primary/10 animate-float">
            <Clock className="h-6 w-6 text-accent-primary" />
          </div>
          <p className="font-heading text-lg text-text-primary">Aucune génération</p>
          <p className="mt-1 text-sm text-text-secondary">Vos looks générés apparaîtront ici</p>
        </motion.div>
      ) : (
        <motion.div variants={item} className="space-y-3">
          {jobs.map((job) => (
            <Card key={job.id} hover>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {job.job_type === 'image' ? 'Essayage Photo' : job.job_type === 'video' ? 'Vidéo' : 'Lookbook'}
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
                  <Badge status={job.status}>
                    {job.status === 'done' ? 'Terminé' : job.status === 'error' ? 'Erreur' : job.status}
                  </Badge>
                </div>
              </div>
            </Card>
          ))}
        </motion.div>
      )}
    </motion.div>
  )
}
