import { WifiOffIcon } from 'lucide-react'
import { useOnline } from '@/lib/online'

/**
 * Installed on a phone, the app opens with no connection at all, so it has to say so: a workout can
 * go on being written down, but anything that talks to the server has to wait.
 */
export function OfflineNotice() {
  const online = useOnline()
  if (online) return null

  return (
    <p
      role="status"
      className="bg-muted text-muted-foreground flex items-center justify-center gap-2 px-4 py-2 text-center text-xs"
    >
      <WifiOffIcon className="size-4 shrink-0" aria-hidden />
      Sin conexión. Lo que apuntes se queda en el móvil; podrás guardarlo cuando vuelva la cobertura.
    </p>
  )
}
