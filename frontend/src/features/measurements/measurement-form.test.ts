import { describe, expect, it } from 'vitest'
import type { BodyMeasurement } from '@/lib/types'
import {
  emptyMeasurementForm,
  formToMeasurementPayload,
  localToday,
  measurementFormSchema,
  measurementToForm,
  withWeightChanges,
} from './measurement-form'

function measurement(overrides: Partial<BodyMeasurement> = {}): BodyMeasurement {
  return {
    id: 1,
    measured_on: '2026-09-14',
    weight_kg: 78.7,
    body_fat_pct: null,
    waist_cm: null,
    chest_cm: null,
    arm_cm: null,
    thigh_cm: null,
    notes: null,
    ...overrides,
  }
}

describe('measurement form', () => {
  it("uses the device's local date for today", () => {
    expect(localToday(new Date(2026, 0, 5, 23, 30))).toBe('2026-01-05')
  })

  it('round-trips a measurement through the form values', () => {
    const entry = measurement({ waist_cm: 82.5, notes: 'En ayunas' })
    expect(formToMeasurementPayload(measurementToForm(entry))).toEqual({
      measured_on: '2026-09-14',
      weight_kg: 78.7,
      body_fat_pct: null,
      waist_cm: 82.5,
      chest_cm: null,
      arm_cm: null,
      thigh_cm: null,
      notes: 'En ayunas',
    })
  })

  it('requires at least one measurement and valid ranges', () => {
    const empty = measurementFormSchema.safeParse(emptyMeasurementForm('2026-09-16'))
    expect(empty.error?.issues.map((issue) => issue.message)).toEqual(['Introduce al menos una medida'])

    const outOfRange = measurementFormSchema.safeParse({
      ...emptyMeasurementForm('2026-09-16'),
      weightKg: 0,
      bodyFatPct: 120,
    })
    expect(outOfRange.error?.issues.map((issue) => issue.message)).toEqual([
      'Peso: debe ser mayor que 0',
      'Grasa: máximo 100',
    ])
  })

  it('computes weight changes against the previous weighed entry', () => {
    const rows = withWeightChanges([
      measurement({ id: 1, measured_on: '2026-09-12', weight_kg: 79.1 }),
      measurement({ id: 2, measured_on: '2026-09-13', weight_kg: null, waist_cm: 83 }),
      measurement({ id: 3, measured_on: '2026-09-14', weight_kg: 78.7 }),
    ])
    expect(rows.map((row) => row.change)).toEqual([null, null, -0.4])
  })
})
