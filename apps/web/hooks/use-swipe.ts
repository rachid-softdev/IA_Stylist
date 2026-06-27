'use client'

import { useRef, useCallback } from 'react'

interface SwipeHandlers {
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
}

const SWIPE_THRESHOLD = 50

export function useSwipe({ onSwipeLeft, onSwipeRight }: SwipeHandlers) {
  const touchStartX = useRef(0)
  const touchStartY = useRef(0)

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0]
    if (!touch) return
    touchStartX.current = touch.clientX
    touchStartY.current = touch.clientY
  }, [])

  const onTouchEnd = useCallback((e: React.TouchEvent) => {
    const touch = e.changedTouches[0]
    if (!touch) return
    const diffX = touch.clientX - touchStartX.current
    const diffY = touch.clientY - touchStartY.current

    // Ignore vertical swipes
    if (Math.abs(diffY) > Math.abs(diffX)) return

    if (diffX > SWIPE_THRESHOLD) {
      onSwipeRight?.()
    } else if (diffX < -SWIPE_THRESHOLD) {
      onSwipeLeft?.()
    }
  }, [onSwipeLeft, onSwipeRight])

  return { onTouchStart, onTouchEnd }
}
