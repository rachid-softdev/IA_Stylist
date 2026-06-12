'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { UploadZone } from '@/components/ui/upload-zone'
import { ArrowRight, ArrowLeft, Camera } from 'lucide-react'
import { useUpload } from '@/hooks/use-upload'
import { useToastStore } from '@/stores/toast-store'

const stepVariants = {
  enter: { opacity: 0, y: 20 },
  center: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
}

export default function OnboardingPage() {
  const [step, setStep] = useState(1)
  const [photos, setPhotos] = useState<string[]>([])
  const { addToast } = useToastStore()

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
                {['Visage', 'Profil', 'Corps entier'].map((label) => (
                  <div
                    key={label}
                    className="aspect-[3/4] rounded-lg border border-dashed border-border-default bg-bg-surface p-2 flex items-center justify-center hover:border-accent-primary transition-colors"
                  >
                    <span className="text-xs text-text-tertiary">{label}</span>
                  </div>
                ))}
              </div>
              <Button
                className="mt-8"
                size="lg"
                iconRight={<ArrowRight className="h-4 w-4" />}
                onClick={() => setStep(2)}
              >
                Continuer
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
                {['T-shirt Blanc', 'Robe Noire', 'Jean Slim', 'Veste Blazer'].map(
                  (item) => (
                    <div
                      key={item}
                      className="aspect-square rounded-lg border border-border-default bg-bg-surface flex items-center justify-center hover:border-accent-primary p-4 transition-colors"
                    >
                      <span className="text-sm text-text-secondary">{item}</span>
                    </div>
                  ),
                )}
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
                  iconRight={<ArrowRight className="h-4 w-4" />}
                  onClick={() => setStep(3)}
                >
                  Essayer ce vêtement
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
                <span className="text-sm text-text-tertiary">Votre résultat apparaîtra ici</span>
              </div>
              <div className="mt-6">
                <Button
                  variant="ghost"
                  size="sm"
                  iconLeft={<ArrowLeft className="h-4 w-4" />}
                  onClick={() => setStep(2)}
                >
                  Retour
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
