'use client'

import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog } from '@/components/ui/dialog'
import Image from 'next/image'
import { Download, Trash2, Search, Filter, Camera } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'
import type { GenerationJob } from '@vfs/shared-types'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function DressingPage() {
  const [filter, setFilter] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const { addToast } = useToastStore()

  const { data, isLoading } = useQuery({
    queryKey: ['dressing'],
    queryFn: async () => {
      const res = await api.get<GenerationJob[]>('/dressing/?status=done')
      return res
    },
  })

  const jobs = data?.data || []

  const handleDelete = useCallback(async (jobId: string) => {
    setDeletingId(jobId)
    try {
      await api.delete(`/dressing/${jobId}`)
      setConfirmDeleteId(null)
      addToast({ type: 'success', title: 'Supprimé' })
    } catch {
      addToast({ type: 'error', title: 'Erreur', message: 'Impossible de supprimer' })
    } finally {
      setDeletingId(null)
    }
  }, [addToast])

  const handleDownload = (url: string, jobId: string) => {
    const a = document.createElement('a')
    a.href = url
    a.download = `vfs-${jobId.slice(0, 8)}.webp`
    a.click()
  }

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Dressing</h1>
        <p className="mt-1 text-text-secondary">Votre galerie de looks générés</p>
      </motion.div>

      {/* Filters */}
      <motion.div variants={item} className="mb-6 flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            placeholder="Rechercher..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button variant="secondary" size="md" iconLeft={<Filter className="h-4 w-4" />}>
          Filtres
        </Button>
      </motion.div>

      {/* Grid */}
      <motion.div variants={item}>
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} variant="image" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent-primary/10 animate-float">
            <Camera className="h-6 w-6 text-accent-primary" />
          </div>
          <h2 className="text-xl font-heading text-text-primary">Votre dressing est vide</h2>
          <p className="mt-2 max-w-sm text-text-secondary leading-relaxed">
            Créez votre premier look dans le Studio — choisissez un vêtement, 
            téléchargez votre photo, et laissez la magie opérer.
          </p>
          <Button variant="primary" className="mt-6" onClick={() => window.location.href = '/studio'}>
            Ouvrir le Studio
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {jobs
              .filter((j) =>
                !filter || j.id?.toLowerCase().includes(filter.toLowerCase()) || (j as any).garment_name?.toLowerCase().includes(filter.toLowerCase())
              )
            .map((job) => (
              <div
                key={job.id}
                className="group relative aspect-square overflow-hidden rounded-lg border border-border-default bg-bg-surface transition-colors duration-200 hover:border-border-strong hover:shadow-md animate-card-in"
              >
                {job.result_url ? (
                  <Image
                    src={job.result_url}
                    alt={(job as any).garment_name ? `Look ${(job as any).garment_name}` : 'Look généré'}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                    onError={(e) => { (e.target as HTMLElement).style.display = 'none' }}
                  />
                ) : (
                  <div className="aspect-square w-full bg-bg-elevated" />
                )}

                {/* Overlay actions — always visible on mobile, hover-reveal on desktop */}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-bg-base/95 to-transparent p-3 pt-8 transition-transform duration-200 md:translate-y-full md:group-hover:translate-y-0">
                  <div className="flex items-center justify-between">
                    <Button
                      variant="ghost"
                      size="sm"
                      iconLeft={<Download className="h-3.5 w-3.5" />}
                      onClick={(e) => {
                        e.preventDefault()
                        job.result_url && handleDownload(job.result_url, job.id)
                      }}
                    >
                      Télécharger
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      iconLeft={<Trash2 className="h-3.5 w-3.5" />}
                      loading={deletingId === job.id}
                      disabled={deletingId !== null}
                      onClick={(e) => {
                        e.preventDefault()
                        setConfirmDeleteId(job.id)
                      }}
                    >
                      Supprimer
                    </Button>
                  </div>
                </div>

                {/* Status badge */}
                <Badge
                  status={job.status}
                  className="absolute right-2 top-2"
                />
              </div>
            ))}
        </div>
      )}
      </motion.div>

      {/* Confirm delete dialog */}
      <Dialog open={confirmDeleteId !== null} onClose={() => setConfirmDeleteId(null)} title="Supprimer ce look ?">
        <p className="text-sm text-text-secondary">
          Cette action est irréversible. Le look sera définitivement supprimé de votre dressing.
        </p>
        <div className="mt-6 flex gap-3 justify-end">
          <Button variant="secondary" size="sm" onClick={() => setConfirmDeleteId(null)}>
            Annuler
          </Button>
          <Button
            variant="destructive"
            size="sm"
            loading={deletingId === confirmDeleteId}
            onClick={() => confirmDeleteId && handleDelete(confirmDeleteId)}
          >
            Supprimer
          </Button>
        </div>
      </Dialog>
    </motion.div>
  )
}
