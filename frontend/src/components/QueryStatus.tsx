import type { UseQueryResult } from '@tanstack/react-query'
import { WifiOffIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useOnline } from '@/lib/online'
import { cn } from '@/lib/utils'

interface QueryStatusProps {
  query: Pick<UseQueryResult, 'isPending' | 'isError' | 'fetchStatus'>
  /** Shown while the first answer is on its way. */
  loading: ReactNode
  /** Shown when the server answered with an error. */
  error: string
  className?: string
}

/**
 * What a screen shows before its data is there. Without a connection a query can get stuck in more
 * than one way: started after the connection dropped, it is paused and would say "Cargando…"
 * forever; in an app opened with no connection at all, it keeps retrying and then fails like a
 * server error would. All of it is the same thing to someone in a gym basement, so all of it says
 * so, and the screen fills in when the connection returns.
 */
export function QueryStatus({ query, loading, error, className }: QueryStatusProps) {
  const online = useOnline()
  const waitingForConnection =
    (query.isPending && query.fetchStatus === 'paused') || ((query.isPending || query.isError) && !online)

  if (waitingForConnection) {
    return (
      <p role="status" className={cn('text-muted-foreground flex items-center gap-2 text-sm', className)}>
        <WifiOffIcon className="size-4 shrink-0" aria-hidden />
        Sin conexión. Se cargará cuando vuelva la cobertura.
      </p>
    )
  }
  if (query.isError) {
    return (
      <Alert variant="destructive" className={className}>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }
  if (query.isPending) {
    return typeof loading === 'string' ? (
      <p className={cn('text-muted-foreground text-sm', className)}>{loading}</p>
    ) : (
      loading
    )
  }
  return null
}
