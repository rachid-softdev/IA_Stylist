'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Key, Copy } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function ApiKeysPage() {
  const [apiKey, setApiKey] = useState<string | null>(null)
  const { addToast } = useToastStore()

  const handleGenerate = () => {
    const key = 'vfs_live_' + Math.random().toString(36).substring(2, 34)
    setApiKey(key)
    addToast({ type: 'success', title: 'Clé générée', message: 'Copiez-la maintenant, elle ne sera plus visible' })
  }

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">API Keys</h1>
        <p className="mt-1 text-text-secondary">Gérez vos clés d&apos;intégration</p>
      </motion.div>

      <motion.div variants={item}>
        <Card className="mb-6">
          <div className="flex items-start gap-4">
            <Key className="mt-0.5 h-5 w-5 text-accent-primary" />
            <div className="flex-1">
              <h3 className="font-heading text-sm text-text-primary">Clé API</h3>
              <p className="text-xs text-text-secondary">
                Utilisez cette clé pour intégrer le widget Shopify ou utiliser l&apos;API REST.
              </p>
              {apiKey ? (
                <div className="mt-3 flex items-center gap-2">
                  <Input value={apiKey} readOnly className="font-mono text-xs" />
                  <Button
                    variant="secondary"
                    size="sm"
                    iconLeft={<Copy className="h-3.5 w-3.5" />}
                    onClick={() => {
                      navigator.clipboard.writeText(apiKey)
                      addToast({ type: 'success', title: 'Copié !' })
                    }}
                  >
                    Copier
                  </Button>
                </div>
              ) : (
                <Button
                  variant="secondary"
                  size="sm"
                  className="mt-3"
                  onClick={handleGenerate}
                >
                  Générer une clé
                </Button>
              )}
            </div>
          </div>
        </Card>
      </motion.div>

      <motion.p variants={item} className="text-xs text-text-tertiary">
        Les clés API donnent accès à toutes les fonctionnalités de votre compte marque.
        Ne les partagez jamais.
      </motion.p>
    </motion.div>
  )
}
