'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useStudioStore } from '@/stores/studio-store'
import { useToastStore } from '@/stores/toast-store'
import { PhotoUploadZone } from '@/components/studio/photo-upload'
import { GarmentSelector } from '@/components/studio/garment-selector'
import { CategorySelect } from '@/components/studio/category-select'
import { GenerateButton } from '@/components/studio/generate-button'
import { ResultDisplay } from '@/components/studio/result-display'
import { JobProgress } from '@/components/studio/job-progress'
import { CatalogBrowser } from '@/components/studio/catalog-browser'
import { OnboardingTour } from '@/components/studio/onboarding-tour'
import { useGenerationJob } from '@/hooks/use-generation-job'
import { api } from '@/lib/api'
import type { GarmentCategory, JobStatus } from '@vfs/shared-types'
import { X, Package, Plus } from 'lucide-react'

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

    // Batch
    batchMode,
    batchGarments,
    batchJobs,
    isBatchGenerating,
    toggleBatchMode,
    addBatchGarment,
    removeBatchGarment,
    clearBatchGarments,
    setBatchJobs,
    updateBatchJob,
    resetBatch,
  } = useStudioStore()

  const { addToast } = useToastStore()
  const [photoError, setPhotoError] = useState<string | null>(null)
  const [showBatchCatalog, setShowBatchCatalog] = useState(false)

  const handlePhotoUpload = useCallback((photo: { url: string; r2_key: string }) => {
    setActivePhoto(photo)
    setPhotoError(null)
  }, [setActivePhoto])

  const handleGarmentSelect = useCallback((garment: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  } | null) => {
    setSelectedGarment(garment)
    if (garment?.category) {
      setCategory(garment.category)
    }
  }, [setSelectedGarment, setCategory])

  const handleCancelGeneration = useCallback(async () => {
    if (!currentJobId && !isGenerating) return
    try {
      await api.post(`/generate/jobs/${currentJobId}/cancel`)
      addToast({ type: 'info', title: 'Génération annulée', message: 'Votre crédit a été conservé.' })
      reset()
    } catch {
      addToast({ type: 'error', title: 'Erreur', message: 'Impossible d\'annuler la génération' })
    }
  }, [currentJobId, isGenerating, addToast, reset])

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

  const handleBatchGenerate = useCallback(async () => {
    if (!activePhoto || batchGarments.length === 0) {
      addToast({
        type: 'warning',
        title: 'Photo et vêtements requis',
        message: 'Uploadez votre photo et sélectionnez au moins un vêtement',
      })
      return
    }

    try {
      const res = await api.post<{ jobs: { garment_id: string; job_id: string; status: string }[] }>('/generate/lookbook', {
        model_photo_id: activePhoto.r2_key,
        garments: batchGarments.map((g) => ({
          id: g.id,
          image_url: g.image_url,
          category: g.category,
          name: g.name,
        })),
      })

      const jobs = res.data.jobs.map((j) => ({
        garmentId: j.garment_id,
        garmentName: batchGarments.find((g) => g.id === j.garment_id)?.name || '',
        jobId: j.job_id,
        status: j.status as JobStatus,
        resultUrl: null,
        errorMessage: null,
      }))
      setBatchJobs(jobs)

      addToast({
        type: 'info',
        title: 'Lookbook lancé',
        message: `${jobs.length} looks en cours de création...`,
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Une erreur est survenue'
      addToast({
        type: 'error',
        title: 'Échec de la génération du lookbook',
        message,
      })
      resetBatch()
    }
  }, [activePhoto, batchGarments, setBatchJobs, addToast, resetBatch])

  // Watch batch jobs
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

  // Keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Cmd/Ctrl + Enter → generate
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault()
        if (isReady && !isGenerating && !resultUrl) {
          handleGenerate()
        }
      }
      // Escape → reset result
      if (e.key === 'Escape' && resultUrl) {
        reset()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isReady, isGenerating, resultUrl, handleGenerate, reset])

  // Poll batch jobs
  useEffect(() => {
    if (!isBatchGenerating || batchJobs.length === 0) return

    const allDone = batchJobs.every((j) => j.status === 'done' || j.status === 'error')
    if (allDone) return

    const interval = setInterval(async () => {
      for (const job of batchJobs) {
        if (job.status === 'done' || job.status === 'error') continue
        try {
          const res = await api.get<{ status: string; result_url?: string }>(`/generate/jobs/${job.jobId}`)
          if (res.data.status === 'done' && res.data.result_url) {
            updateBatchJob(job.garmentId, { status: 'done', resultUrl: res.data.result_url })
          } else if (res.data.status === 'error') {
            updateBatchJob(job.garmentId, { status: 'error', errorMessage: 'Échec de la génération' })
          } else {
            updateBatchJob(job.garmentId, { status: res.data.status as JobStatus })
          }
        } catch {
          updateBatchJob(job.garmentId, { status: 'error', errorMessage: 'Erreur de suivi' })
        }
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [isBatchGenerating, batchJobs, updateBatchJob])

  const batchAllDone = batchJobs.length > 0 && batchJobs.every((j) => j.status === 'done' || j.status === 'error')
  const batchSuccessCount = batchJobs.filter((j) => j.status === 'done').length
  const batchErrorCount = batchJobs.filter((j) => j.status === 'error').length

  const step = !activePhoto ? 1 : !selectedGarment && !batchMode ? 2 : 3

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

      {/* Step indicator */}
      <motion.div variants={item} className="mb-8 flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`flex h-6 w-6 items-center justify-center rounded-full text-2xs font-medium transition-all duration-300 ${
                s <= step
                  ? 'bg-accent-primary text-text-inverse'
                  : 'bg-bg-elevated text-text-tertiary'
              }`}
            >
              {s}
            </div>
            <span
              className={`text-xs transition-all duration-300 ${
                s === step ? 'text-text-primary font-medium' : 'text-text-tertiary'
              }`}
            >
              {s === 1 ? 'Photo' : s === 2 ? 'Vêtement' : 'Génération'}
            </span>
            {s < 3 && <div className="mx-1 h-px w-6 bg-border-subtle" aria-hidden />}
          </div>
        ))}
      </motion.div>

      {/* Batch mode toggle */}
      <motion.div variants={item} className="mb-6">
        <div className="flex items-center gap-3 rounded-lg border border-border-default bg-bg-surface p-3">
          <button
            onClick={toggleBatchMode}
            className={`relative flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
              batchMode
                ? 'bg-accent-primary text-text-inverse shadow-sm'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {batchMode ? 'Mode lot actif' : 'Activer le mode lot'}
          </button>
          {batchMode && (
            <p className="text-2xs text-text-tertiary">
              Sélectionnez plusieurs vêtements pour générer un lookbook complet
            </p>
          )}
        </div>
      </motion.div>

      {/* Main canvas */}
      <motion.div variants={item} className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
        {/* Left: Uploads */}
        <div className="space-y-6">
          <div data-tour="photo-upload">
            <PhotoUploadZone
              preview={activePhoto?.url || null}
              onUpload={handlePhotoUpload}
              error={photoError}
            />
          </div>

          <motion.div
            animate={{
              opacity: activePhoto ? 1 : 0.45,
              height: 'auto',
            }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            {batchMode ? (
              <div className="space-y-3">
                <h3 className="text-sm font-heading tracking-wide text-text-secondary uppercase">
                  Vêtements ({batchGarments.length})
                </h3>

                {/* Selected garments list */}
                {batchGarments.length > 0 && (
                  <div className="space-y-2">
                    {batchGarments.map((g) => (
                      <div key={g.id} className="flex items-center gap-3 rounded-lg border border-border-default bg-bg-surface p-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded bg-bg-elevated">
                          <Package className="h-5 w-5 text-text-tertiary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-text-primary truncate">{g.name}</p>
                          <p className="text-2xs text-text-tertiary">{g.category}</p>
                        </div>
                        <button
                          onClick={() => removeBatchGarment(g.id)}
                          className="rounded p-1 text-text-tertiary hover:text-status-error transition-colors"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add more button */}
                <button
                  onClick={() => setShowBatchCatalog(true)}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-border-default p-4 text-center transition-all hover:border-accent-primary hover:bg-bg-overlay"
                >
                  <Plus className="h-4 w-4 text-text-tertiary" />
                  <span className="text-sm text-text-secondary">
                    {batchGarments.length > 0 ? 'Ajouter des vêtements' : 'Sélectionner des vêtements'}
                  </span>
                </button>

                {batchGarments.length > 0 && (
                  <button
                    onClick={clearBatchGarments}
                    className="text-xs text-text-tertiary hover:text-text-secondary"
                  >
                    Tout effacer
                  </button>
                )}
              </div>
            ) : (
              <div data-tour="garment-select">
                <GarmentSelector
                  selected={selectedGarment}
                  onSelect={handleGarmentSelect}
                />
              </div>
            )}
          </motion.div>

          {selectedGarment && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            >
              <div data-tour="category-select">
                <CategorySelect
                  value={selectedCategory}
                  onChange={setCategory}
                />
              </div>
            </motion.div>
          )}
        </div>

        {/* Right: Result */}
        <div className="space-y-6">
          {batchMode ? (
            <>
              {isBatchGenerating ? (
                <div className="space-y-4">
                  {batchJobs.map((job) => (
                    <div key={job.garmentId} className="rounded-lg border border-border-default bg-bg-surface p-4">
                      <p className="text-sm font-medium text-text-primary mb-2">{job.garmentName}</p>
                      {job.jobId && (
                        <JobProgress
                          jobId={job.jobId}
                          status={job.status}
                          onCancel={handleCancelGeneration}
                        />
                      )}
                    </div>
                  ))}
                  {batchAllDone && (
                    <button onClick={resetBatch} className="text-sm text-accent-primary hover:underline">
                      Recommencer
                    </button>
                  )}
                </div>
              ) : batchAllDone ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-heading tracking-wide text-text-secondary uppercase">
                      Résultats
                    </h3>
                    <div className="flex gap-3 text-2xs">
                      <span className="text-status-success">{batchSuccessCount} réussi{batchSuccessCount > 1 ? 's' : ''}</span>
                      {batchErrorCount > 0 && (
                        <span className="text-status-error">{batchErrorCount} échec{batchErrorCount > 1 ? 's' : ''}</span>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {batchJobs.map((job) => (
                      <div key={job.garmentId} className="rounded-lg border border-border-default overflow-hidden">
                        {job.status === 'done' && job.resultUrl ? (
                          <img src={job.resultUrl} alt={job.garmentName} loading="lazy" className="w-full aspect-[3/4] object-cover" />
                        ) : (
                          <div className="flex aspect-[3/4] items-center justify-center bg-bg-elevated p-4 text-center">
                            <p className="text-2xs text-status-error">{job.errorMessage || 'Échec'}</p>
                          </div>
                        )}
                        <div className="border-t border-border-subtle p-2">
                          <p className="text-2xs font-medium text-text-primary truncate">{job.garmentName}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={resetBatch} className="text-sm text-accent-primary hover:underline">
                      Nouveau lookbook
                    </button>
                    <button onClick={reset} className="text-sm text-text-tertiary hover:text-text-secondary">
                      Nouvelle photo
                    </button>
                  </div>
                </div>
              ) : errorMessage ? (
                <div className="rounded-lg border border-status-error/30 bg-status-error/5 p-6 text-center">
                  <p className="text-status-error font-medium">Génération échouée</p>
                  <p className="mt-2 text-sm text-text-secondary">{errorMessage}</p>
                  <button onClick={reset} className="mt-4 text-sm text-accent-primary hover:underline">
                    Réessayer
                  </button>
                </div>
              ) : (
                <motion.div
                  className="flex h-full min-h-[300px] items-center justify-center rounded-lg border border-dashed p-8 text-center"
                  animate={{
                    borderColor: activePhoto && batchGarments.length > 0
                      ? 'var(--accent-primary)'
                      : 'var(--border-default)',
                    opacity: activePhoto && batchGarments.length > 0 ? 1 : 0.6,
                  }}
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                >
                  <div>
                    <p className="text-text-secondary">
                      {!activePhoto
                        ? 'Uploadez votre photo pour commencer'
                        : batchGarments.length === 0
                          ? 'Sélectionnez des vêtements'
                          : `Prêt à générer ${batchGarments.length} look${batchGarments.length > 1 ? 's' : ''}`
                      }
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Batch generate button */}
              {!isBatchGenerating && !batchAllDone && (
                <motion.div
                  className="flex flex-col items-center gap-2"
                  animate={{
                    opacity: activePhoto && batchGarments.length > 0 ? 1 : 0.5,
                    y: activePhoto && batchGarments.length > 0 ? 0 : 4,
                  }}
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                >
                  <GenerateButton
                    onClick={handleBatchGenerate}
                    disabled={!activePhoto || batchGarments.length === 0 || isBatchGenerating}
                    credits={batchGarments.length}
                  />
                </motion.div>
              )}
            </>
          ) : (
            <>
              {isGenerating && currentJobId ? (
                <div data-tour="result-area">
                  <JobProgress jobId={currentJobId} status={jobStatus} onCancel={handleCancelGeneration} />
                </div>
              ) : resultUrl ? (
                <div data-tour="result-area">
                  <ResultDisplay
                    imageUrl={resultUrl}
                    metadata={resultMetadata}
                    onTryAgain={reset}
                    jobId={currentJobId}
                  />
                </div> errorMessage ? (
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
                <motion.div
                  className="flex h-full min-h-[300px] items-center justify-center rounded-lg border border-dashed p-8 text-center"
                  animate={{
                    borderColor: isReady
                      ? 'var(--accent-primary)'
                      : 'var(--border-default)',
                    opacity: isReady ? 1 : 0.6,
                  }}
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                >
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
                </motion.div>
              )}

              {/* Generate button */}
              {!isGenerating && !resultUrl && (
                <motion.div
                  className="flex flex-col items-center gap-2"
                  data-tour="generate-button"
                  animate={{
                    opacity: isReady ? 1 : 0.5,
                    y: isReady ? 0 : 4,
                  }}
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                >
                  <GenerateButton
                    onClick={handleGenerate}
                    disabled={!isReady || isGenerating}
                    credits={1}
                  />
                  {isReady && (
                    <kbd className="hidden font-mono text-2xs text-text-tertiary md:inline-block">
                      ⌘⏎ / Ctrl+⏎ pour générer
                    </kbd>
                  )}
                </motion.div>
              )}
            </>
          )}
        </div>
      </motion.div>

      {/* Catalog browser for batch mode */}
      <CatalogBrowser
        open={showBatchCatalog}
        onClose={() => setShowBatchCatalog(false)}
        onSelect={(garment) => {
          addBatchGarment({ ...garment })
          setShowBatchCatalog(false)
        }}
        multiSelect
        selectedIds={batchGarments.map((g) => g.id)}
        onSelectMultiple={(garments) => {
          garments.forEach((g) => addBatchGarment(g))
          setShowBatchCatalog(false)
        }}
      />

      <OnboardingTour enabled={!isGenerating && !resultUrl && !activePhoto && !selectedGarment} />
    </motion.div>
  )
}
