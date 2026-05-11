import { Sidebar } from '@/components/shared/sidebar'
import { BottomNav } from '@/components/shared/bottom-nav'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 lg:pl-60 pb-14 lg:pb-0">
        <div className="mx-auto max-w-grid px-4 py-8 md:px-8">
          {children}
        </div>
      </main>
      <BottomNav />
    </div>
  )
}
