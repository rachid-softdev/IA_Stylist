'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { useToastStore } from '@/stores/toast-store'
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { ArrowRight, ArrowLeft, Building2, ShoppingBag, Check } from 'lucide-react'

const stepVariants = {
  enter: { opacity: 0, y: 20 },
  center: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
}

export default function BrandOnboardingPage() {
  const [step, setStep] = useState(1)
  const [name, setName] = useState('')
  const [shopifyUrl, setShopifyUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const { addToast } = useToastStore()
  const router = useRouter()

  const handleCreate = async () => {
    setLoading(true)
    try {
      await api.post('/brands/onboarding', {
        name,
        shopify_url: shopifyUrl || undefined,
      })
      addToast({ type: 'success', title: 'Marque créée' })
      router.push('/dashboard')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erreur lors de la création'
      addToast({ type: 'error', title: 'Erreur', message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-lg">
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="mb-8 flex justify-center gap-2"
        >
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1 w-12 rounded-full transition-all duration-300 ${
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
            >
              <Card className="text-center">
                <Building2 className="mx-auto h-8 w-8 text-accent-primary" />
                <h1 className="mt-4 font-display text-2xl text-text-primary">
                  Créez votre marque
                </h1>
                <p className="mt-2 text-sm text-text-secondary">
                  Lancez vous en quelques clics
                </p>
                <div className="mt-6 space-y-4 text-left">
                  <div>
                    <label className="mb-1 block text-xs text-text-secondary">Nom de la marque</label>
                    <Input
                      placeholder="Ma Marque"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                  <Button
                    className="w-full"
                    size="lg"
                    iconRight={<ArrowRight className="h-4 w-4" />}
                    onClick={() => setStep(2)}
                    disabled={!name.trim()}
                  >
                    Continuer
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              variants={stepVariants}
              initial="enter"
              animate="center"
              exit="exit"
            >
              <Card className="text-center">
                <ShoppingBag className="mx-auto h-8 w-8 text-accent-primary" />
                <h1 className="mt-4 font-display text-2xl text-text-primary">
                  Votre boutique
                </h1>
                <p className="mt-2 text-sm text-text-secondary">
                  Connectez votre boutique Shopify ou passez cette étape
                </p>
                <div className="mt-6 space-y-4">
                  <div>
                    <label className="mb-1 block text-xs text-text-secondary">URL Shopify (optionnel)</label>
                    <Input
                      placeholder="https://ma-marque.myshopify.com"
                      value={shopifyUrl}
                      onChange={(e) => setShopifyUrl(e.target.value)}
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="ghost"
                      size="md"
                      iconLeft={<ArrowLeft className="h-4 w-4" />}
                      onClick={() => setStep(1)}
                    >
                      Retour
                    </Button>
                    <Button
                      className="flex-1"
                      size="lg"
                      iconRight={<ArrowRight className="h-4 w-4" />}
                      onClick={() => setStep(3)}
                    >
                      Continuer
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              variants={stepVariants}
              initial="enter"
              animate="center"
              exit="exit"
            >
              <Card className="text-center">
                <Check className="mx-auto h-8 w-8 text-gen-done" />
                <h1 className="mt-4 font-display text-2xl text-text-primary">
                  Prêt à démarrer
                </h1>
                <p className="mt-2 text-sm text-text-secondary">
                  Vous pourrez inviter votre équipe et configurer votre catalogue ensuite
                </p>
                <div className="mt-6 rounded-md bg-bg-elevated p-4 text-left text-sm">
                  <div className="flex justify-between py-1">
                    <span className="text-text-secondary">Marque</span>
                    <span className="text-text-primary font-medium">{name}</span>
                  </div>
                  {shopifyUrl && (
                    <div className="flex justify-between py-1">
                      <span className="text-text-secondary">Shopify</span>
                      <span className="text-text-primary font-medium">{shopifyUrl}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-1">
                    <span className="text-text-secondary">Plan</span>
                    <span className="text-text-primary font-medium">Starter — 500 crédits</span>
                  </div>
                </div>
                <div className="mt-6 flex gap-3">
                  <Button
                    variant="ghost"
                    size="md"
                    iconLeft={<ArrowLeft className="h-4 w-4" />}
                    onClick={() => setStep(2)}
                    disabled={loading}
                  >
                    Retour
                  </Button>
                  <Button
                    className="flex-1"
                    size="lg"
                    loading={loading}
                    onClick={handleCreate}
                  >
                    Créer ma marque
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
