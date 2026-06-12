'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToastStore } from '@/stores/toast-store'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function BillingPage() {
  const { addToast } = useToastStore()

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Facturation</h1>
        <p className="mt-1 text-text-secondary">Gérez votre abonnement et consultez vos factures</p>
      </motion.div>

      <motion.div variants={item}>
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
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-primary">Historique des factures</h3>
          <div className="py-8 text-center">
            <p className="text-sm text-text-secondary">Aucune facture pour le moment</p>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}
