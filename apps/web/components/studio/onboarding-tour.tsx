'use client'

import { useState, useEffect } from 'react'
import Joyride, { type Step, type CallBackProps, STATUS } from 'react-joyride'
import { useQueryClient } from '@tanstack/react-query'

const TOUR_STORAGE_KEY = 'vfs-tour-completed'

interface OnboardingTourProps {
  /** Only mount when the user is on the studio page with no prior generation history */
  enabled: boolean
}

export function OnboardingTour({ enabled }: OnboardingTourProps) {
  const [run, setRun] = useState(false)
  const queryClient = useQueryClient()

  useEffect(() => {
    if (enabled) {
      const completed = localStorage.getItem(TOUR_STORAGE_KEY)
      if (!completed) {
        // Small delay so the page renders first
        const timer = setTimeout(() => setRun(true), 800)
        return () => clearTimeout(timer)
      }
    }
  }, [enabled])

  const handleJoyrideCallback = async (data: CallBackProps) => {
    const { status, type } = data
    if (type === 'tour:end' || status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      localStorage.setItem(TOUR_STORAGE_KEY, 'true')
      setRun(false)

      // Optionally persist to backend
      try {
        await fetch('/v1/brands/me', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })
      } catch {
        // silent
      }
    }
  }

  if (!run) return null

  const steps: Step[] = [
    {
      target: 'body',
      content: 'Bienvenue dans votre studio virtuel ! Découvrez comment créer votre premier look en quelques clics.',
      title: 'Studio VFS',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '[data-tour="photo-upload"]',
      content: 'Commencez par uploader une photo de vous. Utilisez une photo en pied pour les meilleurs résultats.',
      title: '1. Votre photo',
      placement: 'bottom',
    },
    {
      target: '[data-tour="garment-select"]',
      content: 'Choisissez un vêtement dans notre catalogue ou uploadez le vôtre.',
      title: '2. Le vêtement',
      placement: 'bottom',
    },
    {
      target: '[data-tour="category-select"]',
      content: 'Indiquez la catégorie du vêtement pour un meilleur rendu.',
      title: '3. Catégorie',
      placement: 'bottom',
    },
    {
      target: '[data-tour="generate-button"]',
      content: 'Cliquez ici pour lancer la génération. Le résultat apparaît en quelques secondes.',
      title: '4. Génération',
      placement: 'top',
    },
    {
      target: '[data-tour="result-area"]',
      content: 'Vous pouvez télécharger le résultat ou réessayer avec un autre vêtement. À vous de jouer !',
      title: '5. Résultat',
      placement: 'top',
    },
  ]

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      locale={{
        back: 'Retour',
        close: 'Fermer',
        last: 'Terminer',
        next: 'Suivant',
        skip: 'Passer',
      }}
      styles={{
        options: {
          primaryColor: '#D4A853',
          backgroundColor: '#111111',
          textColor: '#F5F0E8',
          arrowColor: '#111111',
        },
        buttonClose: { display: 'none' },
        tooltipContainer: { textAlign: 'left' },
        tooltipContent: { padding: '12px 0' },
      }}
      callback={handleJoyrideCallback}
    />
  )
}
