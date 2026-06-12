'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, Package, RefreshCw, DollarSign } from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

interface OverviewData {
  total_tryons: number
  tryons_delta: number
  conversion_rate: number
  conversion_delta: number
  returns_saved: number
  returns_delta: number
  cost_savings: number
  savings_delta: number
  is_estimate: boolean
}

interface TimePoint {
  date: string
  count: number
}

interface TopSku {
  garment_id: string
  name: string
  sku: string
  tryons: number
}

interface AnalyticsResponse {
  data: OverviewData
  time_series: TimePoint[]
  top_skus: TopSku[]
}

const RANGE_OPTIONS = [
  { label: '7 jours', value: 7 },
  { label: '30 jours', value: 30 },
  { label: '90 jours', value: 90 },
] as const

export default function AnalyticsPage() {
  const [days, setDays] = useState(30)

  const { data, isLoading } = useQuery({
    queryKey: ['analytics', days],
    queryFn: async () => {
      const res = await api.get<AnalyticsResponse>(`/analytics/brand-id/overview?days=${days}`)
      return res.data
    },
  })

  const overview = data?.data
  const maxCount = Math.max(...(data?.time_series?.map(t => t.count) || [1]), 1)

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Analytics</h1>
          <p className="mt-1 text-text-secondary">Analysez les performances de vos try-ons</p>
        </div>
        <div className="flex gap-2">
          {RANGE_OPTIONS.map(opt => (
            <button
              key={opt.value}
              onClick={() => setDays(opt.value)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                days === opt.value
                  ? 'bg-accent-primary text-text-inverse'
                  : 'bg-bg-elevated text-text-secondary hover:text-text-primary'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* KPI Row */}
      <motion.div variants={item} className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} hover={false}>
              <Skeleton className="mb-2 h-3 w-16" />
              <Skeleton className="h-8 w-24" />
            </Card>
          ))
        ) : (
          <>
            <Card hover>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-text-tertiary uppercase tracking-widest">Try-ons</p>
                  <p className="mt-1 font-display text-2xl text-text-primary">{overview?.total_tryons || 0}</p>
                  <p className={`mt-0.5 text-xs ${(overview?.tryons_delta || 0) >= 0 ? 'text-gen-done' : 'text-status-error'}`}>
                    {overview?.tryons_delta || 0}% vs période préc.
                  </p>
                </div>
                <Package className="h-5 w-5 text-text-tertiary" />
              </div>
            </Card>
            <Card hover>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-text-tertiary uppercase tracking-widest">Conversion</p>
                  <p className="mt-1 font-display text-2xl text-text-primary">{overview?.conversion_rate || 0}%</p>
                  <p className="mt-0.5 text-xs text-text-tertiary">Via Shopify</p>
                </div>
                <TrendingUp className="h-5 w-5 text-text-tertiary" />
              </div>
            </Card>
            <Card hover>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-text-tertiary uppercase tracking-widest">Retours évités</p>
                  <p className="mt-1 font-display text-2xl text-text-primary">{overview?.returns_saved || 0}</p>
                  <p className="mt-0.5 text-xs text-gen-done">Estimé (-25%)</p>
                </div>
                <RefreshCw className="h-5 w-5 text-text-tertiary" />
              </div>
            </Card>
            <Card hover>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-text-tertiary uppercase tracking-widest">Économies</p>
                  <p className="mt-1 font-display text-2xl text-text-primary">{overview?.cost_savings?.toLocaleString() || 0}€</p>
                  <p className="mt-0.5 text-xs text-text-tertiary">vs shooting classique</p>
                </div>
                <DollarSign className="h-5 w-5 text-text-tertiary" />
              </div>
            </Card>
          </>
        )}
      </motion.div>

      {/* Charts */}
      <motion.div variants={item} className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card hover={false}>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Try-ons par jour
          </h3>
          {isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
                <div className="flex h-48 items-end gap-1" role="img" aria-label="Graphique des try-ons par jour">
              {(data?.time_series || []).map((point) => {
                const formattedDate = new Date(point.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
                return (
                  <div
                    key={point.date}
                    className="flex-1 rounded-t bg-accent-primary/30 hover:bg-accent-primary/50 transition-colors relative group"
                    style={{ height: `${(point.count / maxCount) * 100}%` }}
                    role="graphics-symbol"
                    aria-label={`${formattedDate}: ${point.count} try-ons`}
                  >
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 hidden group-hover:block text-2xs text-text-secondary whitespace-nowrap bg-bg-surface px-1.5 py-0.5 rounded">
                      {formattedDate} — {point.count}
                    </div>
                  </div>
                )
              })}
              {(!data?.time_series || data.time_series.length === 0) && (
                <div className="flex h-full w-full items-center justify-center text-sm text-text-tertiary">
                  Aucune donnée
                </div>
              )}
            </div>
          )}
        </Card>

        <Card hover={false}>
          <h3 className="mb-4 font-heading text-sm text-text-secondary uppercase tracking-widest">
            Top SKUs
          </h3>
          {isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <div className="space-y-2">
              {(data?.top_skus || []).slice(0, 6).map((sku) => {
                const pct = ((sku.tryons) / (overview?.total_tryons || 1)) * 100
                return (
                  <div key={sku.garment_id} className="flex items-center gap-3">
                    <span className="w-16 truncate text-xs text-text-secondary">{sku.sku || sku.name}</span>
                    <div className="flex-1 h-4 rounded-full bg-bg-elevated overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent-primary/40"
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-text-secondary w-8 text-right">{sku.tryons}</span>
                  </div>
                )
              })}
              {(!data?.top_skus || data.top_skus.length === 0) && (
                <div className="flex h-full items-center justify-center text-sm text-text-tertiary">
                  Essayez des vêtements pour voir les données
                </div>
              )}
            </div>
          )}
        </Card>
      </motion.div>

      {overview?.is_estimate && (
        <motion.p variants={item} className="text-xs text-text-tertiary text-center">
          * Les données de conversion et retours sont des estimations basées sur les moyennes du secteur.
          Connectez votre boutique Shopify pour des données précises.
        </motion.p>
      )}
    </motion.div>
  )
}
