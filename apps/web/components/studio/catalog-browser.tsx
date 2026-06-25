'use client'

import { useState } from 'react'
import { Dialog } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Search, Package } from 'lucide-react'
import type { GarmentCategory } from '@vfs/shared-types'

interface CatalogItem {
  id: string
  name: string
  image_url: string
  category: GarmentCategory
}

interface CatalogBrowserProps {
  open: boolean
  onClose: () => void
  onSelect: (garment: {
    id: string
    name: string
    image_url: string
    category: GarmentCategory
  }) => void
  multiSelect?: boolean
  selectedIds?: string[]
  onSelectMultiple?: (garments: {
    id: string
    name: string
    image_url: string
    category: GarmentCategory
  }[]) => void
}

const demoGarments: CatalogItem[] = [
  { id: 'demo-tshirt', name: 'T-shirt Blanc', image_url: '/demo/tshirt-blanc.jpg', category: 'top' },
  { id: 'demo-robe', name: 'Robe Noire', image_url: '/demo/robe-noire.jpg', category: 'dress' },
  { id: 'demo-jean', name: 'Jean Slim', image_url: '/demo/jean-slim.jpg', category: 'bottom' },
  { id: 'demo-blazer', name: 'Veste Blazer', image_url: '/demo/veste-blazer.jpg', category: 'outerwear' },
  { id: 'demo-pull', name: 'Pull Cachemire', image_url: '/demo/pull-cachemire.jpg', category: 'top' },
  { id: 'demo-veste-cuir', name: 'Veste Cuir', image_url: '/demo/veste-cuir.jpg', category: 'outerwear' },
  { id: 'demo-chemise', name: 'Chemise Lin', image_url: '/demo/chemise-lin.jpg', category: 'top' },
  { id: 'demo-manteau', name: 'Manteau Long', image_url: '/demo/manteau-long.jpg', category: 'outerwear' },
]

const categoryLabels: Record<string, string> = {
  top: 'Haut',
  bottom: 'Bas',
  dress: 'Robe',
  outerwear: 'Veste/Manteau',
  shoes: 'Chaussures',
  accessories: 'Accessoires',
}

export function CatalogBrowser({ open, onClose, onSelect, multiSelect, selectedIds = [], onSelectMultiple }: CatalogBrowserProps) {
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<GarmentCategory | 'all'>('all')
  const [tempSelected, setTempSelected] = useState<string[]>(multiSelect ? [...selectedIds] : [])

  const filtered = demoGarments.filter((g) => {
    const matchesSearch = !search || g.name.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || g.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const categories = Array.from(new Set(demoGarments.map((g) => g.category)))

  return (
    <Dialog open={open} onClose={onClose} title="Catalogue" size="xl">
      {/* Search + filter */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un vêtement..."
            className="w-full rounded-md border border-border-default bg-bg-surface py-2 pl-9 pr-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-accent-primary focus:outline-none"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          <button
            onClick={() => setCategoryFilter('all')}
            className={`whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              categoryFilter === 'all'
                ? 'bg-accent-primary text-text-inverse'
                : 'bg-bg-elevated text-text-secondary hover:text-text-primary'
            }`}
          >
            Tous
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                categoryFilter === cat
                  ? 'bg-accent-primary text-text-inverse'
                  : 'bg-bg-elevated text-text-secondary hover:text-text-primary'
              }`}
            >
              {categoryLabels[cat] || cat}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Package className="mb-3 h-8 w-8 text-text-tertiary" />
          <p className="text-sm text-text-secondary">Aucun vêtement trouvé</p>
          <button
            onClick={() => { setSearch(''); setCategoryFilter('all') }}
            className="mt-2 text-xs text-accent-primary hover:underline"
          >
            Réinitialiser les filtres
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {filtered.map((garment) => {
            const isSelected = tempSelected.includes(garment.id)
            return (
              <button
                key={garment.id}
                onClick={() => {
                  if (multiSelect) {
                    setTempSelected((prev) =>
                      prev.includes(garment.id)
                        ? prev.filter((id) => id !== garment.id)
                        : [...prev, garment.id],
                    )
                  } else {
                    onSelect({
                      id: garment.id,
                      name: garment.name,
                      image_url: garment.image_url,
                      category: garment.category,
                    })
                    onClose()
                  }
                }}
                className={`group flex flex-col rounded-lg border overflow-hidden transition-all hover:shadow-md ${
                  isSelected
                    ? 'border-accent-primary bg-accent-primary/5'
                    : 'border-border-default bg-bg-surface hover:border-accent-primary'
                }`}
              >
                <div className="relative aspect-[3/4] bg-bg-elevated flex items-center justify-center overflow-hidden">
                  {isSelected && (
                    <div className="absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full bg-accent-primary text-2xs font-bold text-text-inverse">
                      ✓
                    </div>
                  )}
                  <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-bg-elevated to-bg-surface p-4">
                    <Package className="h-10 w-10 text-text-tertiary group-hover:text-accent-primary transition-colors" />
                  </div>
                </div>
                <div className="border-t border-border-subtle p-3">
                  <p className="text-sm font-medium text-text-primary truncate">{garment.name}</p>
                  <p className="text-xs text-text-tertiary">{categoryLabels[garment.category] || garment.category}</p>
                </div>
              </button>
            )
          })}
        </div>
      )}

      {multiSelect && (
        <div className="mt-6 flex items-center justify-between border-t border-border-subtle pt-4">
          <p className="text-sm text-text-secondary">{tempSelected.length} sélectionné{tempSelected.length > 1 ? 's' : ''}</p>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Annuler
            </Button>
            <Button
              size="sm"
              disabled={tempSelected.length === 0}
              onClick={() => {
                const selected = demoGarments.filter((g) => tempSelected.includes(g.id))
                onSelectMultiple?.(selected.map((g) => ({
                  id: g.id,
                  name: g.name,
                  image_url: g.image_url,
                  category: g.category,
                })))
                setTempSelected([])
                onClose()
              }}
            >
              Confirmer ({tempSelected.length})
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  )
}
