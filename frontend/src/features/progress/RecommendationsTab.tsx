import { ArrowDownIcon, ArrowUpIcon, RepeatIcon, TrendingUpIcon, type LucideIcon } from 'lucide-react'
import { formatDay } from '@/lib/format'
import { formatSetPlan } from '@/lib/set-plan'
import type { ProgressionAction, Recommendation } from '@/lib/types'
import { EmptyState } from './ProgressParts'
import { ACTION_TEXT, groupRecommendations } from './progress-data'

const ACTION_ICONS: Record<ProgressionAction, LucideIcon> = {
  increase_load: ArrowUpIcon,
  increase_reps: TrendingUpIcon,
  hold: RepeatIcon,
  deload: ArrowDownIcon,
}

const toPlan = (sets: { reps: number | null; weight_kg: number | null }[]) =>
  sets.map((set) => ({ reps: set.reps, weightKg: set.weight_kg }))

function RecommendationRow({ item }: { item: Recommendation }) {
  const target = formatSetPlan(toPlan(item.target_sets))
  return (
    <li className="space-y-0.5 py-2.5">
      <p className="font-medium">{item.exercise_name}</p>
      <p className="text-muted-foreground text-xs tabular-nums">
        {formatDay(item.last_performed_on)}: {formatSetPlan(toPlan(item.last_sets))}
        {target && ` · objetivo ${target}`}
      </p>
      <p className="text-sm tabular-nums">
        <span className="text-muted-foreground">Próxima: </span>
        <span className="font-semibold">{formatSetPlan(toPlan(item.suggested_sets))}</span>
      </p>
    </li>
  )
}

export function RecommendationsTab({ recommendations }: { recommendations: Recommendation[] }) {
  if (recommendations.length === 0) {
    return (
      <EmptyState>Registra tu primer entreno para recibir recomendaciones para la próxima sesión.</EmptyState>
    )
  }
  return (
    <div className="space-y-4">
      <p className="text-muted-foreground text-sm">
        Según tu última sesión de cada ejercicio, su objetivo de repeticiones en la rutina y el RPE.
      </p>
      {groupRecommendations(recommendations).map(({ action, items }) => {
        const Icon = ACTION_ICONS[action]
        return (
          <section key={action} className="bg-card rounded-xl border px-4 pt-3 pb-1">
            <h2 className="flex items-center gap-2 font-medium">
              <Icon className="text-primary size-4" aria-hidden />
              {ACTION_TEXT[action].title}
              <span className="text-muted-foreground text-sm font-normal">({items.length})</span>
            </h2>
            <p className="text-muted-foreground text-xs">{ACTION_TEXT[action].hint}</p>
            <ul className="divide-y">
              {items.map((item) => (
                <RecommendationRow key={item.exercise_id} item={item} />
              ))}
            </ul>
          </section>
        )
      })}
    </div>
  )
}
