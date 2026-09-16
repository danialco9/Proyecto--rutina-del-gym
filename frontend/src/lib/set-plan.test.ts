import { describe, expect, it } from 'vitest'
import { formatSetPlan } from './set-plan'

describe('formatSetPlan', () => {
  it('summarizes straight sets', () => {
    expect(
      formatSetPlan([
        { reps: 8, weightKg: 60 },
        { reps: 8, weightKg: 60 },
        { reps: 8, weightKg: 60 },
      ]),
    ).toBe('3 × 8 · 60 kg')
    expect(
      formatSetPlan([
        { reps: 12, weightKg: null },
        { reps: 12, weightKg: null },
      ]),
    ).toBe('2 × 12')
  })

  it('lists each set when they differ', () => {
    expect(
      formatSetPlan([
        { reps: 10, weightKg: 60 },
        { reps: 8, weightKg: 72.5 },
        { reps: 6, weightKg: null },
      ]),
    ).toBe('60×10 · 72,5×8 · –×6')
  })

  it('is empty without targets', () => {
    expect(formatSetPlan([])).toBeNull()
    expect(formatSetPlan([{ reps: null, weightKg: null }])).toBeNull()
  })
})
