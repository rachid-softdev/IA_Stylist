'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createContext, useContext, useEffect, useState } from 'react'
import { createBrowserClient } from '@supabase/ssr'
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
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseKey) {
      throw new Error(
        'Missing Supabase environment variables.\n' +
        'Ensure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set.',
      )
    }

    const client = createBrowserClient(supabaseUrl, supabaseKey)
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
