import { describe, it, expect } from 'vitest'
import { formatBytes, formatRelativeTime, truncate, clamp, isAllowedImageType } from '../index'

describe('formatBytes', () => {
  it('returns "0 B" for zero', () => {
    expect(formatBytes(0)).toBe('0 B')
  })

  it('formats bytes correctly', () => {
    expect(formatBytes(512)).toBe('512 B')
  })

  it('formats kilobytes', () => {
    expect(formatBytes(1024)).toBe('1 KB')
  })

  it('formats megabytes', () => {
    expect(formatBytes(1048576)).toBe('1 MB')
  })

  it('formats gigabytes', () => {
    expect(formatBytes(1073741824)).toBe('1 GB')
  })

  it('formats terabytes', () => {
    expect(formatBytes(1099511627776)).toBe('1 TB')
  })

  it('respects decimals parameter', () => {
    expect(formatBytes(1536, 2)).toBe('1.5 KB')
  })

  it('handles negative bytes as "0 B"', () => {
    expect(formatBytes(-100)).toBe('0 B')
  })
})

describe('formatRelativeTime', () => {
  it('returns "just now" for current time', () => {
    expect(formatRelativeTime(new Date().toISOString())).toBe('just now')
  })

  it('returns minutes ago for recent past', () => {
    const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000)
    expect(formatRelativeTime(fiveMinAgo.toISOString())).toBe('5m ago')
  })

  it('returns hours ago', () => {
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000)
    expect(formatRelativeTime(twoHoursAgo.toISOString())).toBe('2h ago')
  })

  it('returns days ago', () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
    expect(formatRelativeTime(threeDaysAgo.toISOString())).toBe('3d ago')
  })

  it('returns weeks ago', () => {
    const twoWeeksAgo = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000)
    expect(formatRelativeTime(twoWeeksAgo.toISOString())).toBe('2w ago')
  })

  it('returns a formatted date for older times', () => {
    const yearAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
    const result = formatRelativeTime(yearAgo.toISOString())
    // Should be a localized date string with month and year
    expect(result).toMatch(/\d{4}/)
  })
})

describe('truncate', () => {
  it('returns string as-is when within length', () => {
    expect(truncate('hello', 10)).toBe('hello')
  })

  it('truncates and adds ellipsis when exceeding length', () => {
    const result = truncate('hello world this is long', 10)
    expect(result.length).toBeLessThanOrEqual(11)
    expect(result.endsWith('…')).toBe(true)
  })
})

describe('clamp', () => {
  it('returns value within range', () => {
    expect(clamp(5, 0, 10)).toBe(5)
  })

  it('returns min when value below min', () => {
    expect(clamp(-5, 0, 10)).toBe(0)
  })

  it('returns max when value above max', () => {
    expect(clamp(15, 0, 10)).toBe(10)
  })
})

describe('isAllowedImageType', () => {
  it('accepts jpeg, png, webp', () => {
    expect(isAllowedImageType('image/jpeg')).toBe(true)
    expect(isAllowedImageType('image/png')).toBe(true)
    expect(isAllowedImageType('image/webp')).toBe(true)
  })

  it('rejects gif, svg, avif', () => {
    expect(isAllowedImageType('image/gif')).toBe(false)
    expect(isAllowedImageType('image/svg+xml')).toBe(false)
    expect(isAllowedImageType('image/avif')).toBe(false)
  })
})
