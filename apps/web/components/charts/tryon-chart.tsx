'use client'

import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Skeleton } from '@/components/ui/skeleton'

interface TryonChartProps {
  data?: { date: string; count: number }[]
  loading?: boolean
  error?: string | null
}

const fallbackData = [
  { date: 'Sem 1', count: 45 },
  { date: 'Sem 2', count: 82 },
  { date: 'Sem 3', count: 68 },
  { date: 'Sem 4', count: 110 },
  { date: 'Sem 5', count: 94 },
  { date: 'Sem 6', count: 145 },
  { date: 'Sem 7', count: 128 },
  { date: 'Sem 8', count: 190 },
]

export function TryonChart({ data, loading, error }: TryonChartProps) {
  const chartData = data ?? fallbackData

  // Resolve CSS variable values for charts
  const colors = useMemo(() => {
    if (typeof window === 'undefined') {
      return { text: '#9A9185', accent: '#D4A853', grid: '#2E2E2E', surface: '#111111' }
    }
    const style = getComputedStyle(document.documentElement)
    return {
      text: style.getPropertyValue('--text-secondary').trim() || '#9A9185',
      accent: style.getPropertyValue('--accent-primary').trim() || '#D4A853',
      grid: style.getPropertyValue('--border-default').trim() || '#2E2E2E',
      surface: style.getPropertyValue('--bg-surface').trim() || '#111111',
    }
  }, [])

  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="w-full space-y-3">
          <Skeleton variant="text" className="h-4 w-3/4" />
          <Skeleton variant="text" className="h-32 w-full" />
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
        <p className="text-sm text-text-tertiary">Aucune donnée this semaine</p>
      </div>
    )
  }

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: colors.text, fontSize: 11 }}
            dy={8}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: colors.text, fontSize: 11 }}
            dx={-4}
            allowDecimals={false}
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
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke={colors.accent}
            strokeWidth={2}
            dot={{ fill: colors.accent, r: 3, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: colors.accent, strokeWidth: 0 }}
            animationDuration={800}
            animationEasing="ease-out"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
