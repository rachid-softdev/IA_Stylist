'use client'

import { motion, MotionConfig, useReducedMotion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Sparkles, Zap, Camera, BarChart3, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Demoslider } from '@/components/landing/demo-slider'

/* ─── Animation variants ────────────────────────────────── */
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.15 },
  },
}

const child = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
}

const childScale = {
  hidden: { opacity: 0, scale: 0.94 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
}

/* ─── Nav ─────────────────────────────────────────────────── */
function Nav() {
  return (
    <motion.header
      className="fixed inset-x-0 top-0 z-50 border-b border-transparent backdrop-blur-lg"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="mx-auto flex h-16 max-w-grid items-center justify-between px-4 md:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent-primary text-sm font-bold text-text-inverse">
            V
          </div>
          <span className="font-heading text-base tracking-wide text-text-primary">VFS</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-8 md:flex" aria-label="Navigation principale">
          <Link
            href="/pricing"
            className="text-sm text-text-secondary transition-colors hover:text-text-primary"
          >
            Tarifs
          </Link>
          <Link
            href="/login"
            className="text-sm text-text-secondary transition-colors hover:text-text-primary"
          >
            Connexion
          </Link>
          <Link href="/signup">
            <Button size="sm" iconRight={<ArrowRight className="h-3.5 w-3.5" />}>
              Essai gratuit
            </Button>
          </Link>
        </nav>

        {/* Mobile CTA */}
        <Link href="/signup" className="md:hidden">
          <Button size="sm">Essayer</Button>
        </Link>
      </div>
    </motion.header>
  )
}

/* ─── Hero ────────────────────────────────────────────────── */
function HeroSection() {
  const prefersReduced = useReducedMotion()

  return (
    <section className="relative overflow-hidden pt-24 md:pt-32" aria-labelledby="hero-heading">
      {/* Subtle ambient glow */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-accent-primary/3 blur-[120px]" aria-hidden />

      <motion.div
        className="mx-auto max-w-grid px-4 pb-16 text-center md:pb-24"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        {/* Eyebrow — single, deliberate, not on every section */}
        <motion.div variants={child} className="mb-6">
          <span className="inline-block rounded-full border border-border-default bg-bg-surface px-4 py-1 text-2xs font-medium uppercase tracking-widest text-accent-primary">
            IA Fashion Studio
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          id="hero-heading"
          variants={child}
          className="font-display text-4xl tracking-tight text-text-primary md:text-5xl lg:text-6xl"
          style={{ textWrap: 'balance' } as React.CSSProperties}
        >
          Votre shooting photo
          <br />
          <span className="text-accent-primary">en 60 secondes.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          variants={child}
          className="mx-auto mt-5 max-w-lg text-md leading-relaxed text-text-secondary"
        >
          Essayez n&apos;importe quel vêtement sur vous grâce à l&apos;IA.
          Résultats professionnels, essai gratuit.
        </motion.p>

        {/* CTA */}
        <motion.div variants={child} className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Link href="/signup">
            <Button size="lg" iconRight={<ArrowRight className="h-4 w-4" />}>
              Essayer gratuitement — 10 crédits offerts
            </Button>
          </Link>
          <Link
            href="#features"
            className="flex items-center gap-1.5 text-sm text-text-secondary transition-colors hover:text-text-primary"
          >
            En savoir plus
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </motion.div>

        {/* Demo slider */}
        <motion.div
          variants={prefersReduced ? {} : childScale}
          className="mt-12 flex justify-center md:mt-16"
        >
          <Demoslider
            beforeSrc="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&fit=crop&q=80"
            afterSrc="https://images.unsplash.com/photo-1581044777550-4c0a0df6b3f4?w=600&h=800&fit=crop&q=80"
          />
        </motion.div>
      </motion.div>
    </section>
  )
}

/* ─── Social Proof ─────────────────────────────────────────── */

function SocialProof() {
  return (
    <section className="border-y border-border-subtle bg-bg-surface/50" aria-label="Témoignage">
      <div className="mx-auto max-w-grid px-4 py-12 md:py-16">
        <motion.figure
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-2xl text-center"
        >
          <svg className="mx-auto h-8 w-8 text-accent-primary/30 mb-6" fill="currentColor" viewBox="0 0 32 32" aria-hidden>
            <path d="M10 8c-3.3 0-6 2.7-6 6v10h10V14H8c0-1.1.9-2 2-2V8zm14 0c-3.3 0-6 2.7-6 6v10h10V14h-6c0-1.1.9-2 2-2V8z"/>
          </svg>
          <blockquote>
            <p className="text-lg leading-relaxed text-text-primary md:text-xl">
              &ldquo;On a réduit nos retours de <em className="text-accent-primary not-italic font-medium">30%</em> en deux mois.
              Un shooting coûtait <em className="text-accent-primary not-italic font-medium">10× moins cher</em> et prenait
              <em className="text-accent-primary not-italic font-medium"> moins de 60 secondes</em> par produit.
              C&rsquo;est devenu notre outil quotidien.&rdquo;
            </p>
          </blockquote>
          <figcaption className="mt-6 flex items-center justify-center gap-3">
            <div className="h-10 w-10 rounded-full bg-accent-primary/20 flex items-center justify-center text-sm font-medium text-accent-primary">
              ML
            </div>
            <div className="text-left">
              <span className="block text-sm text-text-primary">Marion Lefèvre</span>
              <span className="block text-xs text-text-tertiary">Directrice Marketing, Maison&nbsp;Claire</span>
            </div>
          </figcaption>
        </motion.figure>
      </div>
    </section>
  )
}

/* ─── Features ─────────────────────────────────────────────── */
const features = [
  {
    icon: Camera,
    title: 'Essayage Photo',
    desc: 'Visualisez n\'importe quel vêtement sur votre propre photo en quelques secondes. Résultat photoréaliste, pas de filtre.',
    highlight: true,
  },
  {
    icon: Zap,
    title: 'Vidéo Défilé',
    desc: 'Transformez vos looks en vidéos dynamiques. Runway, mirror selfie, rotation 360° — prêt pour les réseaux sociaux.',
  },
  {
    icon: Sparkles,
    title: 'Styliste IA',
    desc: 'Des conseils personnalisés basés sur votre morphologie, votre teint et votre style. Comme un styliste personnel, en instantané.',
  },
  {
    icon: BarChart3,
    title: 'Tableau de bord Marque',
    desc: 'Analysez vos performances, réduisez les retours de 30%, et suivez l\'engagement de chaque SKU en temps réel.',
  },
]

function FeaturesSection() {
  const [primary, ...rest] = features
  if (!primary) return null

  return (
    <section id="features" className="py-20 md:py-28" aria-labelledby="features-heading">
      <div className="mx-auto max-w-grid px-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="text-center"
        >
          <h2
            id="features-heading"
            className="font-display text-3xl tracking-tight text-text-primary md:text-4xl"
            style={{ textWrap: 'balance' } as React.CSSProperties}
          >
            Une plateforme complète
          </h2>
          <p className="mx-auto mt-3 max-w-md text-sm text-text-secondary">
            De la visualisation produit à l&apos;analyse de performance, tout ce dont vous avez besoin.
          </p>
        </motion.div>

        <div className="mt-12 grid gap-5 md:grid-cols-2">
          {/* Primary feature card — larger, spans full height */}
          <motion.article
            className="group relative row-span-2 flex flex-col justify-center rounded-xl border border-border-default bg-gradient-to-br from-bg-surface to-bg-elevated p-8 transition-all duration-300 hover:border-border-strong hover:shadow-md"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-accent-primary/10 ring-1 ring-accent-primary/20">
              <Camera className="h-6 w-6 text-accent-primary" />
            </div>
            <h3 className="font-display text-xl text-text-primary">{primary.title}</h3>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-text-secondary">{primary.desc}</p>
            <div className="mt-6 grid grid-cols-3 gap-6 border-t border-border-subtle pt-6">
              {[
                { label: 'Résolution', value: '4K HD' },
                { label: 'Temps', value: '&lt; 60s' },
                { label: 'Réalisme', value: '98%' },
              ].map((s) => (
                <div key={s.label}>
                  <p className="text-xs text-text-tertiary uppercase tracking-widest">{s.label}</p>
                  <p className="mt-0.5 font-display text-lg text-accent-primary">{s.value}</p>
                </div>
              ))}
            </div>
          </motion.article>

          {/* Secondary features — 2-col grid inside */}
          <div className="grid gap-5 content-start">
            {rest.map((feature, i) => {
              const Icon = feature.icon
              return (
                <motion.article
                  key={feature.title}
                  className="group relative rounded-xl border border-border-default bg-bg-surface p-6 transition-all duration-300 hover:border-border-strong hover:shadow-md"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.5, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                >
                  <div className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition-opacity duration-300 group-hover:opacity-100" aria-hidden>
                    <div className="absolute inset-0 rounded-xl ring-1 ring-accent-primary/20" />
                  </div>
                  <div className="relative flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent-primary/10">
                      <Icon className="h-5 w-5 text-accent-primary" />
                    </div>
                    <div>
                      <h3 className="font-heading text-base text-text-primary">{feature.title}</h3>
                      <p className="mt-1 text-sm leading-relaxed text-text-secondary">{feature.desc}</p>
                    </div>
                  </div>
                </motion.article>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ─── Pricing ──────────────────────────────────────────────── */
const plans = [
  {
    name: 'Free',
    price: '0€',
    credits: '10 crédits/mois',
    features: ['Essayage Photo', 'Galerie 7 jours', 'Qualité standard'],
    cta: 'Commencer',
    href: '/signup',
  },
  {
    name: 'Pro',
    price: '19€',
    credits: '100 crédits/mois',
    features: ['Essayage Photo + Vidéo', 'Export HD', 'Collections illimitées', 'Styliste IA'],
    cta: 'Essayer Pro',
    href: '/signup?plan=pro',
    highlight: true,
  },
  {
    name: 'Brand',
    price: '199€',
    credits: '500 crédits/mois',
    features: [
      'Dashboard analytics',
      'Plugin Shopify',
      'API & intégrations',
      'Lookbook automatique',
      'Support prioritaire',
    ],
    cta: 'Contacter l\'équipe',
    href: '/signup?plan=brand',
  },
]

function PricingSection() {
  return (
    <section className="border-t border-border-subtle bg-bg-surface/30 py-20 md:py-28" aria-labelledby="pricing-heading">
      <div className="mx-auto max-w-grid px-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="text-center"
        >
          <h2
            id="pricing-heading"
            className="font-display text-3xl tracking-tight text-text-primary md:text-4xl"
            style={{ textWrap: 'balance' } as React.CSSProperties}
          >
            Plans adaptés à vos besoins
          </h2>
          <p className="mx-auto mt-3 max-w-md text-sm text-text-secondary">
            Gratuit pour découvrir, premium pour créer, professionnel pour développer votre marque.
          </p>
        </motion.div>

        <div className="mt-12 grid gap-6 md:grid-cols-3 md:gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              className={`relative rounded-xl border p-8 transition-all duration-300 ${
                plan.highlight
                  ? 'border-accent-primary/60 bg-accent-primary/[0.04] shadow-glow-gold'
                  : 'border-border-default bg-bg-surface hover:border-border-strong'
              }`}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-accent-primary px-3 py-0.5 text-2xs font-medium uppercase tracking-widest text-text-inverse">
                    Populaire
                  </span>
                </div>
              )}

              <h3 className="font-heading text-lg text-text-primary">{plan.name}</h3>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="font-display text-3xl text-text-primary">{plan.price}</span>
                <span className="text-sm text-text-secondary">/mois</span>
              </div>
              <p className="mt-1 text-sm text-accent-primary">{plan.credits}</p>

              <ul className="mt-6 space-y-3" role="list">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-text-secondary">
                    <svg
                      className="mt-0.5 h-4 w-4 shrink-0 text-accent-primary"
                      fill="none"
                      viewBox="0 0 16 16"
                      aria-hidden
                    >
                      <path
                        d="M13.5 4.5L6.5 11.5L3 8"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>

              <Link href={plan.href} className="mt-8 block">
                <Button
                  variant={plan.highlight ? 'primary' : 'secondary'}
                  className="w-full"
                >
                  {plan.cta}
                </Button>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ─── CTA Section (pre-footer) ─────────────────────────────── */
function CtaSection() {
  return (
    <section className="py-20 md:py-28" aria-labelledby="cta-heading">
      <div className="mx-auto max-w-2xl px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2
            id="cta-heading"
            className="font-display text-3xl tracking-tight text-text-primary md:text-4xl"
            style={{ textWrap: 'balance' } as React.CSSProperties}
          >
            Prêt à transformer votre manière de présenter la mode&nbsp;?
          </h2>
          <p className="mx-auto mt-4 max-w-md text-md text-text-secondary">
            Créez votre premier look en 60 secondes. 10 crédits offerts, sans engagement.
          </p>
          <div className="mt-8">
            <Link href="/signup">
              <Button size="lg" iconRight={<ArrowRight className="h-4 w-4" />}>
                Essayer gratuitement
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

/* ─── Footer ───────────────────────────────────────────────── */
function Footer() {
  return (
    <footer className="border-t border-border-subtle py-10">
      <div className="mx-auto max-w-grid px-4">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent-primary/10 text-xs font-bold text-accent-primary">
              V
            </div>
            <span className="text-sm text-text-tertiary">
              Virtual Fashion Studio
            </span>
          </div>

          <nav className="flex items-center gap-6" aria-label="Liens pied de page">
            <Link href="/legal" className="text-xs text-text-tertiary transition-colors hover:text-text-secondary">
              Mentions légales
            </Link>
            <Link href="/privacy" className="text-xs text-text-tertiary transition-colors hover:text-text-secondary">
              Confidentialité
            </Link>
            <Link href="/contact" className="text-xs text-text-tertiary transition-colors hover:text-text-secondary">
              Contact
            </Link>
          </nav>

          <p className="text-xs text-text-tertiary">
            © {new Date().getFullYear()} VFS. Tous droits réservés.
          </p>
        </div>
      </div>
    </footer>
  )
}

/* ─── Mobile sticky CTA ────────────────────────────────────── */
function StickyMobileCta() {
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-border-subtle bg-bg-base/90 px-4 py-3 backdrop-blur-lg md:hidden">
      <Link href="/signup" className="block">
        <Button className="w-full" size="md" iconRight={<ArrowRight className="h-4 w-4" />}>
          Essayer gratuitement — 10 crédits offerts
        </Button>
      </Link>
    </div>
  )
}

/* ─── Page ─────────────────────────────────────────────────── */
export default function LandingPage() {
  return (
    <MotionConfig reducedMotion="user">
      <div className="min-h-screen bg-bg-base pb-20 md:pb-0">
        <Nav />
        <main>
          <HeroSection />
          <SocialProof />
          <FeaturesSection />
          <PricingSection />
          <CtaSection />
        </main>
        <Footer />
        <StickyMobileCta />
      </div>
    </MotionConfig>
  )
}
