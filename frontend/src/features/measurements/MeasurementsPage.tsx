import { lazy, Suspense, useRef, useState } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { formatKg, formatSignedKg } from '@/lib/format'
import { localToday } from './measurement-form'
import { MeasurementForm } from './MeasurementForm'
import { MeasurementHistory } from './MeasurementHistory'
import { useMeasurements } from './queries'

const WeightChart = lazy(() => import('./WeightChart').then((module) => ({ default: module.WeightChart })))

export function MeasurementsPage() {
  const measurements = useMeasurements()
  const formRef = useRef<HTMLDivElement>(null)
  // Opening a history entry remounts the form on that entry's date.
  const [formSeed, setFormSeed] = useState(() => ({ date: localToday(), version: 0 }))

  const weights = (measurements.data ?? []).flatMap((measurement) =>
    measurement.weight_kg === null
      ? []
      : [{ date: measurement.measured_on, weightKg: measurement.weight_kg }],
  )
  const first = weights.at(0)
  const last = weights.at(-1)

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="font-heading text-2xl font-semibold">Medidas</h1>
        <p className="text-muted-foreground text-sm">
          Pésate en condiciones parecidas (por ejemplo, en ayunas) para comparar mejor.
        </p>
      </header>

      {measurements.isPending && <p className="text-muted-foreground text-sm">Cargando medidas…</p>}
      {measurements.isError && (
        <Alert variant="destructive">
          <AlertDescription>No se pudieron cargar tus medidas.</AlertDescription>
        </Alert>
      )}

      {measurements.data && (
        <>
          <div ref={formRef} className="scroll-mt-4">
            <MeasurementForm
              key={`${formSeed.date}-${formSeed.version}`}
              measurements={measurements.data}
              initialDate={formSeed.date}
            />
          </div>

          {first && last && weights.length >= 2 && (
            <section className="space-y-2">
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="font-heading text-lg font-medium">Evolución del peso</h2>
                <span className="text-muted-foreground text-sm tabular-nums">
                  {formatKg(last.weightKg)} ·{' '}
                  {formatSignedKg(Math.round((last.weightKg - first.weightKg) * 100) / 100)} en total
                </span>
              </div>
              <Suspense fallback={<div className="bg-muted h-48 animate-pulse rounded-xl" />}>
                <WeightChart points={weights} />
              </Suspense>
            </section>
          )}

          <section className="space-y-3">
            <h2 className="font-heading text-lg font-medium">Historial</h2>
            {measurements.data.length === 0 ? (
              <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
                Aún no has registrado medidas. Empieza por tu peso de hoy.
              </p>
            ) : (
              <MeasurementHistory
                measurements={measurements.data}
                onSelect={(measurement) => {
                  setFormSeed(({ version }) => ({ date: measurement.measured_on, version: version + 1 }))
                  formRef.current?.scrollIntoView?.({ behavior: 'smooth' })
                }}
              />
            )}
          </section>
        </>
      )}
    </div>
  )
}
