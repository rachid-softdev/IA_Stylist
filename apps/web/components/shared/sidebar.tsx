'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@vfs/utils'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Avatar } from '@/components/ui/avatar'
import {
  Camera,
  Clapperboard,
  Sparkles,
  Settings,
  Coins,
  Menu,
  X,
} from 'lucide-react'
import { useAuthStore } from '@/stores/auth-store'
import { useState } from 'react'

const navItems = [
  { href: '/studio', label: 'Studio', icon: Camera },
  { href: '/dressing', label: 'Dressing', icon: Clapperboard },
  { href: '/stylist', label: 'AI Stylist', icon: Sparkles, badge: 'Pro' },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 rounded-md p-2 text-text-primary hover:bg-bg-overlay lg:hidden"
        aria-label="Menu"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border-subtle bg-bg-surface transition-transform duration-200 lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent-primary text-sm font-bold text-text-inverse">
            V
          </div>
          <span className="font-heading text-lg tracking-wide text-text-primary">
            VFS
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = pathname === item.href

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
                {item.badge && (
                  <span className="ml-auto rounded-full bg-accent-primary/15 px-1.5 py-0.5 text-2xs text-accent-primary">
                    {item.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Bottom section */}
        <div className="border-t border-border-subtle p-3">
          {/* Credits */}
          <div className="mb-2 flex items-center gap-2 rounded-md px-3 py-2 text-sm text-text-secondary">
            <Coins className="h-4 w-4 text-accent-primary" />
            <span>{user?.credits ?? 0} crédits</span>
          </div>

          {/* Profile / Settings */}
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-text-secondary hover:bg-bg-overlay hover:text-text-primary"
          >
            <Avatar fallback={user?.email?.[0]} size="sm" />
            <span className="truncate">{user?.email || 'Compte'}</span>
          </Link>

          <div className="mt-2 flex items-center justify-between rounded-md px-3 py-1">
            <ThemeToggle />
            <Link
              href="/settings"
              className="rounded p-2 text-text-tertiary hover:bg-bg-overlay hover:text-text-primary"
            >
              <Settings className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}
