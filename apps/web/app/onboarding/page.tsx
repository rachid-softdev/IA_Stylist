'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { UploadZone } from '@/components/ui/upload-zone'
import { ArrowRight, Camera } from 'lucide-react'
import { useUpload } from '@/hooks/use-upload'
import { useToastStore } from '@/stores/toast-store'

export default function OnboardingPage() {
  const [step, setStep] = useState(1)
  const [photos, setPhotos] = useState<string[]>([])
  const { addToast } = useToastStore()

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-base px-4">
      <div className="w-full max-w-md">
        {/* Progress dots */}
        <div className="mb-8 flex justify-center gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1 w-8 rounded-full transition-all duration-300 ${
                s <= step ? 'bg-accent-primary' : 'bg-bg-elevated'
              }`}
            />
          ))}
        </div>

        {step === 1 && (
          <div className="text-center animate-fade-in">
            <Camera className="mx-auto h-8 w-8 text-accent-primary" />
            <h1 className="mt-4 font-display text-2xl text-text-primary">
              Votre studio en 3 photos
            </h1>
            <p className="mt-2 text-sm text-text-secondary">
              Uploadez 3 photos pour obtenir les meilleurs résultats
            </p>
            <div className="mt-6 grid grid-cols-3 gap-3">
              {['Face', '3/4', 'Corps entier'].map((label) => (
                <div
                  key={label}
                  className="aspect-[3/4] rounded-lg border border-dashed border-border-default bg-bg-surface p-2 flex items-center justify-center cursor-pointer hover:border-accent-primary"
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
          </div>
        )}

        {step === 2 && (
          <div className="text-center animate-fade-in">
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
                    className="aspect-square rounded-lg border border-border-default bg-bg-surface flex items-center justify-center cursor-pointer hover:border-accent-primary p-4"
                  >
                    <span className="text-sm text-text-secondary">{item}</span>
                  </div>
                ),
              )}
            </div>
            <Button
              className="mt-8"
              size="lg"
              iconRight={<ArrowRight className="h-4 w-4" />}
              onClick={() => setStep(3)}
            >
              Essayer ce vêtement
            </Button>
          </div>
        )}

        {step === 3 && (
          <div className="text-center animate-fade-in">
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
            <p className="mt-6 text-sm text-accent-primary">
              Effet &quot;wow&quot; garanti — créez votre compte pour télécharger
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
