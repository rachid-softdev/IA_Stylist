'use client'

import { useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>('system')

  useEffect(() => {
    const stored = localStorage.getItem('vfs-theme') as Theme | null
    if (stored) setThemeState(stored)
  }, [])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    const root = document.documentElement

    if (newTheme === 'system') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', newTheme)
    }

    if (newTheme !== 'system') {
      localStorage.setItem('vfs-theme', newTheme)
    } else {
      localStorage.removeItem('vfs-theme')
    }
  }

  return { theme, setTheme }
}
