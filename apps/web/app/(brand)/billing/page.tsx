'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToastStore } from '@/stores/toast-store'

export default function BillingPage() {
  const { addToast } = useToastStore()

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Facturation</h1>
        <p className="mt-1 text-text-secondary">Gérez votre abonnement et consultez vos factures</p>
      </div>

      <Card className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-heading text-sm text-text-primary">Plan Starter</h3>
            <p className="text-xs text-text-secondary">199€/mois — 500 crédits/mois</p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => addToast({ type: 'info', title: 'Stripe', message: 'Page de checkout à implémenter' })}
          >
            Changer de plan
          </Button>
        </div>
      </Card>

      <Card>
        <h3 className="mb-4 font-heading text-sm text-text-primary">Historique des factures</h3>
        <div className="py-8 text-center">
          <p className="text-sm text-text-secondary">Aucune facture pour le moment</p>
        </div>
      </Card>
    </div>
  )
}
