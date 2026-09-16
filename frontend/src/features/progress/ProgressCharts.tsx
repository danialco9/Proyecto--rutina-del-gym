import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatDay, formatDecimal, formatKg, formatShortDay } from '@/lib/format'
import type { ExerciseSession, ProgressOverview } from '@/lib/types'
import {
  muscleLabel,
  OTHER_MUSCLES,
  seriesColor,
  type VolumeRow,
  type VolumeSeriesKey,
} from './progress-data'

// Charts are loaded lazily with the progress page so Recharts stays out of the main bundle.

const AXIS_TICK = { fill: 'var(--muted-foreground)', fontSize: 12 }
const TOOLTIP_STYLE = {
  background: 'var(--popover)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  color: 'var(--popover-foreground)',
  fontSize: 13,
}
const CHART_MARGIN = { top: 8, right: 8, bottom: 0, left: -12 }

const volumeColor = (key: VolumeSeriesKey, index: number) =>
  key === OTHER_MUSCLES ? 'var(--chart-other)' : seriesColor(index)

interface LegendItem {
  label: string
  color: string
  shape?: 'line' | 'dot' | 'square'
}

/** Identity for multi-series charts: a coloured key beside text in the normal text colour. */
function ChartLegend({ items }: { items: LegendItem[] }) {
  return (
    <ul className="text-muted-foreground flex flex-wrap gap-x-4 gap-y-1 text-xs">
      {items.map(({ label, color, shape = 'square' }) => (
        <li key={label} className="flex items-center gap-1.5">
          <span
            aria-hidden
            className={
              shape === 'line'
                ? 'h-0.5 w-4 rounded-full'
                : shape === 'dot'
                  ? 'size-2 rounded-full'
                  : 'size-2.5 rounded-sm'
            }
            style={{ background: color }}
          />
          {label}
        </li>
      ))}
    </ul>
  )
}

const kgAxis = (value: number) => formatDecimal(Math.round(value))

export function ExerciseChart({ sessions }: { sessions: ExerciseSession[] }) {
  return (
    <div className="space-y-2">
      <div className="h-56 w-full">
        <ResponsiveContainer>
          <LineChart data={sessions} margin={CHART_MARGIN}>
            <CartesianGrid vertical={false} stroke="var(--border)" />
            <XAxis
              dataKey="performed_on"
              tickFormatter={formatShortDay}
              tickLine={false}
              axisLine={false}
              minTickGap={24}
              tick={AXIS_TICK}
            />
            <YAxis
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={kgAxis}
              tickLine={false}
              axisLine={false}
              width={48}
              tick={AXIS_TICK}
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelFormatter={(label) => formatDay(String(label))}
              formatter={(value, name) => [formatKg(Number(value)), name]}
            />
            <Line
              name="e1RM estimado"
              dataKey="best_e1rm_kg"
              stroke={seriesColor(0)}
              strokeWidth={2}
              dot={{ r: 4, fill: seriesColor(0), stroke: 'var(--background)', strokeWidth: 2 }}
              activeDot={{ r: 5 }}
            />
            <Line
              name="Peso máximo"
              dataKey="top_weight_kg"
              stroke={seriesColor(1)}
              strokeWidth={2}
              dot={{ r: 4, fill: seriesColor(1), stroke: 'var(--background)', strokeWidth: 2 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <ChartLegend
        items={[
          { label: 'e1RM estimado', color: seriesColor(0), shape: 'line' },
          { label: 'Peso máximo', color: seriesColor(1), shape: 'line' },
        ]}
      />
    </div>
  )
}

interface VolumeChartProps {
  rows: VolumeRow[]
  series: VolumeSeriesKey[]
}

export function VolumeChart({ rows, series }: VolumeChartProps) {
  return (
    <div className="space-y-2">
      <div className="h-56 w-full">
        <ResponsiveContainer>
          <BarChart data={rows} margin={CHART_MARGIN} barCategoryGap="30%">
            <CartesianGrid vertical={false} stroke="var(--border)" />
            <XAxis
              dataKey="week_start"
              tickFormatter={formatShortDay}
              tickLine={false}
              axisLine={false}
              tick={AXIS_TICK}
            />
            <YAxis allowDecimals={false} tickLine={false} axisLine={false} width={40} tick={AXIS_TICK} />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              cursor={{ fill: 'var(--muted)', opacity: 0.6 }}
              labelFormatter={(label) => `Semana del ${formatDay(String(label))}`}
              formatter={(value, name) => [`${String(value)} series`, name]}
            />
            {series.map((key, index) => (
              <Bar
                key={key}
                name={muscleLabel(key)}
                dataKey={key}
                stackId="sets"
                fill={volumeColor(key, index)}
                stroke="var(--background)"
                strokeWidth={2}
                maxBarSize={24}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ChartLegend
        items={series.map((key, index) => ({ label: muscleLabel(key), color: volumeColor(key, index) }))}
      />
    </div>
  )
}

export function BodyWeightChart({ entries }: { entries: ProgressOverview['body_weight']['entries'] }) {
  return (
    <div className="space-y-2">
      <div className="h-56 w-full">
        <ResponsiveContainer>
          <ComposedChart data={entries} margin={CHART_MARGIN}>
            <CartesianGrid vertical={false} stroke="var(--border)" />
            <XAxis
              dataKey="measured_on"
              tickFormatter={formatShortDay}
              tickLine={false}
              axisLine={false}
              minTickGap={24}
              tick={AXIS_TICK}
            />
            <YAxis
              domain={['dataMin - 1', 'dataMax + 1']}
              tickFormatter={kgAxis}
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
              width={48}
              tick={AXIS_TICK}
            />
            <Tooltip
              contentStyle={TOOLTIP_STYLE}
              labelFormatter={(label) => formatDay(String(label))}
              formatter={(value, name) => [formatKg(Number(value)), name]}
            />
            <Scatter name="Pesaje" dataKey="weight_kg" fill={seriesColor(0)} fillOpacity={0.45} />
            <Line
              name="Media 7 días"
              dataKey="trend_kg"
              stroke={seriesColor(0)}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <ChartLegend
        items={[
          { label: 'Pesaje', color: seriesColor(0), shape: 'dot' },
          { label: 'Media 7 días', color: seriesColor(0), shape: 'line' },
        ]}
      />
    </div>
  )
}
