import { useEffect, useState } from "react"
import type { User } from "@vfs/shared-types"

interface UseServerUserResult {
  user: User | null
  isLoading: boolean
  error: Error | null
}

export function useServerUser(): UseServerUserResult {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchUser() {
      try {
        const res = await fetch("/api/auth/me")
        if (!res.ok) {
          throw new Error(`Failed to fetch user: ${res.status}`)
        }
        const data = await res.json()
        if (!cancelled) {
          setUser(data.user ?? null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error("Unknown error"))
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    fetchUser()

    return () => {
      cancelled = true
    }
  }, [])

  return { user, isLoading, error }
}
