import { describe, expect, it } from 'vitest'
import {
  formatDay,
  formatDuration,
  formatKg,
  formatSeconds,
  formatShortDay,
  formatSignedKg,
  plural,
} from './format'

describe('format', () => {
  it('formats weights with the Spanish decimal separator', () => {
    expect(formatKg(52.5)).toBe('52,5 kg')
    expect(formatKg(110)).toBe('110 kg')
  })

  it('formats signed weight changes', () => {
    expect(formatSignedKg(-0.3)).toBe('-0,3 kg')
    expect(formatSignedKg(1.25)).toBe('+1,25 kg')
    expect(formatSignedKg(0)).toBe('0 kg')
  })

  it('formats calendar dates without shifting the day', () => {
    expect(formatShortDay('2026-09-01')).toBe('1/9')
    expect(formatDay('2026-09-16')).toMatch(/16/)
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
