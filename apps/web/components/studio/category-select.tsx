import type { GarmentCategory } from '@vfs/shared-types'

interface CategorySelectProps {
  value: GarmentCategory | null
  onChange: (category: GarmentCategory) => void
}

const options: { value: GarmentCategory; label: string }[] = [
  { value: 'top', label: 'Haut' },
  { value: 'bottom', label: 'Bas' },
  { value: 'dress', label: 'Robe' },
  { value: 'outerwear', label: 'Veste/Manteau' },
  { value: 'shoes', label: 'Chaussures' },
  { value: 'accessories', label: 'Accessoires' },
]

export function CategorySelect({ value, onChange }: CategorySelectProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-heading tracking-wide text-text-secondary uppercase">
        Catégorie
      </h3>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={`rounded-md border px-3 py-1.5 text-sm transition-all duration-200 ${
              value === opt.value
                ? 'border-accent-primary bg-accent-primary/10 text-accent-primary'
                : 'border-border-default text-text-secondary hover:border-border-strong'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
