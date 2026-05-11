'use client'

import { useState, useCallback } from 'react'
import { api } from '@/lib/api'

interface UseUploadOptions {
  folder: string
  onProgress?: (progress: number) => void
  onSuccess?: (url: string, r2Key: string) => void
  onError?: (error: string) => void
}

export function useUpload(options: UseUploadOptions) {
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null)

  const upload = useCallback(
    async (file: File) => {
      setError(null)
      setIsUploading(true)
      setProgress(0)

      try {
        const result = await api.uploadFile(file, options.folder, (p) => {
          setProgress(p)
          options.onProgress?.(p)
        })

        setUploadedUrl(result.public_url)
        options.onSuccess?.(result.public_url, result.r2_key)

        return result
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed'
        setError(message)
        options.onError?.(message)
        return null
      } finally {
        setIsUploading(false)
      }
    },
    [options.folder],
  )

  const reset = useCallback(() => {
    setProgress(0)
    setError(null)
    setUploadedUrl(null)
  }, [])

  return {
    upload,
    reset,
    isUploading,
    progress,
    error,
    uploadedUrl,
  }
}
