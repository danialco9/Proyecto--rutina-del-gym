import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface StatTileProps {
  label: string
  value: string
  detail?: string
  className?: string
}

/** Label and figure wrap rather than truncate: on a phone the tile is barely wider than the text. */
export function StatTile({ label, value, detail, className }: StatTileProps) {
  return (
    <div className={cn('bg-card ring-foreground/10 min-w-0 rounded-xl p-3 ring-1 sm:p-4', className)}>
      <p className="eyebrow">{label}</p>
      <p className="stat-number mt-2 text-xl sm:mt-2.5 sm:text-2xl">{value}</p>
      {detail && <p className="text-muted-foreground mt-1 text-xs">{detail}</p>}
    </div>
  )
}

export function ChartFallback() {
  return <div className="bg-muted h-56 animate-pulse rounded-xl" />
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
      {children}
    </p>
  )
}

interface DataTableProps {
  caption: string
  headers: string[]
  rows: (string | number)[][]
}

/** The numbers behind a chart, collapsed by default, so nothing depends on reading colours or shapes. */
export function DataTable({ caption, headers, rows }: DataTableProps) {
  return (
    <details className="text-sm">
      <summary className="text-muted-foreground hover:text-foreground cursor-pointer select-none">
        Ver datos
      </summary>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full text-left tabular-nums">
          <caption className="sr-only">{caption}</caption>
          <thead className="text-muted-foreground text-xs">
            <tr>
              {headers.map((header) => (
                <th key={header} scope="col" className="py-1 pr-3 font-medium">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={String(row[0])} className="border-t">
                {row.map((cell, index) => (
                  <td key={headers[index]} className="py-1 pr-3">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}
