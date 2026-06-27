'use client'

import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Download, RefreshCw, Film } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'
import { useSwipe } from '@/hooks/use-swipe'

interface ResultDisplayProps {
  imageUrl: string
  metadata: Record<string, unknown> | null
  onTryAgain: () => void
  jobId: string | null
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
}

export function ResultDisplay({ imageUrl, metadata: _metadata, onTryAgain, jobId, onSwipeLeft, onSwipeRight }: ResultDisplayProps) {
  const { addToast } = useToastStore()
  const swipeHandlers = useSwipe({ onSwipeLeft, onSwipeRight })

  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `vfs-tryon-${jobId?.slice(0, 8)}.webp`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      addToast({
        type: 'success',
        title: 'Image téléchargée',
        message: 'Votre look a été enregistré',
      })
    } catch {
      addToast({
        type: 'error',
        title: 'Erreur',
        message: 'Impossible de télécharger l\'image',
      })
    }
  }

  return (
    <div className="animate-result-reveal" {...swipeHandlers}>
      <div className="relative aspect-[3/4] overflow-hidden rounded-lg border border-border-default bg-bg-surface">
        <Image
          src={imageUrl}
          alt="Try-on result"
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, 50vw"
        />

        {/* Overlay actions */}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-bg-base/90 via-bg-base/40 to-transparent p-4 pt-12">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <Button
              variant="secondary"
              size="sm"
              iconLeft={<Download className="h-3.5 w-3.5" />}
              onClick={handleDownload}
            >
              Télécharger
            </Button>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                iconLeft={<Film className="h-3.5 w-3.5" />}
                onClick={() => {
                  addToast({
                    type: 'info',
                    title: 'Vidéo',
                    message: 'Génération vidéo bientôt disponible (3 crédits)',
                  })
                }}
              >
                Vidéo
              </Button>
              <Button
                variant="ghost"
                size="sm"
                iconLeft={<RefreshCw className="h-3.5 w-3.5" />}
                onClick={onTryAgain}
              >
                Nouveau
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
