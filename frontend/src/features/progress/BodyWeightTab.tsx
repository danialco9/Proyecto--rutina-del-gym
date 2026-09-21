import { lazy, Suspense } from 'react'
import { Link } from 'react-router'
import { formatDay, formatDecimal, formatKg, formatShortDay, formatSignedKg } from '@/lib/format'
import type { ProgressOverview } from '@/lib/types'
import { ChartFallback, DataTable, EmptyState, StatTile } from './ProgressParts'

const BodyWeightChart = lazy(() =>
  import('./ProgressCharts').then((module) => ({ default: module.BodyWeightChart })),
)

export function BodyWeightTab({ bodyWeight }: { bodyWeight: ProgressOverview['body_weight'] }) {
  const { entries, weekly_change_kg: weeklyChange } = bodyWeight
  const latest = entries.at(-1)

  if (latest === undefined) {
    return (
      <EmptyState>
        Registra tu peso en{' '}
        <Link to="/medidas" className="text-primary underline-offset-4 hover:underline">
          Medidas
        </Link>{' '}
        para ver su tendencia.
      </EmptyState>
    )
  }
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        <StatTile
          label="Último pesaje"
          value={formatKg(latest.weight_kg)}
          detail={formatDay(latest.measured_on)}
        />
        <StatTile label="Media 7 días" value={formatKg(latest.trend_kg)} />
        <StatTile
          className="col-span-2 sm:col-span-1"
          label="Tendencia"
          value={weeklyChange === null ? '—' : formatSignedKg(weeklyChange)}
          detail="por semana (4 sem.)"
        />
      </div>

      <section className="space-y-2">
        <div className="space-y-1">
          <h2 className="font-heading text-lg font-medium">Peso corporal</h2>
          <p className="text-muted-foreground text-sm">
            La media de 7 días suaviza las variaciones diarias (agua, comidas) y muestra la tendencia real.
          </p>
        </div>
        {entries.length < 2 ? (
          <EmptyState>Con dos pesajes verás la gráfica.</EmptyState>
        ) : (
          <Suspense fallback={<ChartFallback />}>
            <BodyWeightChart entries={entries} />
          </Suspense>
        )}
        <DataTable
          caption="Pesajes y media de 7 días"
          headers={['Fecha', 'Peso', 'Media 7 días']}
          rows={entries
            .toReversed()
            .map((entry) => [
              formatShortDay(entry.measured_on),
              formatDecimal(entry.weight_kg),
              formatDecimal(entry.trend_kg),
            ])}
        />
      </section>
    </div>
  )
}
