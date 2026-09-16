import { ArrowDownIcon, ArrowUpIcon, RepeatIcon, TrendingUpIcon, type LucideIcon } from 'lucide-react'
import { formatDay, formatKg } from '@/lib/format'
import type { ProgressionAction, Recommendation } from '@/lib/types'
import { EmptyState } from './ProgressParts'
import { ACTION_TEXT, groupRecommendations } from './progress-data'

const ACTION_ICONS: Record<ProgressionAction, LucideIcon> = {
  increase_load: ArrowUpIcon,
  increase_reps: TrendingUpIcon,
  hold: RepeatIcon,
  deload: ArrowDownIcon,
}

function RecommendationRow({ item }: { item: Recommendation }) {
  const changes = item.suggested_weight_kg !== item.last_weight_kg
  return (
    <li className="flex items-center justify-between gap-3 py-2.5">
      <div className="min-w-0">
        <p className="truncate font-medium">{item.exercise_name}</p>
        <p className="text-muted-foreground text-xs">
          {formatDay(item.last_performed_on)}: {formatKg(item.last_weight_kg)} × {item.last_reps.join('/')}
          {item.target_reps !== null && ` · objetivo ${item.target_reps}`}
        </p>
      </div>
      <p className="shrink-0 text-right tabular-nums">
        {changes && <span className="text-muted-foreground text-sm">{formatKg(item.last_weight_kg)} → </span>}
        <span className="font-semibold">{formatKg(item.suggested_weight_kg)}</span>
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
