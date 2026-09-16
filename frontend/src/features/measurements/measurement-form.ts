import { z } from 'zod'
import type { BodyMeasurement, BodyMeasurementIn } from '@/lib/types'

function optionalValue(label: string, min: number, max: number, exclusiveMin = true) {
  const number = z.number({ error: `${label}: introduce un número` })
  const bounded = exclusiveMin
    ? number.gt(min, `${label}: debe ser mayor que ${min}`)
    : number.min(min, `${label}: mínimo ${min}`)
  return bounded.max(max, `${label}: máximo ${max}`).nullable()
}

export const OPTIONAL_FIELDS = [
  { key: 'bodyFatPct', label: 'Grasa corporal (%)', shortLabel: 'Grasa', unit: '%', placeholder: '18' },
  { key: 'waistCm', label: 'Cintura (cm)', shortLabel: 'Cintura', unit: 'cm', placeholder: '82' },
  { key: 'chestCm', label: 'Pecho (cm)', shortLabel: 'Pecho', unit: 'cm', placeholder: '100' },
  { key: 'armCm', label: 'Brazo (cm)', shortLabel: 'Brazo', unit: 'cm', placeholder: '35' },
  { key: 'thighCm', label: 'Muslo (cm)', shortLabel: 'Muslo', unit: 'cm', placeholder: '58' },
] as const

// Limits mirror the API validation (BodyMeasurementIn in backend/src/gym_tracker/schemas.py).
export const measurementFormSchema = z
  .object({
    measuredOn: z.iso.date('Elige una fecha válida'),
    weightKg: optionalValue('Peso', 0, 500),
    bodyFatPct: optionalValue('Grasa', 0, 100, false),
    waistCm: optionalValue('Cintura', 0, 300),
    chestCm: optionalValue('Pecho', 0, 300),
    armCm: optionalValue('Brazo', 0, 300),
    thighCm: optionalValue('Muslo', 0, 300),
    notes: z.string().max(2000, 'Las notas son demasiado largas'),
  })
  .refine(
    (values) =>
      [values.weightKg, ...OPTIONAL_FIELDS.map(({ key }) => values[key])].some((value) => value !== null),
    { message: 'Introduce al menos una medida', path: ['weightKg'] },
  )

export type MeasurementFormValues = z.infer<typeof measurementFormSchema>

/** Today's date as `YYYY-MM-DD` in the device's time zone (not UTC). */
export function localToday(now = new Date()): string {
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

export function emptyMeasurementForm(measuredOn: string): MeasurementFormValues {
  return {
    measuredOn,
    weightKg: null,
    bodyFatPct: null,
    waistCm: null,
    chestCm: null,
    armCm: null,
    thighCm: null,
    notes: '',
  }
}

export function measurementToForm(measurement: BodyMeasurement): MeasurementFormValues {
  return {
    measuredOn: measurement.measured_on,
    weightKg: measurement.weight_kg,
    bodyFatPct: measurement.body_fat_pct,
    waistCm: measurement.waist_cm,
    chestCm: measurement.chest_cm,
    armCm: measurement.arm_cm,
    thighCm: measurement.thigh_cm,
    notes: measurement.notes ?? '',
  }
}

export function formToMeasurementPayload(values: MeasurementFormValues): BodyMeasurementIn {
  return {
    measured_on: values.measuredOn,
    weight_kg: values.weightKg,
    body_fat_pct: values.bodyFatPct,
    waist_cm: values.waistCm,
    chest_cm: values.chestCm,
    arm_cm: values.armCm,
    thigh_cm: values.thighCm,
    notes: values.notes.trim() || null,
  }
}

export const hasOptionalValues = (values: MeasurementFormValues) =>
  OPTIONAL_FIELDS.some(({ key }) => values[key] !== null)

/** Weight change against the previous entry that has a weight, rounded to avoid float noise. */
export function withWeightChanges(measurements: BodyMeasurement[]) {
  let previousWeight: number | null = null
  return measurements.map((measurement) => {
    const { weight_kg: weight } = measurement
    const change =
      weight !== null && previousWeight !== null ? Math.round((weight - previousWeight) * 100) / 100 : null
    previousWeight = weight ?? previousWeight
    return { measurement, change }
  })
}
