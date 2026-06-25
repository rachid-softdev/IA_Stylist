'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@vfs/utils'
import { useState } from 'react'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { HelpDialog } from '@/components/ui/help-dialog'
import { useAuthStore } from '@/stores/auth-store'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Package,
  BarChart3,
  Key,
  CreditCard,
  Users,
  Settings,
  ShoppingBag,
  Menu,
  X,
  ChevronDown,
  Coins,
} from 'lucide-react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/catalog', label: 'Catalogue', icon: Package },
  { href: '/analytics', label: 'Analyses', icon: BarChart3 },
  { href: '/members', label: 'Membres', icon: Users },
  { href: '/widget', label: 'Widget Shopify', icon: ShoppingBag },
  { href: '/api-keys', label: 'Clés API', icon: Key },
  { href: '/billing', label: 'Facturation', icon: CreditCard },
  { href: '/settings', label: 'Paramètres', icon: Settings },
]

export function BrandSidebar() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const { user } = useAuthStore()

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 rounded-md p-2 text-text-primary hover:bg-bg-overlay lg:hidden"
        aria-label="Menu"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      <aside
        className={cn(
          'sidebar-panel fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border-subtle bg-bg-surface transition-transform duration-200 lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex items-center gap-3 px-6 py-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent-primary text-sm font-bold text-text-inverse">
            V
          </div>
          <span className="font-heading text-lg tracking-wide text-text-primary">
            VFS
          </span>
          <span className="rounded-full border border-accent-primary/30 px-2 py-0.5 text-2xs text-accent-primary">
            Marque
          </span>
        </div>

        <nav className="flex-1 px-3 py-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = pathname.startsWith(item.href)

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={cn(
                  'mb-0.5 flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-all duration-150',
                  active
                    ? 'bg-bg-overlay text-text-primary font-medium'
                    : 'text-text-secondary hover:bg-bg-overlay hover:text-text-primary',
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-border-subtle p-3 space-y-2">
          {/* Credits */}
          <div className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-text-secondary">
            <Coins className="h-4 w-4 text-accent-primary" />
            <AnimatePresence mode="wait">
              <motion.span
                key={user?.credits ?? 0}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              >
                {user?.credits ?? 0} crédits
              </motion.span>
            </AnimatePresence>
          </div>

          {/* Theme toggle */}
          <div className="flex items-center justify-between rounded-md px-3 py-1">
            <span className="text-xs text-text-tertiary">Thème</span>
            <div className="flex items-center gap-1">
              <HelpDialog />
              <ThemeToggle />
            </div>
          </div>

          {/* Back to app */}
          <Link
            href="/"
            className="flex items-center gap-2 rounded-md border border-border-default px-3 py-2 text-xs text-text-secondary hover:bg-bg-overlay hover:text-text-primary transition-colors"
          >
            <ChevronDown className="h-3 w-3 -rotate-90" />
            Retour à l&apos;app
          </Link>
        </div>
      </aside>

      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}
