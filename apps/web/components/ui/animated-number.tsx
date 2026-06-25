'use client'

import { useAnimatedCounter } from '@/hooks/use-animated-counter'

/**
 * Renders a number that counts up from 0 when it enters the viewport.
 * For non-numeric values, renders as-is.
 */
export function AnimatedNumber({ value, locale = 'fr-FR' }: { value: number | string; locale?: string }) {
  const numValue = typeof value === 'number' ? value : Number(value.replace(/[^0-9.,]/g, '').replace(',', '.'))
  const isNumeric = !isNaN(numValue) && typeof value === 'number'

  if (!isNumeric) {
    return <>{value}</>
  }

  return <AnimatedNumberInner end={numValue} locale={locale} />
}

function AnimatedNumberInner({ end, locale }: { end: number; locale: string }) {
  const { count, ref } = useAnimatedCounter(end)

  return <span ref={ref}>{count.toLocaleString(locale)}</span>
}
