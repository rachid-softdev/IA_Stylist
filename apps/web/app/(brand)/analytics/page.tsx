'use client'

import { Card } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Analytics</h1>
        <p className="mt-1 text-text-secondary">Analysez les performances de vos try-ons</p>
      </div>

      <Card>
        <div className="flex h-64 items-center justify-center">
          <BarChart3 className="h-8 w-8 text-text-tertiary" />
          <span className="ml-3 text-sm text-text-secondary">Analytics détaillés à venir</span>
        </div>
      </Card>
    </div>
  )
}
