import { formatDecimal } from './format'

export interface SetPlanItem {
  reps: number | null
  weightKg: number | null
}

const formatWeight = (weightKg: number | null) => (weightKg === null ? '–' : formatDecimal(weightKg))

/**
 * Short text for a list of sets: "3 × 8 · 60 kg" when every set is the same, otherwise one
 * "weight×reps" per set ("60×10 · 70×8 · 80×6"). Returns null when nothing is planned.
 */
export function formatSetPlan(sets: SetPlanItem[]): string | null {
  const first = sets[0]
  if (first === undefined || sets.every((set) => set.reps === null && set.weightKg === null)) {
    return null
  }
  const uniform = sets.every((set) => set.reps === first.reps && set.weightKg === first.weightKg)
  if (uniform) {
    const scheme = `${sets.length} × ${first.reps ?? '–'}`
    return first.weightKg === null ? scheme : `${scheme} · ${formatDecimal(first.weightKg)} kg`
  }
  return sets.map((set) => `${formatWeight(set.weightKg)}×${set.reps ?? '–'}`).join(' · ')
}
