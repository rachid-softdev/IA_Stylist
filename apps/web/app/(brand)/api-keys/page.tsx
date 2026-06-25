'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Key, Copy, Trash2, Plus } from 'lucide-react'
import { api } from '@/lib/api'
import { useToastStore } from '@/stores/toast-store'

interface ApiKey {
  id: string
  prefix: string
  created_at: string
  last_used_at: string | null
  is_active: boolean
}

interface NewKeyResponse {
  id: string
  key: string
  prefix: string
  created_at: string
}

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function ApiKeysPage() {
  const [newKey, setNewKey] = useState<NewKeyResponse | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const { addToast } = useToastStore()
  const queryClient = useQueryClient()

  const { data: keys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const res = await api.get<ApiKey[]>('/brands/me/api-keys')
      return res.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post<NewKeyResponse>('/brands/me/api-keys')
      return res.data
    },
    onSuccess: (data) => {
      setNewKey(data)
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
    onError: (err: Error) => {
      addToast({ type: 'error', title: 'Erreur', message: err.message })
    },
  })

  const revokeMutation = useMutation({
    mutationFn: async (keyId: string) => {
      await api.delete(`/brands/me/api-keys/${keyId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      addToast({ type: 'success', title: 'Clé révoquée' })
    },
    onError: (err: Error) => {
      addToast({ type: 'error', title: 'Erreur', message: err.message })
    },
  })

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Clés API</h1>
          <p className="mt-1 text-text-secondary">Gérez vos clés d&apos;intégration</p>
        </div>
        <Button size="sm" iconLeft={<Plus className="h-3.5 w-3.5" />} onClick={() => setShowCreate(true)}>
          Créer une clé
        </Button>
      </motion.div>

      {/* New key reveal card */}
      <Dialog open={newKey !== null} onClose={() => setNewKey(null)} title="Clé API créée">
        <div className="space-y-4">
          <div className="rounded-lg border border-accent-primary/30 bg-accent-primary/5 p-4">
            <p className="text-xs text-text-secondary font-medium mb-2">Votre clé API</p>
            <div className="flex items-center gap-2">
              <Input value={newKey?.key || ''} readOnly className="font-mono text-xs" />
              <Button
                variant="secondary"
                size="sm"
                iconLeft={<Copy className="h-3.5 w-3.5" />}
                onClick={() => {
                  if (newKey) {
                    navigator.clipboard.writeText(newKey.key)
                    addToast({ type: 'success', title: 'Copié !' })
                  }
                }}
              >
                Copier
              </Button>
            </div>
          </div>
          <div className="rounded-md border border-status-warning/30 bg-status-warning/5 p-3 text-xs text-text-secondary">
            <strong className="text-status-warning">Important :</strong> Copiez cette clé maintenant.
            Elle ne sera plus jamais affichée. Si vous la perdez, créez-en une nouvelle.
          </div>
          <Button className="w-full" onClick={() => setNewKey(null)}>
            J&apos;ai copié la clé
          </Button>
        </div>
      </Dialog>

      {/* Key list */}
      <motion.div variants={item}>
        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-primary">Clés existantes</h3>
          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : keys && keys.length > 0 ? (
            <div className="divide-y divide-border-subtle">
              {keys.map((key) => (
                <div key={key.id} className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    <Key className="h-4 w-4 text-text-tertiary" />
                    <div>
                      <div className="flex items-center gap-2">
                        <code className="text-sm font-mono text-text-primary">
                          {key.prefix}...{key.id.slice(-4)}
                        </code>
                        <Badge status={key.is_active ? 'active' : 'inactive'}>
                          {key.is_active ? 'Active' : 'Révoquée'}
                        </Badge>
                      </div>
                      <p className="mt-0.5 text-xs text-text-tertiary">
                        Créée le {new Date(key.created_at).toLocaleDateString('fr-FR')}
                        {key.last_used_at && ` · Dernière utilisation : ${new Date(key.last_used_at).toLocaleDateString('fr-FR')}`}
                      </p>
                    </div>
                  </div>
                  {key.is_active && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-status-error"
                      loading={revokeMutation.isPending}
                      onClick={() => revokeMutation.mutate(key.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <Key className="mx-auto h-8 w-8 text-text-tertiary" />
              <p className="mt-3 text-sm text-text-secondary">Aucune clé API</p>
              <p className="text-xs text-text-tertiary mt-1">
                Créez une clé pour intégrer le widget Shopify ou utiliser l&apos;API REST.
              </p>
            </div>
          )}
        </Card>
      </motion.div>

      <motion.p variants={item} className="mt-6 text-xs text-text-tertiary">
        Les clés API donnent accès à toutes les fonctionnalités de votre compte marque.
        Ne les partagez jamais. Révoquez les clés compromises immédiatement.
      </motion.p>
    </motion.div>
  )
}
