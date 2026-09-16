import { ChevronRightIcon } from 'lucide-react'
import { formatDay, formatDecimal, formatKg, formatSignedKg } from '@/lib/format'
import type { BodyMeasurement } from '@/lib/types'
import { measurementToForm, OPTIONAL_FIELDS, withWeightChanges } from './measurement-form'

function extraSummary(measurement: BodyMeasurement): string {
  const values = measurementToForm(measurement)
  return OPTIONAL_FIELDS.flatMap(({ key, shortLabel, unit }) => {
    const value = values[key]
    return value === null ? [] : [`${shortLabel} ${formatDecimal(value)} ${unit}`]
  }).join(' · ')
}

interface MeasurementHistoryProps {
  /** Oldest first, as the API returns them. */
  measurements: BodyMeasurement[]
  onSelect: (measurement: BodyMeasurement) => void
}

export function MeasurementHistory({ measurements, onSelect }: MeasurementHistoryProps) {
  return (
    <ul className="space-y-2">
      {withWeightChanges(measurements)
        .toReversed()
        .map(({ measurement, change }) => {
          const extra = extraSummary(measurement)
          return (
            <li key={measurement.id}>
              <button
                type="button"
                className="bg-card hover:bg-muted flex w-full items-center justify-between gap-3 rounded-xl border p-3 text-left transition-colors"
                onClick={() => onSelect(measurement)}
              >
                <span className="min-w-0">
                  <span className="text-muted-foreground block text-sm">
                    {formatDay(measurement.measured_on)}
                  </span>
                  <span className="flex items-baseline gap-2">
                    <span className="font-medium tabular-nums">
                      {measurement.weight_kg === null ? 'Sin peso' : formatKg(measurement.weight_kg)}
                    </span>
                    {change !== null && (
                      <span className="text-muted-foreground text-sm tabular-nums">
                        {formatSignedKg(change)}
                      </span>
                    )}
                  </span>
                  {extra && <span className="text-muted-foreground block truncate text-xs">{extra}</span>}
                </span>
                <ChevronRightIcon className="text-muted-foreground size-5 shrink-0" aria-hidden />
              </button>
            </li>
          )
        })}
    </ul>
  )
}
