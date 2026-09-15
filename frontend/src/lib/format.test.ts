import { describe, expect, it } from 'vitest'
import { formatDuration, formatKg, formatSeconds, plural } from './format'

describe('format', () => {
  it('formats weights with the Spanish decimal separator', () => {
    expect(formatKg(52.5)).toBe('52,5 kg')
    expect(formatKg(110)).toBe('110 kg')
  })

  it('formats rest countdowns', () => {
    expect(formatSeconds(90)).toBe('1:30')
    expect(formatSeconds(5)).toBe('0:05')
  })

  it('formats workout durations', () => {
    expect(formatDuration('2026-09-15T16:00:00Z', '2026-09-15T16:45:00Z')).toBe('45 min')
    expect(formatDuration('2026-09-15T16:00:00Z', '2026-09-15T17:10:00Z')).toBe('1 h 10 min')
    expect(formatDuration('2026-09-15T16:00:00Z', null)).toBeNull()
  })

  it('picks singular or plural nouns', () => {
    expect(plural(1, 'serie', 'series')).toBe('serie')
    expect(plural(3, 'serie', 'series')).toBe('series')
  })
})
