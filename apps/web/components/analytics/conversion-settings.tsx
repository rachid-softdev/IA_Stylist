'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Dialog } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Settings2, Save } from 'lucide-react'

interface ConversionEntry {
  period: string
  orders: number
  returns: number
  updated_at: string | null
}

interface ConversionData {
  data: ConversionEntry[]
}

export function ConversionSettings() {
  const [open, setOpen] = useState(false)
  const [period, setPeriod] = useState('')
  const [orders, setOrders] = useState('')
  const [returns, setReturns] = useState('')
  const queryClient = useQueryClient()

  // Set default period to current month on mount
  useEffect(() => {
    const now = new Date()
    setPeriod(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
  }, [])

  const { data: conversionData, isLoading } = useQuery<ConversionData>({
    queryKey: ['shopify-conversion'],
    queryFn: () => api.get<ConversionData>('/brands/me/shopify/conversion').then(r => r.data),
    enabled: open,
  })

  const mutation = useMutation({
    mutationFn: (body: { period: string; orders: number; returns: number }) =>
      api.put('/brands/me/shopify/conversion', body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopify-conversion'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
      queryClient.invalidateQueries({ queryKey: ['brand-dashboard'] })
      setOrders('')
      setReturns('')
    },
  })

  const entries = conversionData?.data || []
  const latestEntry = entries[0]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      period,
      orders: parseInt(orders) || 0,
      returns: parseInt(returns) || 0,
    })
  }

  const fillFromLatest = () => {
    if (latestEntry && !orders && !returns) {
      setOrders(String(latestEntry.orders))
      setReturns(String(latestEntry.returns))
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="ml-1 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-accent-primary hover:bg-accent-primary/10 transition-colors"
        title="Paramètres Shopify"
      >
        <Settings2 className="h-3 w-3" />
      </button>

      <Dialog open={open} onClose={() => setOpen(false)} title="Données Shopify">
        <div className="p-6">

          {!isLoading && entries.length > 0 && (
            <div className="mb-4 rounded-lg border border-border-subtle bg-bg-elevated p-3">
              <p className="text-xs text-text-tertiary uppercase tracking-widest mb-2">
                Dernière saisie
              </p>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-xs text-text-secondary">Période</p>
                  <p className="font-display text-sm text-text-primary">{latestEntry.period}</p>
                </div>
                <div>
                  <p className="text-xs text-text-secondary">Commandes</p>
                  <p className="font-display text-sm text-text-primary">{latestEntry.orders}</p>
                </div>
                <div>
                  <p className="text-xs text-text-secondary">Retours</p>
                  <p className="font-display text-sm text-text-primary">{latestEntry.returns}</p>
                </div>
              </div>
            </div>
          )}

          {entries.length > 1 && (
            <details className="mb-4">
              <summary className="cursor-pointer text-xs text-text-tertiary hover:text-text-secondary transition-colors">
                Historique ({entries.length - 1} mois)
              </summary>
              <div className="mt-2 space-y-1">
                {entries.slice(1).map((entry) => (
                  <div key={entry.period} className="grid grid-cols-3 gap-3 rounded bg-bg-surface px-3 py-1.5 text-xs text-text-secondary">
                    <span>{entry.period}</span>
                    <span>{entry.orders} commandes</span>
                    <span>{entry.returns} retours</span>
                  </div>
                ))}
              </div>
            </details>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs text-text-secondary mb-1">Période</label>
              <input
                type="month"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full rounded-lg border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
                required
                onFocus={fillFromLatest}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-text-secondary mb-1">Commandes</label>
                <input
                  type="number"
                  min="0"
                  value={orders}
                  onChange={(e) => setOrders(e.target.value)}
                  placeholder="0"
                  className="w-full rounded-lg border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
                />
              </div>
              <div>
                <label className="block text-xs text-text-secondary mb-1">Retours</label>
                <input
                  type="number"
                  min="0"
                  value={returns}
                  onChange={(e) => setReturns(e.target.value)}
                  placeholder="0"
                  className="w-full rounded-lg border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
                />
              </div>
            </div>
            {mutation.isSuccess && (
              <p className="text-xs text-gen-done">Données enregistrées ✓</p>
            )}
            {mutation.isError && (
              <p className="text-xs text-status-error">Erreur lors de l'enregistrement</p>
            )}
            <Button
              type="submit"
              size="sm"
              className="w-full"
              disabled={mutation.isPending}
              iconLeft={<Save className="h-3.5 w-3.5" />}
            >
              {mutation.isPending ? 'Enregistrement...' : 'Enregistrer'}
            </Button>
          </form>
        </div>
      </Dialog>
    </>
  )
}
