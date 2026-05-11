'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createContext, useContext, useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import type { SupabaseClient } from '@supabase/supabase-js'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      gcTime: 1000 * 60 * 60,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

type SupabaseContextType = {
  supabase: SupabaseClient | null
}

const SupabaseContext = createContext<SupabaseContextType>({ supabase: null })

export function useSupabase() {
  return useContext(SupabaseContext)
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [supabase, setSupabase] = useState<SupabaseClient | null>(null)

  useEffect(() => {
    const client = createClientComponentClient()
    setSupabase(client)
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <SupabaseContext.Provider value={{ supabase }}>
        {children}
      </SupabaseContext.Provider>
    </QueryClientProvider>
  )
}
