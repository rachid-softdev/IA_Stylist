'use client'

import Image from 'next/image'
import { cn } from '@vfs/utils'
import { useCallback, useState, type DragEvent } from 'react'
import { Camera, Upload, AlertCircle } from 'lucide-react'

interface UploadZoneProps {
  onFile: (file: File) => void
  accept?: string
  maxSizeMB?: number
  preview?: string | null
  label?: string
  description?: string
  error?: string | null
  className?: string
}

export function UploadZone({
  onFile,
  accept = 'image/jpeg,image/png,image/webp',
  maxSizeMB = 10,
  preview,
  label = 'Glissez votre photo ici',
  description = 'ou cliquez pour sélectionner',
  error,
  className,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file) {
        if (file.size > maxSizeMB * 1024 * 1024) {
          return
        }
        onFile(file)
      }
    },
    [onFile, maxSizeMB],
  )

  const handleClick = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = accept
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) onFile(file)
    }
    input.click()
  }

  const handleCameraCapture = (e: React.MouseEvent) => {
    e.stopPropagation()
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = accept
    input.capture = 'environment'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) onFile(file)
    }
    input.click()
  }

  const isMobile = typeof window !== 'undefined' && 'ontouchstart' in window

  const isFileSelected = !!preview

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Uploader votre photo. Formats acceptés : JPEG, PNG, WebP`}
      aria-dropeffect="copy"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      className={cn(
        'relative flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 text-center transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary min-h-[200px]',
        isDragging && 'border-accent-primary bg-bg-overlay',
        isFileSelected && 'border-solid border-border-default p-2',
        error ? 'border-status-error' : 'border-border-default hover:border-accent-primary hover:bg-bg-overlay',
        className,
      )}
    >
      {preview ? (
        <div className="relative w-full h-full">
          <Image
            src={preview}
            alt="Preview"
            fill
            className="object-contain rounded-md"
            sizes="(max-width: 768px) 100vw, 300px"
            unoptimized
          />
          <div className="absolute bottom-2 right-2 rounded-md bg-bg-base/80 px-2 py-1 text-xs text-text-secondary">
            Cliquez pour remplacer
          </div>
        </div>
      ) : (
        <>
          {error ? (
            <AlertCircle className="h-6 w-6 text-status-error" />
          ) : (
            <Upload className="h-6 w-6 text-text-tertiary" />
          )}
          <div>
            <p className={cn('text-sm', error ? 'text-status-error' : 'text-text-primary')}>
              {error || label}
            </p>
            <p className="mt-1 text-xs text-text-tertiary">{description}</p>
          </div>
          {/* Camera capture button (mobile only) */}
          {isMobile && !error && (
            <button
              type="button"
              onClick={handleCameraCapture}
              className="flex items-center gap-2 rounded-md bg-accent-primary/10 px-4 py-2 text-xs font-medium text-accent-primary transition-colors hover:bg-accent-primary/20"
            >
              <Camera className="h-3.5 w-3.5" />
              Prendre une photo
            </button>
          )}
          <p className="text-xs text-text-tertiary">
            JPEG, PNG, WebP — Max {maxSizeMB}MB
          </p>
        </>
      )}
    </div>
  )
}
