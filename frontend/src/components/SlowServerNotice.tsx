import { useIsFetching, useIsMutating } from '@tanstack/react-query'
import { LoaderCircleIcon } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useOnline } from '@/lib/online'

/** How long a request may take before it is worth explaining the wait. */
export const SLOW_REQUEST_MS = 5000

/**
 * The API runs on a free plan that sleeps when nobody uses it, and waking it takes up to a minute.
 * Without a word, that minute of "Entrando…" looks like a broken app, so any request that is still
 * on its way after a few seconds says what is going on. Offline, `OfflineNotice` speaks instead.
 */
export function SlowServerNotice() {
  const busy = useIsFetching() + useIsMutating() > 0
  const online = useOnline()
  const [slow, setSlow] = useState(false)

  useEffect(() => {
    if (!busy) return
    const timer = window.setTimeout(() => setSlow(true), SLOW_REQUEST_MS)
    return () => {
      window.clearTimeout(timer)
      setSlow(false)
    }
  }, [busy])

  if (!busy || !slow || !online) return null

  return (
    <p
      role="status"
      className="bg-primary text-primary-foreground fixed inset-x-0 top-0 z-50 flex items-center justify-center gap-2 px-4 py-2 text-center text-xs font-medium"
    >
      <LoaderCircleIcon className="size-4 shrink-0 animate-spin" aria-hidden />
      Arrancando el servidor… puede tardar hasta un minuto.
    </p>
  )
}
