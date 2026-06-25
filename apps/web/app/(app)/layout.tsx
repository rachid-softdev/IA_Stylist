'use client'

import { MotionConfig } from 'framer-motion'
import { Sidebar } from '@/components/shared/sidebar'
import { BottomNav } from '@/components/shared/bottom-nav'
import { PageTransition } from '@/components/shared/page-transition'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig reducedMotion="user">
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 lg:pl-60 pb-14 lg:pb-0">
          <div className="mx-auto max-w-grid px-4 py-8 md:px-8">
            <PageTransition>{children}</PageTransition>
          </div>
        </main>
        <BottomNav />
      </div>
    </MotionConfig>
  )
}
