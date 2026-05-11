'use client'

import { useMemo } from 'react'

export function useMediaQuery(query: string): boolean {
  if (typeof window === 'undefined') return false

  // eslint-disable-next-line react-hooks/rules-of-hooks
  return useMemo(() => window.matchMedia(query).matches, [query])
}

export function useBreakpoint() {
  const isSm = useMediaQuery('(min-width: 640px)')
  const isMd = useMediaQuery('(min-width: 768px)')
  const isLg = useMediaQuery('(min-width: 1024px)')
  const isXl = useMediaQuery('(min-width: 1280px)')

  return { isSm, isMd, isLg, isXl, isMobile: !isMd }
}
