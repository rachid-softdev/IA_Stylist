'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  BarChart3,
  TrendingUp,
  Package,
  DollarSign,
  Plus,
  Upload,
  RefreshCw,
} from 'lucide-react'

export default function BrandDashboardPage() {
  return (
    <div className="animate-fade-in">
      {/* Topbar */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">
            Brand Dashboard
          </h1>
          <p className="mt-1 text-text-secondary">Vue d&apos;ensemble de votre marque</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge status="active" className="!text-accent-primary !border-accent-primary/30">
            Plan Starter
          </Badge>
          <span className="text-sm text-text-secondary">500 crédits</span>
        </div>
      </div>

      {/* KPI Row */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Try-ons', value: '1,234', delta: '+12%', icon: Package },
          { label: 'Conversion', value: '3.2%', delta: '+0.5%', icon: TrendingUp },
          { label: 'Retours évités', value: '308', delta: '-25%', icon: RefreshCw },
          { label: 'Économies', value: '46k€', delta: '+8%', icon: DollarSign },
        ].map((kpi) => (
          <Card key={kpi.label} hover>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-text-tertiary uppercase tracking-widest">{kpi.label}</p>
                <p className="mt-1 font-display text-2xl text-text-primary">{kpi.value}</p>
                <p className="mt-0.5 text-xs text-gen-done">{kpi.delta} vs mois précédent</p>
              </div>
              <kpi.icon className="h-5 w-5 text-text-tertiary" />
            </div>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Try-ons par semaine
          </h3>
          <div className="flex h-48 items-center justify-center rounded bg-bg-elevated">
            <BarChart3 className="h-8 w-8 text-text-tertiary" />
            <span className="ml-3 text-sm text-text-tertiary">Graphique à venir</span>
          </div>
        </Card>

        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Top SKUs
          </h3>
          <div className="flex h-48 items-center justify-center rounded bg-bg-elevated">
            <BarChart3 className="h-8 w-8 text-text-tertiary" />
            <span className="ml-3 text-sm text-text-tertiary">Graphique à venir</span>
          </div>
        </Card>
      </div>

      {/* Catalogue Table */}
      <Card>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-heading text-sm text-text-secondary uppercase tracking-widest">
            Catalogue
          </h3>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" iconLeft={<Upload className="h-3.5 w-3.5" />}>
              Importer CSV
            </Button>
            <Button size="sm" iconLeft={<Plus className="h-3.5 w-3.5" />}>
              Ajouter produit
            </Button>
          </div>
        </div>

        {/* Table header */}
        <div className="mb-2 grid grid-cols-5 gap-4 border-b border-border-subtle pb-2 text-xs text-text-tertiary uppercase tracking-widest">
          <span>SKU</span>
          <span>Nom</span>
          <span>Catégorie</span>
          <span>Try-ons</span>
          <span>Statut</span>
        </div>

        {/* Empty state */}
        <div className="py-12 text-center">
          <Package className="mx-auto h-8 w-8 text-text-tertiary" />
          <p className="mt-3 text-sm text-text-secondary">
            Aucun produit dans votre catalogue
          </p>
          <p className="text-xs text-text-tertiary">
            Ajoutez vos premiers vêtements pour commencer
          </p>
        </div>
      </Card>
    </div>
  )
}
