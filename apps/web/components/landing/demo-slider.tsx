'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

interface DemosliderProps {
  beforeSrc: string
  afterSrc: string
  beforeLabel?: string
  afterLabel?: string
  className?: string
}

export function Demoslider({
  beforeSrc,
  afterSrc,
  beforeLabel = 'Votre photo',
  afterLabel = 'Try-on IA',
  className,
}: DemosliderProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState(50)
  const [isDragging, setIsDragging] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)

  const handlePointerMove = useCallback(
    (e: PointerEvent) => {
      if (!containerRef.current || !isDragging) return
      const rect = containerRef.current.getBoundingClientRect()
      const x = Math.min(Math.max(e.clientX - rect.left, 0), rect.width)
      setPosition((x / rect.width) * 100)
      setHasInteracted(true)
    },
    [isDragging],
  )

  const handlePointerUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handlePointerDown = useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault()
      setIsDragging(true)
      setHasInteracted(true)
    },
    [],
  )

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('pointermove', handlePointerMove)
      document.addEventListener('pointerup', handlePointerUp)
      document.body.style.cursor = 'ew-resize'
      document.body.style.userSelect = 'none'
    }
    return () => {
      document.removeEventListener('pointermove', handlePointerMove)
      document.removeEventListener('pointerup', handlePointerUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, handlePointerMove, handlePointerUp])

  // Keyboard controls
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const step = 5
      if (e.key === 'ArrowLeft') {
        setPosition((p) => Math.max(0, p - step))
        setHasInteracted(true)
      } else if (e.key === 'ArrowRight') {
        setPosition((p) => Math.min(100, p + step))
        setHasInteracted(true)
      }
    },
    [],
  )

  // Click to seek
  const handleContainerClick = useCallback(
    (e: React.MouseEvent) => {
      if (isDragging) return
      const rect = containerRef.current?.getBoundingClientRect()
      if (!rect) return
      const x = e.clientX - rect.left
      setPosition((x / rect.width) * 100)
      setHasInteracted(true)
    },
    [isDragging],
  )

  return (
    <div
      ref={containerRef}
      className={`group relative aspect-[4/5] w-full max-w-lg cursor-ew-resize overflow-hidden rounded-xl border border-border-default bg-bg-elevated select-none ${className ?? ''}`}
      role="slider"
      aria-label="Comparaison avant/après du try-on"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(position)}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onClick={handleContainerClick}
      onPointerDown={handlePointerDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onPointerEnter={() => setIsHovered(true)}
      onPointerLeave={() => setIsHovered(false)}
    >
      {/* Before image (full width) */}
      <img
        src={beforeSrc}
        alt="Photo originale avant application du vêtement"
        className="absolute inset-0 h-full w-full object-cover"
        draggable={false}
      />

      {/* After image (clipped) */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${position}%` }}
        aria-hidden
      >
        <img
          src={afterSrc}
          alt="Résultat après application du vêtement par IA"
          className="absolute inset-0 h-full w-full object-cover"
          style={{ width: `${100 / (position / 100)}%` }}
          draggable={false}
        />
      </div>

      {/* Divider line */}
      <div
        className="absolute inset-y-0 z-10 w-0.5 transition-colors duration-150"
        style={{
          left: `${position}%`,
          backgroundColor: isDragging
            ? 'var(--accent-primary)'
            : isHovered
              ? 'var(--accent-primary)'
              : 'var(--text-primary)',
        }}
      >
        {/* Handle circle */}
        <div
          className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-lg ring-2 transition-all duration-150 ${
            isDragging
              ? 'h-10 w-10 ring-accent-primary bg-accent-primary'
              : 'h-8 w-8 ring-text-primary bg-bg-surface'
          }`}
        >
          <div className="flex h-full items-center justify-center gap-0.5">
            <svg
              width="8"
              height="14"
              viewBox="0 0 8 14"
              fill="none"
              className={isDragging ? 'text-text-inverse' : 'text-text-primary'}
              aria-hidden
            >
              <path
                d="M1 1L6 7L1 13"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <svg
              width="8"
              height="14"
              viewBox="0 0 8 14"
              fill="none"
              className={isDragging ? 'text-text-inverse' : 'text-text-primary'}
              aria-hidden
            >
              <path
                d="M7 1L2 7L7 13"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Labels */}
      <div
        className="pointer-events-none absolute bottom-3 left-3 z-20 transition-opacity duration-200"
        style={{ opacity: isDragging ? 0.4 : 1 }}
      >
        <span className="rounded-md bg-black/60 px-2 py-1 text-2xs font-medium text-white/90 backdrop-blur-sm">
          {beforeLabel}
        </span>
      </div>
      <div
        className="pointer-events-none absolute bottom-3 right-3 z-20 transition-opacity duration-200"
        style={{ opacity: isDragging ? 0.4 : 1 }}
      >
        <span className="rounded-md bg-accent-primary/80 px-2 py-1 text-2xs font-medium text-text-inverse backdrop-blur-sm">
          {afterLabel}
        </span>
      </div>

      {/* Hint on first view */}
      {!hasInteracted && (
        <div className="pointer-events-none absolute inset-x-0 top-3 z-20 flex justify-center">
          <span className="animate-fade-in rounded-full bg-black/50 px-3 py-1 text-2xs text-white/80 backdrop-blur-sm">
            Faites glisser pour comparer
          </span>
        </div>
      )}
    </div>
  )
}
