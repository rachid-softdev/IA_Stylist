import { MotionConfig } from 'framer-motion'
import { BrandSidebar } from '@/components/shared/brand-sidebar'
import { PageTransition } from '@/components/shared/page-transition'
import { createServerSupabase } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function BrandLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createServerSupabase()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <MotionConfig reducedMotion="user">
      <div className="min-h-screen bg-bg-base">
        <BrandSidebar />
        <div className="lg:pl-60">
          <div className="mx-auto max-w-grid px-4 py-8 md:px-8">
            <PageTransition>{children}</PageTransition>
          </div>
        </div>
      </div>
    </MotionConfig>
  )
}
