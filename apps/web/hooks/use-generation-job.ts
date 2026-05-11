'use client'

import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { api } from '@/lib/api'
import type { JobStatus } from '@vfs/shared-types'

interface JobData {
  id: string
  status: JobStatus
  result_url?: string
  error_message?: string
  result_metadata?: Record<string, unknown>
  job_type: string
  credits_used: number
  ai_provider?: string
  duration_ms?: number
}

export function useGenerationJob(
  jobId: string | null,
  onStatusChange?: (status: JobStatus) => void,
  onResult?: (url: string, metadata?: Record<string, unknown>) => void,
  onError?: (message: string) => void,
) {
  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      const res = await api.get<JobData>(`/generate/jobs/${jobId}`)
      return res.data
    },
    enabled: !!jobId && jobId !== '',
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return 5000
      if (data.status === 'done' || data.status === 'error' || data.status === 'cancelled')
        return false
      return 3000
    },
  })

  useEffect(() => {
    if (!query.data) return

    const { status, result_url, result_metadata, error_message } = query.data

    onStatusChange?.(status)

    if (status === 'done' && result_url) {
      onResult?.(result_url, result_metadata as Record<string, unknown> | undefined)
    }

    if (status === 'error' && error_message) {
      onError?.(error_message)
    }
  }, [query.data])

  return query
}
