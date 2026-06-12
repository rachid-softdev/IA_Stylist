'use client'

import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TryonChart } from '@/components/charts/tryon-chart'
import { TopSkusChart } from '@/components/charts/top-skus-chart'
import {
  BarChart3,
  TrendingUp,
  Package,
  DollarSign,
  Plus,
  Upload,
  RefreshCw,
} from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

interface DashboardData {
  metrics: {
    tryons: number
    conversion: number
    returns_prevented: number
    savings: number
  }
  deltas: {
    tryons: string
    conversion: string
    returns: string
    savings: string
  }
  tryon_history: { date: string; count: number }[]
  top_skus: { sku: string; name: string; tryons: number }[]
}

export default function BrandDashboardPage() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['brand-dashboard'],
    queryFn: () => api.get<DashboardData>('/brands/me/dashboard').then((r) => r.data),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  })

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {/* Topbar */}
      <motion.div variants={item} className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">
            Brand Dashboard
          </h1>
          <p className="mt-1 text-sm text-text-secondary">
            Vue d&apos;ensemble de votre marque
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <Badge status="active" className="!text-accent-primary !border-accent-primary/30">
            Plan Starter
          </Badge>
          <span className="whitespace-nowrap text-sm text-text-secondary">
            {isLoading ? (
              <Skeleton variant="text" className="inline-block h-4 w-16" />
            ) : (
              '500 crédits'
            )}
          </span>
        </div>
      </motion.div>

      {/* KPI Row */}
      <motion.div variants={item} className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} hover={false}>
              <Skeleton className="mb-2 h-3 w-16" />
              <Skeleton className="h-8 w-24" />
              <Skeleton className="mt-2 h-3 w-20" />
            </Card>
          ))
        ) : !data ? (
          <div className="col-span-full flex items-center justify-center rounded-lg border border-dashed border-border-default py-12 text-center">
            <div>
              <BarChart3 className="mx-auto h-8 w-8 text-text-tertiary" />
              <p className="mt-3 text-sm text-text-secondary">
                Aucune donnée disponible pour le moment
              </p>
              <p className="mt-1 text-xs text-text-tertiary">
                Importez vos premiers produits pour voir les statistiques
              </p>
            </div>
          </div>
        ) : (
          [
            {
              label: 'Try-ons',
              value: data.metrics.tryons,
              delta: data.deltas.tryons,
              icon: Package,
            },
            {
              label: 'Conversion',
              value: `${data.metrics.conversion}%`,
              delta: data.deltas.conversion,
              icon: TrendingUp,
            },
            {
              label: 'Retours évités',
              value: data.metrics.returns_prevented,
              delta: data.deltas.returns,
              icon: RefreshCw,
            },
            {
              label: 'Économies',
              value: `${data.metrics.savings.toLocaleString('fr-FR')}€`,
              delta: data.deltas.savings,
              icon: DollarSign,
            },
          ].map((kpi) => {
            const Icon = kpi.icon
            const isPositive = !kpi.delta.startsWith('-')

            return (
              <Card key={kpi.label} hover>
                <div className="flex items-start justify-between">
                  <div className="min-w-0">
                    <p className="text-xs text-text-tertiary uppercase tracking-widest">
                      {kpi.label}
                    </p>
                    <p className="mt-1 truncate font-display text-2xl text-text-primary">
                      {typeof kpi.value === 'number'
                        ? kpi.value.toLocaleString('fr-FR')
                        : kpi.value}
                    </p>
                    <p
                      className={`mt-0.5 text-xs ${
                        isPositive ? 'text-gen-done' : 'text-status-error'
                      }`}
                    >
                      {kpi.delta} vs mois précédent
                    </p>
                  </div>
                  <Icon className="mt-0.5 h-5 w-5 shrink-0 text-text-tertiary" />
                </div>
              </Card>
            )
          })
        )}
      </motion.div>

      {/* Charts */}
      <motion.div variants={item} className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Try-ons par semaine
          </h3>
          <TryonChart
            data={data?.tryon_history}
            loading={isLoading}
            error={error instanceof Error ? error.message : null}
          />
        </Card>

        <Card>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Top SKUs
          </h3>
          <TopSkusChart
            data={data?.top_skus}
            loading={isLoading}
            error={error instanceof Error ? error.message : null}
          />
        </Card>
      </motion.div>

      {/* Catalogue Table */}
      <motion.div variants={item}>
        <Card>
          <div className="mb-4 flex items-center justify-between gap-4">
            <h3 className="font-heading text-sm text-text-secondary uppercase tracking-widest">
              Catalogue
            </h3>
            <div className="flex shrink-0 gap-2">
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

          {isLoading ? (
            <div className="space-y-3 py-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} variant="text" className="h-5 w-full" />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <Package className="mx-auto h-8 w-8 text-text-tertiary" />
              <p className="mt-3 text-sm text-text-secondary">
                Aucun produit dans votre catalogue
              </p>
              <p className="text-xs text-text-tertiary">
                Ajoutez vos premiers vêtements pour commencer
              </p>
            </div>
          )}
        </Card>
      </motion.div>
    </motion.div>
  )
}
