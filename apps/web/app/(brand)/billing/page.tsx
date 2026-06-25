'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToastStore } from '@/stores/toast-store'
import { FileText } from 'lucide-react'

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
              onClick={() => addToast({ type: 'info', title: 'Changement de plan', message: 'Cette fonctionnalité sera bientôt disponible. Contactez le support pour modifier votre abonnement.' })}
            >
              Changer de plan
            </Button>
          </div>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-primary">Historique des factures</h3>
          <div className="py-12 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-accent-primary/10 animate-float">
              <FileText className="h-5 w-5 text-accent-primary" />
            </div>
            <p className="font-heading text-sm text-text-primary">Aucune facture</p>
            <p className="mt-1 text-xs text-text-secondary">Vos factures apparaîtront ici après votre premier paiement</p>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}
