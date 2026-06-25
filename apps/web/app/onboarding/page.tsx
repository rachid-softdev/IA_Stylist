'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { ArrowRight, ArrowLeft, Camera, Check, ImageUp } from 'lucide-react'
import { api } from '@/lib/api'
import { useToastStore } from '@/stores/toast-store'

const stepVariants = {
  enter: { opacity: 0, y: 20 },
  center: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
}

const photoSlots = [
  { key: 'face', label: 'Visage' },
  { key: 'profile', label: 'Profil' },
  { key: 'fullbody', label: 'Corps entier' },
]

const garments = [
  { id: 'tshirt-blanc', name: 'T-shirt Blanc', sku: 'VFS-001' },
  { id: 'robe-noire', name: 'Robe Noire', sku: 'VFS-002' },
  { id: 'jean-slim', name: 'Jean Slim', sku: 'VFS-003' },
  { id: 'veste-blazer', name: 'Veste Blazer', sku: 'VFS-004' },
]

export default function OnboardingPage() {
  const router = useRouter()
  const { addToast } = useToastStore()
  const [step, setStep] = useState(1)

  // Step 1: photo uploads
  const [photoFiles, setPhotoFiles] = useState<Record<string, File | null>>({
    face: null,
    profile: null,
    fullbody: null,
  })
  const [photoPreviews, setPhotoPreviews] = useState<Record<string, string>>({
    face: '',
    profile: '',
    fullbody: '',
  })
  const [uploading, setUploading] = useState(false)
  const [photoKeys, setPhotoKeys] = useState<Record<string, string>>({
    face: '',
    profile: '',
    fullbody: '',
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [activeSlot, setActiveSlot] = useState<string | null>(null)

  // Step 2: garment selection
  const [selectedGarment, setSelectedGarment] = useState<string | null>(null)

  // Step 3: generation
  const [generating, setGenerating] = useState(false)
  const [resultUrl, setResultUrl] = useState<string | null>(null)

  const handleFileSelect = (slotKey: string, file: File) => {
    const preview = URL.createObjectURL(file)
    setPhotoFiles((prev) => ({ ...prev, [slotKey]: file }))
    setPhotoPreviews((prev) => ({ ...prev, [slotKey]: preview }))
  }

  const handleSlotClick = (slotKey: string) => {
    setActiveSlot(slotKey)
    fileInputRef.current?.click()
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && activeSlot) {
      handleFileSelect(activeSlot, file)
    }
    e.target.value = ''
  }

  const handleUpload = async () => {
    setUploading(true)
    try {
      const keys: Record<string, string> = {}
      for (const slot of photoSlots) {
        const file = photoFiles[slot.key]
        if (!file) continue
        const result = await api.uploadFile(file, 'onboarding')
        keys[slot.key] = result.r2_key
      }
      setPhotoKeys(keys)
      addToast({ type: 'success', title: 'Photos uploadées', message: 'Passons à l\'étape suivante !' })
      setStep(2)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erreur lors de l\'upload'
      addToast({ type: 'error', title: 'Erreur', message })
    } finally {
      setUploading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setStep(3)
    try {
      const res = await api.post<{ result_url: string }>('/onboarding/generate', {
        photos: photoKeys,
        garment_sku: selectedGarment,
      })
      setResultUrl(res.data.result_url)
      addToast({ type: 'success', title: 'Look créé !', message: 'Votre premier look est prêt.' })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erreur lors de la génération'
      addToast({ type: 'error', title: 'Erreur', message })
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-base px-4">
      <div className="w-full max-w-md">
        {/* Progress dots */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="mb-8 flex justify-center gap-2"
        >
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1 w-8 rounded-full transition-all duration-300 ${
                s <= step ? 'bg-accent-primary' : 'bg-bg-elevated'
              }`}
            />
          ))}
        </motion.div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileInputChange}
        />

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              variants={stepVariants}
              initial="enter"
              animate="center"
              exit="exit"
              className="text-center"
            >
              <Camera className="mx-auto h-8 w-8 text-accent-primary" />
              <h1 className="mt-4 font-display text-2xl text-text-primary">
                Votre studio en 3 photos
              </h1>
              <p className="mt-2 text-sm text-text-secondary">
                Uploadez 3 photos pour obtenir les meilleurs résultats
              </p>
              <div className="mt-6 grid grid-cols-3 gap-3">
                {photoSlots.map((slot) => (
                  <button
                    key={slot.key}
                    type="button"
                    onClick={() => handleSlotClick(slot.key)}
                    className="group aspect-[3/4] rounded-lg border border-dashed border-border-default bg-bg-surface p-2 flex flex-col items-center justify-center gap-2 hover:border-accent-primary transition-colors overflow-hidden"
                  >
                    {photoPreviews[slot.key] ? (
                      <img
                        src={photoPreviews[slot.key]}
                        alt={slot.label}
                        className="h-full w-full object-cover rounded"
                      />
                    ) : (
                      <>
                        <ImageUp className="h-6 w-6 text-text-tertiary group-hover:text-accent-primary transition-colors" />
                        <span className="text-xs text-text-tertiary">{slot.label}</span>
                      </>
                    )}
                  </button>
                ))}
              </div>
              <Button
                className="mt-8"
                size="lg"
                disabled={!photoSlots.every((s) => photoFiles[s.key])}
                loading={uploading}
                iconRight={!uploading ? <ArrowRight className="h-4 w-4" /> : undefined}
                onClick={handleUpload}
              >
                {uploading ? 'Upload en cours...' : 'Continuer'}
              </Button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              variants={stepVariants}
              initial="enter"
              animate="center"
              exit="exit"
              className="text-center"
            >
              <h1 className="font-display text-2xl text-text-primary">
                Choisissez votre premier vêtement
              </h1>
              <p className="mt-2 text-sm text-text-secondary">
                Sélectionnez parmi notre catalogue démo
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                {garments.map((item) => {
                  const isSelected = selectedGarment === item.id
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setSelectedGarment(item.id)}
                      className={`relative aspect-square rounded-lg border-2 flex items-center justify-center p-4 transition-all ${
                        isSelected
                          ? 'border-accent-primary bg-accent-primary/10'
                          : 'border-border-default bg-bg-surface hover:border-accent-primary'
                      }`}
                    >
                      {isSelected && (
                        <div className="absolute top-2 right-2 h-5 w-5 rounded-full bg-accent-primary flex items-center justify-center">
                          <Check className="h-3 w-3 text-text-inverse" />
                        </div>
                      )}
                      <span className={`text-sm ${isSelected ? 'text-accent-primary font-medium' : 'text-text-secondary'}`}>
                        {item.name}
                      </span>
                    </button>
                  )
                })}
              </div>
              <div className="mt-8 flex gap-3 justify-center">
                <Button
                  variant="ghost"
                  size="md"
                  iconLeft={<ArrowLeft className="h-4 w-4" />}
                  onClick={() => setStep(1)}
                >
                  Retour
                </Button>
                <Button
                  size="lg"
                  disabled={!selectedGarment}
                  loading={generating}
                  iconRight={!generating ? <ArrowRight className="h-4 w-4" /> : undefined}
                  onClick={handleGenerate}
                >
                  {generating ? 'Génération...' : 'Essayer ce vêtement'}
                </Button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              variants={stepVariants}
              initial="enter"
              animate="center"
              exit="exit"
              className="text-center"
            >
              {resultUrl ? (
                <>
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-accent-primary/10">
                    <Check className="h-8 w-8 text-accent-primary" />
                  </div>
                  <h1 className="mt-4 font-display text-2xl text-text-primary">
                    Votre look est prêt !
                  </h1>
                  <div className="mt-6 mx-auto max-w-xs aspect-[3/4] rounded-lg overflow-hidden border border-border-default">
                    <img
                      src={resultUrl}
                      alt="Votre look généré"
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <Button
                    className="mt-6"
                    size="lg"
                    iconRight={<ArrowRight className="h-4 w-4" />}
                    onClick={() => router.push('/studio')}
                  >
                    Aller au Studio
                  </Button>
                </>
              ) : (
                <>
                  <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-accent-primary/10">
                    <div className="h-10 w-10 animate-spin-slow rounded-full border-2 border-border-default border-t-accent-primary" />
                  </div>
                  <h1 className="mt-6 font-display text-2xl text-text-primary">
                    Nous préparons votre look...
                  </h1>
                  <p className="mt-2 text-sm text-text-secondary">
                    Cela prend environ 30 secondes
                  </p>
                  <div className="mt-8 aspect-[3/4] rounded-lg bg-bg-surface border border-border-default flex items-center justify-center">
                    <span className="text-sm text-text-tertiary">Génération en cours...</span>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
