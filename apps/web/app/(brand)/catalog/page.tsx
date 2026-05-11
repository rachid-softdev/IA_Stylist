'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Upload, Search } from 'lucide-react'

export default function CatalogPage() {
  const [search, setSearch] = useState('')

  return (
    <div className="animate-fade-in">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Catalogue</h1>
          <p className="mt-1 text-text-secondary">Gérez vos vêtements</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" iconLeft={<Upload className="h-3.5 w-3.5" />}>
            CSV
          </Button>
          <Button size="sm" iconLeft={<Plus className="h-3.5 w-3.5" />}>
            Ajouter
          </Button>
        </div>
      </div>

      <div className="mb-6">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            placeholder="Rechercher un produit..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Card>
        <div className="py-20 text-center">
          <p className="text-sm text-text-secondary">
            Aucun produit — ajoutez vos premiers vêtements
          </p>
        </div>
      </Card>
    </div>
  )
}
