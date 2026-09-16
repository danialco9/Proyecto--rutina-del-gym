import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatDay, formatDecimal, formatKg, formatShortDay } from '@/lib/format'

export interface WeightPoint {
  date: string
  weightKg: number
}

const AXIS_TICK = { fill: 'var(--muted-foreground)', fontSize: 12 }

interface WeightChartProps {
  points: WeightPoint[]
}

/** Body weight over time. Loaded lazily so the charting library stays out of the main bundle. */
export function WeightChart({ points }: WeightChartProps) {
  return (
    <div className="h-48 w-full">
      <ResponsiveContainer>
        <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis
            dataKey="date"
            tickFormatter={formatShortDay}
            tickLine={false}
            axisLine={false}
            minTickGap={24}
            tick={AXIS_TICK}
          />
          <YAxis
            dataKey="weightKg"
            domain={['dataMin - 1', 'dataMax + 1']}
            allowDecimals={false}
            tickFormatter={(value: number) => formatDecimal(Math.round(value))}
            tickLine={false}
            axisLine={false}
            width={48}
            tick={AXIS_TICK}
          />
          <Tooltip
            formatter={(value) => [formatKg(Number(value)), 'Peso']}
            labelFormatter={(label) => formatDay(String(label))}
            contentStyle={{
              background: 'var(--popover)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--popover-foreground)',
            }}
          />
          <Line
            type="monotone"
            dataKey="weightKg"
            stroke="var(--primary)"
            strokeWidth={2}
            dot={points.length <= 30 ? { r: 3, fill: 'var(--primary)' } : false}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
