'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Sparkles, ArrowRight, Zap, Camera, BarChart3, Shield } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Hero */}
      <header className="relative overflow-hidden">
        <div className="mx-auto max-w-grid px-4 pt-20 text-center md:pt-32">
          <h1 className="font-display text-4xl tracking-tight text-text-primary md:text-5xl lg:text-6xl">
            Votre shooting photo
            <br />
            <span className="text-accent-primary">en 60 secondes.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-lg text-md text-text-secondary">
            Essayez n&apos;importe quel vêtement sur vous grâce à l&apos;IA.
            Résultats professionnels, essai gratuit.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/signup">
              <Button size="lg" iconRight={<ArrowRight className="h-4 w-4" />}>
                Essayer gratuitement — 10 crédits offerts
              </Button>
            </Link>
          </div>

          {/* Demo visual placeholder */}
          <div className="mx-auto mt-16 max-w-3xl rounded-xl border border-border-default bg-bg-surface p-4 shadow-lg">
            <div className="aspect-[16/9] rounded-lg bg-bg-elevated flex items-center justify-center">
              <div className="text-center">
                <Camera className="mx-auto h-10 w-10 text-text-tertiary" />
                <p className="mt-3 text-sm text-text-secondary">
                  Démo interactive — Votre photo + Vêtement = Résultat
                </p>
                <div className="mt-4 flex items-center justify-center gap-4">
                  <div className="h-32 w-24 rounded-md bg-bg-overlay" />
                  <Sparkles className="h-6 w-6 text-accent-primary" />
                  <div className="h-32 w-24 rounded-md bg-bg-overlay border-2 border-dashed border-accent-primary/30" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="mx-auto max-w-grid px-4 py-20 md:py-32">
        <h2 className="text-center font-display text-3xl tracking-tight text-text-primary md:text-4xl">
          Une plateforme complète
        </h2>
        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[
            {
              icon: Camera,
              title: 'Try-On Photo',
              desc: 'Visualisez n\'importe quel vêtement sur vous en quelques secondes.',
            },
            {
              icon: Zap,
              title: 'Vidéo Défilé',
              desc: 'Transformez vos looks en vidéos dynamiques pour les réseaux sociaux.',
            },
            {
              icon: Sparkles,
              title: 'AI Stylist',
              desc: 'Conseils personnalisés basés sur votre morphologie et style.',
            },
            {
              icon: BarChart3,
              title: 'Dashboard Marque',
              desc: 'Analysez vos performances et réduisez vos retours de 30%.',
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="rounded-lg border border-border-default bg-bg-surface p-6 transition-all duration-200 hover:border-border-strong hover:shadow-md"
            >
              <feature.icon className="h-6 w-6 text-accent-primary" />
              <h3 className="mt-4 font-heading text-base text-text-primary">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm text-text-secondary">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="border-t border-border-subtle bg-bg-surface">
        <div className="mx-auto max-w-grid px-4 py-20 md:py-32">
          <h2 className="text-center font-display text-3xl tracking-tight text-text-primary md:text-4xl">
            Plans adaptés à vos besoins
          </h2>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {[
              {
                name: 'Free',
                price: '0€',
                credits: '10 crédits/mois',
                features: ['Try-On Image', 'Galerie 7 jours', 'Qualité standard'],
                cta: 'Commencer',
              },
              {
                name: 'Pro',
                price: '19€',
                credits: '100 crédits/mois',
                features: ['Try-On Image + Vidéo', 'Export HD', 'Collections illimitées', 'AI Stylist basique'],
                cta: 'Essayer Pro',
                highlight: true,
              },
              {
                name: 'Brand',
                price: '199€',
                credits: '500 crédits/mois',
                features: ['Dashboard analytics', 'Plugin Shopify', 'API', 'Lookbook', 'Support prioritaire'],
                cta: 'Contactez-nous',
              },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-lg border p-8 ${
                  plan.highlight
                    ? 'border-accent-primary bg-accent-primary/5 shadow-glow-gold'
                    : 'border-border-default bg-bg-surface'
                }`}
              >
                <h3 className="font-heading text-lg text-text-primary">{plan.name}</h3>
                <p className="mt-2 font-display text-3xl text-text-primary">{plan.price}</p>
                <p className="text-sm text-text-secondary">/mois</p>
                <p className="mt-3 text-sm text-accent-primary">{plan.credits}</p>
                <ul className="mt-6 space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-text-secondary">
                      <span className="text-accent-primary">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <Link href="/signup" className="mt-6 block">
                  <Button
                    variant={plan.highlight ? 'primary' : 'secondary'}
                    className="w-full"
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border-subtle py-8 text-center">
        <div className="mx-auto max-w-grid px-4">
          <div className="flex items-center justify-center gap-2 text-sm text-text-tertiary">
            <Shield className="h-3.5 w-3.5" />
            <span>VFS — Virtual Fashion Studio</span>
          </div>
          <p className="mt-2 text-xs text-text-tertiary">
            © 2026 VFS. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  )
}
