'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Dialog } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { useToastStore } from '@/stores/toast-store'
import { Plus, Upload as UploadIcon, Search, Package } from 'lucide-react'
import type { Garment } from '@vfs/shared-types'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function CatalogPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showAdd, setShowAdd] = useState(false)
  const { addToast } = useToastStore()

  const { data, isLoading } = useQuery({
    queryKey: ['catalog', search, page],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      params.set('page', String(page))
      const res = await api.get<Garment[]>(`/catalog/brand-id/garments?${params}`)
      return res
    },
  })

  const garments = data?.data || []
  const totalPages = data?.meta?.total_pages || 1

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Catalogue</h1>
          <p className="mt-1 text-text-secondary">Gérez vos vêtements</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" iconLeft={<UploadIcon className="h-3.5 w-3.5" />}>
            CSV
          </Button>
          <Button size="sm" iconLeft={<Plus className="h-3.5 w-3.5" />} onClick={() => setShowAdd(true)}>
            Ajouter
          </Button>
        </div>
      </motion.div>

      <motion.div variants={item} className="mb-6">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            placeholder="Rechercher par nom ou SKU..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="pl-9"
          />
        </div>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          {isLoading ? (
            <div className="py-12 text-center text-sm text-text-secondary">Chargement...</div>
          ) : garments.length > 0 ? (
            <div>
              <div className="grid grid-cols-12 gap-4 border-b border-border-subtle px-4 py-3 text-xs text-text-tertiary uppercase tracking-widest">
                <span className="col-span-3">SKU</span>
                <span className="col-span-4">Nom</span>
                <span className="col-span-2">Catégorie</span>
                <span className="col-span-2">Statut</span>
                <span className="col-span-1" />
              </div>
              {garments.map((g: Garment) => (
                <div key={g.id} className="grid grid-cols-12 gap-4 border-b border-border-subtle px-4 py-3 text-sm last:border-0">
                  <span className="col-span-3 font-mono text-xs text-text-secondary">{g.sku}</span>
                  <span className="col-span-4 text-text-primary">{g.name}</span>
                  <span className="col-span-2 text-text-secondary">{g.category}</span>
                  <span className="col-span-2">
                    <Badge status={g.status === 'active' ? 'active' : 'default'}>
                      {g.status === 'active' ? 'Actif' : g.status === 'validating' ? 'Validation' : 'Échec'}
                    </Badge>
                  </span>
                </div>
              ))}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 text-xs text-text-secondary">
                  <span>Page {page} / {totalPages}</span>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                      Précédent
                    </Button>
                    <Button variant="ghost" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                      Suivant
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="py-20 text-center">
              <Package className="mx-auto h-8 w-8 text-text-tertiary" />
              <p className="mt-3 text-sm text-text-secondary">Aucun produit</p>
              <Button size="sm" className="mt-4" onClick={() => setShowAdd(true)}>
                Ajouter un produit
              </Button>
            </div>
          )}
        </Card>
      </motion.div>

      <Dialog open={showAdd} onClose={() => setShowAdd(false)} title="Ajouter un vêtement">
        <AddGarmentForm onDone={() => { setShowAdd(false); addToast({ type: 'success', title: 'Vêtement ajouté' }) }} />
      </Dialog>
    </motion.div>
  )
}

function AddGarmentForm({ onDone }: { onDone: () => void }) {
  const [sku, setSku] = useState('')
  const [name, setName] = useState('')
  const [category, setCategory] = useState('top')
  const [imageUrl, setImageUrl] = useState('')
  const { addToast } = useToastStore()

  const handleSubmit = async () => {
    try {
      await api.post('/catalog/brand-id/garments', { sku, name, category, image_url: imageUrl })
      onDone()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erreur'
      addToast({ type: 'error', title: 'Erreur', message })
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1 block text-xs text-text-secondary">SKU *</label>
        <Input placeholder="PROD-001" value={sku} onChange={(e) => setSku(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-xs text-text-secondary">Nom *</label>
        <Input placeholder="T-shirt blanc" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-xs text-text-secondary">Catégorie *</label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full rounded-md border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary"
        >
          <option value="top">Top</option>
          <option value="bottom">Bottom</option>
          <option value="dress">Robe</option>
          <option value="outerwear">Veste</option>
          <option value="shoes">Chaussures</option>
          <option value="accessories">Accessoires</option>
        </select>
      </div>
      <div>
        <label className="mb-1 block text-xs text-text-secondary">URL de l&apos;image</label>
        <Input placeholder="https://..." value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} />
      </div>
      <Button className="w-full" onClick={handleSubmit} disabled={!sku || !name}>
        Ajouter
      </Button>
    </div>
  )
}
