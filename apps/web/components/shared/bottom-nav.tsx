'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@vfs/utils'
import { Camera, Clapperboard, Sparkles, User } from 'lucide-react'

const navItems = [
  { href: '/studio', label: 'Studio', icon: Camera },
  { href: '/dressing', label: 'Dressing', icon: Clapperboard },
  { href: '/stylist', label: 'Stylist', icon: Sparkles },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t border-border-subtle bg-bg-surface/95 backdrop-blur-sm lg:hidden safe-area-pb">
      {navItems.map((item) => {
        const Icon = item.icon
        const active = pathname === item.href

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex flex-col items-center gap-0.5 py-3 px-4 text-xs transition-colors duration-150',
              active ? 'text-accent-primary' : 'text-text-tertiary',
            )}
          >
            <Icon className="h-5 w-5" />
            <span>{item.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
