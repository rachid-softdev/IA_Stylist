'use client'

import { useState } from 'react'
import { useUpload } from '@/hooks/use-upload'
import { useToastStore } from '@/stores/toast-store'
import { Upload, Package } from 'lucide-react'
import type { GarmentCategory } from '@vfs/shared-types'

interface GarmentSelectorProps {
  selected: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  } | null
  onSelect: (garment: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  }) => void
}

export function GarmentSelector({ selected, onSelect }: GarmentSelectorProps) {
  const { addToast } = useToastStore()
  const [showUpload, setShowUpload] = useState(false)
  const [uploadPreview, setUploadPreview] = useState<string | null>(null)

  const categoryOptions: { value: GarmentCategory; label: string }[] = [
    { value: 'top', label: 'Haut' },
    { value: 'bottom', label: 'Bas' },
    { value: 'dress', label: 'Robe' },
    { value: 'outerwear', label: 'Veste/Manteau' },
    { value: 'shoes', label: 'Chaussures' },
    { value: 'accessories', label: 'Accessoires' },
  ]

  const { upload, isUploading, progress } = useUpload({
    folder: 'uploads/garments',
    onSuccess: (url, _r2Key) => {
      onSelect({
        image_url: url,
        category: 'top', // Default, user can change with CategorySelect
        name: 'Vêtement uploadé',
      })
      setUploadPreview(url)
      addToast({
        type: 'success',
        title: 'Vêtement uploadé',
        message: 'Prêt pour le try-on',
      })
    },
    onError: (err) => {
      addToast({ type: 'error', title: 'Upload échoué', message: err })
    },
  })

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-heading tracking-wide text-text-secondary uppercase">
        Vêtement
      </h3>

      {selected ? (
        <div className="relative rounded-lg border border-border-default bg-bg-surface p-4">
          <div className="flex items-center gap-4">
            <img
              src={selected.image_url}
              alt={selected.name || 'Vêtement'}
              className="h-20 w-20 rounded-md object-cover"
            />
            <div>
              <p className="text-sm font-medium text-text-primary">
                {selected.name || 'Vêtement sélectionné'}
              </p>
              <p className="text-xs text-text-secondary">
                {selected.category && categoryOptions.find(c => c.value === selected.category)?.label}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              onSelect(null as never)
              setUploadPreview(null)
              setShowUpload(false)
            }}
            className="mt-3 text-xs text-text-tertiary hover:text-text-secondary"
          >
            Changer de vêtement
          </button>
        </div>
      ) : showUpload ? (
        <div className="rounded-lg border border-dashed border-border-default p-8 text-center">
          {uploadPreview ? (
            <div className="space-y-3">
              <img
                src={uploadPreview}
                alt="Preview"
                className="mx-auto h-40 w-40 rounded-md object-cover"
              />
              <p className="text-sm text-text-secondary">
                {isUploading ? `Upload... ${Math.round(progress)}%` : 'Vêtement prêt'}
              </p>
            </div>
          ) : (
            <div
              onClick={() => {
                const input = document.createElement('input')
                input.type = 'file'
                input.accept = 'image/png'
                input.onchange = (e) => {
                  const file = (e.target as HTMLInputElement).files?.[0]
                  if (file) upload(file)
                }
                input.click()
              }}
              className="cursor-pointer space-y-2"
            >
              <Upload className="mx-auto h-6 w-6 text-text-tertiary" />
              <p className="text-sm text-text-secondary">
                Cliquez pour uploader un vêtement
              </p>
              <p className="text-xs text-text-tertiary">PNG fond blanc recommandé</p>
            </div>
          )}
          <button
            onClick={() => {
              setShowUpload(false)
              setUploadPreview(null)
            }}
            className="mt-3 text-xs text-text-tertiary hover:text-text-secondary"
          >
            Annuler
          </button>
        </div>
      ) : (
        <div className="flex gap-3">
          <button
            onClick={() => setShowUpload(true)}
            className="flex flex-1 items-center justify-center gap-3 rounded-lg border border-dashed border-border-default p-6 text-center transition-all hover:border-accent-primary hover:bg-bg-overlay"
          >
            <Upload className="h-5 w-5 text-text-tertiary" />
            <span className="text-sm text-text-secondary">Uploader un vêtement</span>
          </button>
          <button
            onClick={() => {
              // TODO: Open catalog browser
              addToast({ type: 'info', title: 'Catalogue', message: 'Fonctionnalité à venir' })
            }}
            className="flex flex-1 items-center justify-center gap-3 rounded-lg border border-dashed border-border-default p-6 text-center transition-all hover:border-accent-primary hover:bg-bg-overlay"
          >
            <Package className="h-5 w-5 text-text-tertiary" />
            <span className="text-sm text-text-secondary">Parcourir le catalogue</span>
          </button>
        </div>
      )}
    </div>
  )
}
