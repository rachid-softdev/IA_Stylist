'use client'

import { useUpload } from '@/hooks/use-upload'
import { UploadZone } from '@/components/ui/upload-zone'
import { useToastStore } from '@/stores/toast-store'
import { useCallback, useEffect, useState } from 'react'

interface PhotoUploadProps {
  preview: string | null
  onUpload: (photo: { url: string; r2_key: string }) => void
  error?: string | null
}

export function PhotoUploadZone({ preview, onUpload, error }: PhotoUploadProps) {
  const { addToast } = useToastStore()
  const [localPreview, setLocalPreview] = useState<string | null>(preview || null)

  const { upload, isUploading, progress } = useUpload({
    folder: 'uploads/raw',
    onSuccess: (url, r2Key) => {
      onUpload({ url, r2_key: r2Key })
      setLocalPreview(url)
      addToast({
        type: 'success',
        title: 'Photo uploadée',
        message: 'Votre photo est prête',
      })
    },
    onError: (err) => {
      addToast({
        type: 'error',
        title: 'Échec de l\'upload',
        message: err,
      })
    },
  })

  useEffect(() => {
    if (preview) setLocalPreview(preview)
  }, [preview])

  const handleFile = useCallback(
    async (file: File) => {
      // Client-side validation
      if (file.size > 10 * 1024 * 1024) {
        addToast({
          type: 'error',
          title: 'Fichier trop volumineux',
          message: 'Maximum 10MB',
        })
        return
      }

      // Local preview
      const objectUrl = URL.createObjectURL(file)
      setLocalPreview(objectUrl)

      await upload(file)
    },
    [upload, addToast],
  )

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-heading tracking-wide text-text-secondary uppercase">
        Votre photo
      </h3>
      <UploadZone
        onFile={handleFile}
        preview={localPreview}
        label="Glissez votre photo ici"
        description="Face, 3/4 ou corps entier — JPEG, PNG, WebP"
        error={error || (isUploading ? `Upload en cours... ${Math.round(progress)}%` : undefined)}
      />
      {isUploading && (
        <div className="h-0.5 w-full overflow-hidden rounded-full bg-bg-elevated">
          <div
            className="h-full bg-accent-primary transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}
