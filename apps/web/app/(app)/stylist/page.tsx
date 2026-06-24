'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar } from '@/components/ui/avatar'
import { Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'

interface StylistProfile {
  status: 'no_profile' | 'complete' | 'analyzing'
  data?: {
    metadata?: {
      morphologie?: string
      teint?: string
      style?: string
    }
  }
}

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}
export default function StylistPage() {
  const { addToast } = useToastStore()

  const { data: profile, isLoading } = useQuery<StylistProfile>({
    queryKey: ['stylist-profile'],
    queryFn: async () => {
      const res = await api.get<StylistProfile>('/stylist/profile')
      return res.data
    },
  })

  const handleAnalyze = async () => {
    try {
      await api.post('/stylist/analyze')
      addToast({ type: 'success', title: 'Analyse lancée', message: 'Votre profil est en cours d\'analyse' })
    } catch {
      addToast({ type: 'error', title: 'Erreur', message: 'Analyse impossible' })
    }
  }

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Styliste IA</h1>
        <p className="mt-1 text-text-secondary">Conseils personnalisés basés sur votre morphologie</p>
      </motion.div>

      {/* Profile Summary */}
      <motion.div variants={item}>
        <Card className="mb-8">
          <div className="flex items-center gap-4">
            <Avatar size="lg" fallback="P" />
            <div>
              <h2 className="font-heading text-lg text-text-primary">Votre profil</h2>
              {profile?.status === 'no_profile' ? (
                <p className="mt-1 text-sm text-text-secondary">
                  Uploadez 3 photos pour activer le Styliste IA
                </p>
              ) : (
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="rounded-full border border-border-default px-3 py-1 text-xs text-text-secondary">
                    Morphologie: {profile?.data?.metadata?.morphologie || 'À analyser'}
                  </span>
                  <span className="rounded-full border border-border-default px-3 py-1 text-xs text-text-secondary">
                    Teint: {profile?.data?.metadata?.teint || 'À analyser'}
                  </span>
                </div>
              )}
              <button
                onClick={handleAnalyze}
                className="mt-3 flex items-center gap-1.5 text-sm text-accent-primary hover:underline"
              >
                <Sparkles className="h-3.5 w-3.5" />
                Analyser mon profil
              </button>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Recommendations */}
      <motion.div variants={item} className="mb-6">
        <h3 className="mb-4 font-heading text-base text-text-primary">
          Mes recommandations
        </h3>
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Skeleton variant="card" />
            <Skeleton variant="card" />
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-border-default p-8 text-center">
            <p className="text-sm text-text-secondary">
              Générez votre premier look pour obtenir des recommandations personnalisées
            </p>
          </div>
        )}
      </motion.div>

      {/* Suggested outfits */}
      <motion.div variants={item}>
        <h3 className="mb-4 font-heading text-base text-text-primary">
          Outfits suggérés
        </h3>
        <div className="rounded-lg border border-dashed border-border-default p-8 text-center">
          <p className="text-sm text-text-secondary">
            Complétez votre dressing pour débloquer les suggestions d&apos;outfits
          </p>
        </div>
      </motion.div>

      {/* Feedback */}
      <motion.div variants={item} className="mt-8 flex items-center justify-center gap-4 border-t border-border-subtle pt-6">
        <span className="text-sm text-text-tertiary">Ces suggestions sont-elles utiles ?</span>
        <button
          onClick={() => addToast({ type: 'success', title: 'Merci !', message: 'Feedback enregistré' })}
          className="rounded p-2 text-text-tertiary hover:bg-bg-overlay hover:text-accent-primary transition-colors duration-150"
        >
          <ThumbsUp className="h-4 w-4" />
        </button>
        <button
          onClick={() => addToast({ type: 'info', title: 'Merci', message: 'Nous allons nous améliorer' })}
          className="rounded p-2 text-text-tertiary hover:bg-bg-overlay hover:text-accent-primary transition-colors duration-150"
        >
          <ThumbsDown className="h-4 w-4" />
        </button>
      </motion.div>
    </motion.div>
  )
}
