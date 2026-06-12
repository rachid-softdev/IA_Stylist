'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useStudioStore } from '@/stores/studio-store'
import { useToastStore } from '@/stores/toast-store'
import { PhotoUploadZone } from '@/components/studio/photo-upload'
import { GarmentSelector } from '@/components/studio/garment-selector'
import { CategorySelect } from '@/components/studio/category-select'
import { GenerateButton } from '@/components/studio/generate-button'
import { ResultDisplay } from '@/components/studio/result-display'
import { JobProgress } from '@/components/studio/job-progress'
import { useGenerationJob } from '@/hooks/use-generation-job'
import { api } from '@/lib/api'
import type { GarmentCategory, JobStatus } from '@vfs/shared-types'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function StudioPage() {
  const {
    activePhoto,
    selectedGarment,
    selectedCategory,
    currentJobId,
    jobStatus,
    resultUrl,
    resultMetadata,
    errorMessage,
    isGenerating,
    setActivePhoto,
    setSelectedGarment,
    setCategory,
    setJobId,
    setJobStatus,
    setResult,
    setError,
    reset,
  } = useStudioStore()

  const { addToast } = useToastStore()
  const [photoError, setPhotoError] = useState<string | null>(null)

  const handlePhotoUpload = useCallback((photo: { url: string; r2_key: string }) => {
    setActivePhoto(photo)
    setPhotoError(null)
  }, [setActivePhoto])

  const handleGarmentSelect = useCallback((garment: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  }) => {
    setSelectedGarment(garment)
    if (garment.category) {
      setCategory(garment.category)
    }
  }, [setSelectedGarment, setCategory])

  const handleGenerate = useCallback(async () => {
    if (!activePhoto || !selectedGarment) {
      addToast({
        type: 'warning',
        title: 'Photo et vêtement requis',
        message: 'Uploadez votre photo et choisissez un vêtement',
      })
      return
    }

    try {
      const res = await api.post<{ job_id: string; status: string }>('/generate/try-on', {
        model_photo_id: activePhoto.r2_key,
        garment_image: selectedGarment.image_url,
        garment_id: selectedGarment.id,
        category: selectedCategory || selectedGarment.category,
      })

      setJobId(res.data.job_id)

      addToast({
        type: 'info',
        title: 'Génération lancée',
        message: 'Votre look est en cours de création...',
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Une erreur est survenue'
      setError(message)
      addToast({
        type: 'error',
        title: 'Échec de la génération',
        message,
      })
    }
  }, [activePhoto, selectedGarment, selectedCategory, setJobId, setError, addToast])

  // Watch job status
  useGenerationJob(
    currentJobId,
    (status: JobStatus) => setJobStatus(status),
    (url: string, metadata?: Record<string, unknown>) => {
      setResult(url, metadata)
      addToast({
        type: 'success',
        title: 'Look généré !',
        message: 'Votre shooting est prêt',
      })
    },
    (message: string) => {
      setError(message)
      addToast({
        type: 'error',
        title: 'Génération échouée',
        message,
      })
    },
  )

  const isReady = !!activePhoto && !!selectedGarment

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">
          Studio
        </h1>
        <p className="mt-1 text-text-secondary">
          Votre shooting photo en 60 secondes
        </p>
      </motion.div>

      {/* Main canvas */}
      <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
        {/* Left: Uploads */}
        <div className="space-y-6">
          <PhotoUploadZone
            preview={activePhoto?.url || null}
            onUpload={handlePhotoUpload}
            error={photoError}
          />

          <GarmentSelector
            selected={selectedGarment}
            onSelect={handleGarmentSelect}
          />

          <CategorySelect
            value={selectedCategory}
            onChange={setCategory}
          />
        </div>

        {/* Right: Result */}
        <div className="space-y-6">
          {isGenerating && currentJobId ? (
            <JobProgress jobId={currentJobId} status={jobStatus} />
          ) : resultUrl ? (
            <ResultDisplay
              imageUrl={resultUrl}
              metadata={resultMetadata}
              onTryAgain={reset}
              jobId={currentJobId}
            />
          ) : errorMessage ? (
            <div className="rounded-lg border border-status-error/30 bg-status-error/5 p-6 text-center">
              <p className="text-status-error font-medium">Génération échouée</p>
              <p className="mt-2 text-sm text-text-secondary">{errorMessage}</p>
              <p className="mt-1 text-sm text-text-tertiary">
                Vos crédits vous ont été remboursés
              </p>
              <button
                onClick={reset}
                className="mt-4 text-sm text-accent-primary hover:underline"
              >
                Réessayer
              </button>
            </div>
          ) : (
            <div className="flex h-full min-h-[300px] items-center justify-center rounded-lg border border-dashed border-border-default p-8 text-center">
              <div>
                <p className="text-text-secondary">
                  {!activePhoto
                    ? 'Uploadez votre photo pour commencer'
                    : !selectedGarment
                      ? 'Choisissez un vêtement'
                      : 'Prêt à générer votre look'
                  }
                </p>
              </div>
            </div>
          )}

          {/* Generate button */}
          {!isGenerating && !resultUrl && (
            <div className="flex justify-center">
              <GenerateButton
                onClick={handleGenerate}
                disabled={!isReady}
                credits={1}
              />
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
