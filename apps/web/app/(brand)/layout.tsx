export default function BrandLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="mx-auto max-w-grid px-4 py-8 md:px-8">
        {children}
      </div>
    </div>
  )
}
