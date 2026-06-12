'use client'

import { MotionConfig } from 'framer-motion'
import { BrandSidebar } from '@/components/shared/brand-sidebar'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/auth-store'
import { useEffect } from 'react'

export default function BrandLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { user, isLoading } = useAuthStore()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-base">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <MotionConfig reducedMotion="user">
      <div className="min-h-screen bg-bg-base">
        <BrandSidebar />
        <div className="lg:pl-60">
          <div className="mx-auto max-w-grid px-4 py-8 md:px-8">
            {children}
          </div>
        </div>
      </div>
    </MotionConfig>
  )
}
