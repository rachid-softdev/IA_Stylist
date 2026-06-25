'use client'

import { useState } from 'react'
import { Dialog } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { HelpCircle, Camera, Sparkles, CreditCard, BookOpen } from 'lucide-react'
import Link from 'next/link'

const faqs = [
  {
    icon: Camera,
    question: 'Quelle photo utiliser ?',
    answer: 'Face, profil ou corps entier dans une bonne lumière. Évitez les arrière-plans chargés. Plus la photo est nette, meilleur est le résultat.',
  },
  {
    icon: Sparkles,
    question: 'Que donne l\'AI Stylist Pro ?',
    answer: 'Le Styliste IA analyse votre morphologie et votre teint pour recommander les coupes et couleurs qui vous vont le mieux. Disponible avec l\'abonnement Pro.',
  },
  {
    icon: CreditCard,
    question: 'Comment fonctionnent les crédits ?',
    answer: 'Chaque génération (photo ou vidéo) consomme des crédits. Les crédits sont remis à jour chaque mois selon votre abonnement. Les crédits offerts à l\'inscription sont valables 30 jours.',
  },
  {
    icon: BookOpen,
    question: 'Documentation technique',
    answer: 'Consultez notre documentation complète pour l\'intégration Shopify et l\'API REST.',
  },
]

export function HelpDialog() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="rounded p-2 text-text-tertiary hover:bg-bg-overlay hover:text-text-primary transition-colors duration-150"
        aria-label="Aide"
      >
        <HelpCircle className="h-4 w-4" />
      </button>

      <Dialog open={open} onClose={() => setOpen(false)} title="Aide & Support">
        <div className="space-y-4">
          {faqs.map((faq) => {
            const Icon = faq.icon
            return (
              <div key={faq.question} className="rounded-lg border border-border-default p-4">
                <div className="flex items-start gap-3">
                  <Icon className="mt-0.5 h-4 w-4 shrink-0 text-accent-primary" />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{faq.question}</p>
                    <p className="mt-1 text-xs text-text-secondary leading-relaxed">{faq.answer}</p>
                  </div>
                </div>
              </div>
            )
          })}
          {faqs.some(f => f.icon === BookOpen) && (
            <Link
              href="https://docs.vfs.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 rounded-md border border-border-default px-4 py-2.5 text-sm text-accent-primary hover:bg-bg-overlay transition-colors"
            >
              Documentation complète
              <BookOpen className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      </Dialog>
    </>
  )
}
