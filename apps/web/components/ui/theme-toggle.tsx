'use client'

import { useTheme } from '@/hooks/use-theme'
import { Moon, Sun, Monitor } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const cycle = () => {
    if (theme === 'dark') setTheme('light')
    else if (theme === 'light') setTheme('system')
    else setTheme('dark')
  }

  return (
    <button
      onClick={cycle}
      className="rounded-md p-2 text-text-tertiary transition-all duration-150 hover:bg-bg-overlay hover:text-text-primary"
      aria-label={`Thème actuel : ${theme}`}
    >
      {theme === 'dark' && <Moon className="h-4 w-4" />}
      {theme === 'light' && <Sun className="h-4 w-4" />}
      {theme === 'system' && <Monitor className="h-4 w-4" />}
    </button>
  )
}
