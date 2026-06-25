'use client'

import { useEffect, useRef, useState } from 'react'

/**
 * Spring solver configuration for a subtle overshoot (~3%).
 * Higher stiffness = faster, lower damping = more overshoot.
 */
function springOvershoot(t: number, end: number) {
  // Stiffness & damping tuned for ~3% overshoot, settle in ~800ms
  const stiffness = 180
  const damping = 16
  const mass = 1

  // Semi-implicit Euler integration
  let pos = 0
  let vel = 0
  const dt = 1 / 60
  const steps = Math.floor(t / dt)

  for (let i = 0; i < steps; i++) {
    const displacement = pos - end
    const force = -stiffness * displacement - damping * vel
    const accel = force / mass
    vel += accel * dt
    pos += vel * dt
  }

  return pos
}

/**
 * Animated counter that counts from 0 to `end` using spring physics
 * when the element becomes visible. The spring gives a subtle overshoot
 * (~2-3%) before settling — feels alive but restrained.
 */
export function useAnimatedCounter(end: number, duration = 800) {
  const [count, setCount] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el || started.current) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting && !started.current) {
          started.current = true
          const startTime = performance.now()

          function animate(now: number) {
            const elapsed = now - startTime
            const t = Math.min(elapsed / 1000, duration / 1000)
            const raw = springOvershoot(t, end)
            // Round to integer, clamp final frame to exact `end`
            const rounded = t >= duration / 1000 ? end : Math.round(raw)
            setCount(rounded)
            if (elapsed < duration) {
              requestAnimationFrame(animate)
            }
          }

          requestAnimationFrame(animate)
        }
      },
      { threshold: 0.3 },
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [end, duration])

  return { count, ref }
}
