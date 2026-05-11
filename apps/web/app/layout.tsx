import type { Metadata } from 'next'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toast'
import './globals.css'

export const metadata: Metadata = {
  title: 'VFS — Virtual Fashion Studio',
  description: 'Transformez n\'importe quel vêtement en shooting professionnel en 60 secondes.',
  metadataBase: new URL('https://vfs.ai'),
  openGraph: {
    title: 'Virtual Fashion Studio',
    description: 'Shooting photo par IA en 60 secondes.',
    type: 'website',
    siteName: 'VFS',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('vfs-theme');
                  if (theme === 'dark' || theme === 'light') {
                    document.documentElement.setAttribute('data-theme', theme);
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-bg-base text-text-primary antialiased">
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}
