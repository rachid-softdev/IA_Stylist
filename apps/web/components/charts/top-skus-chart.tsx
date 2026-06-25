'use client'

import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Skeleton } from '@/components/ui/skeleton'

interface TopSku {
  sku: string
  name: string
  tryons: number
}

interface TopSkusChartProps {
  data?: TopSku[]
  loading?: boolean
  error?: string | null
}

const fallbackData: TopSku[] = [
  { sku: 'VFS-001', name: 'Robe été', tryons: 89 },
  { sku: 'VFS-002', name: 'Blazer noir', tryons: 72 },
  { sku: 'VFS-003', name: 'Jean slim', tryons: 58 },
  { sku: 'VFS-004', name: 'Pull cachemire', tryons: 45 },
  { sku: 'VFS-005', name: 'Veste cuir', tryons: 34 },
]

export function TopSkusChart({ data, loading, error }: TopSkusChartProps) {
  const chartData = data ?? fallbackData

  const colors = useMemo(() => {
    if (typeof window === 'undefined') {
      return { text: '#9A9185', accent: '#D4A853', grid: '#2E2E2E', surface: '#111111' }
    }
    const style = getComputedStyle(document.documentElement)
    return {
      text: style.getPropertyValue('--text-secondary').trim() || '#9A9185',
      accent: style.getPropertyValue('--accent-primary').trim() || '#D4A853',
      warm: style.getPropertyValue('--accent-warm').trim() || '#C8956A',
      grid: style.getPropertyValue('--border-default').trim() || '#2E2E2E',
      surface: style.getPropertyValue('--bg-surface').trim() || '#111111',
    }
  }, [])

  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="w-full space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="text" className="h-6 w-full" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-48 items-center justify-center rounded bg-bg-elevated">
        <p className="text-sm text-status-error">{error}</p>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded bg-bg-elevated">
        <p className="text-sm text-text-tertiary">Aucune donnée disponible</p>
      </div>
    )
  }

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 8, left: 4, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} horizontal={false} />
          <XAxis
            type="number"
            axisLine={false}
            tickLine={false}
            tick={{ fill: colors.text, fontSize: 11 }}
            allowDecimals={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: colors.text, fontSize: 11 }}
            width={90}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: colors.surface,
              border: `1px solid ${colors.grid}`,
              borderRadius: '6px',
              fontSize: '12px',
              color: colors.text,
            }}
            labelStyle={{ color: colors.text, fontWeight: 600 }}
            formatter={(value) => [`${value ?? 0} try-ons`, '']}
          />
          <Bar
            dataKey="tryons"
            fill={colors.accent}
            radius={[0, 3, 3, 0]}
            barSize={16}
            animationDuration={800}
            animationEasing="ease-out"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
