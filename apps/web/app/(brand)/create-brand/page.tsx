'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { useToastStore } from '@/stores/toast-store'
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { ArrowRight, Building2, ShoppingBag, Check } from 'lucide-react'

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
        <div className="mb-8 flex justify-center gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1 w-12 rounded-full transition-all duration-300 ${
                s <= step ? 'bg-accent-primary' : 'bg-bg-elevated'
              }`}
            />
          ))}
        </div>

        {step === 1 && (
          <Card className="text-center animate-fade-in">
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
        )}

        {step === 2 && (
          <Card className="animate-fade-in">
            <ShoppingBag className="mx-auto h-8 w-8 text-accent-primary" />
            <h1 className="mt-4 text-center font-display text-2xl text-text-primary">
              Votre boutique
            </h1>
            <p className="mt-2 text-center text-sm text-text-secondary">
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
              <Button
                className="w-full"
                size="lg"
                iconRight={<ArrowRight className="h-4 w-4" />}
                onClick={() => setStep(3)}
              >
                Continuer
              </Button>
            </div>
          </Card>
        )}

        {step === 3 && (
          <Card className="text-center animate-fade-in">
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
            <Button
              className="mt-6 w-full"
              size="lg"
              loading={loading}
              onClick={handleCreate}
            >
              Créer ma marque
            </Button>
          </Card>
        )}
      </div>
    </div>
  )
}
