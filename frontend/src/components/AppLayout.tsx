import {
  ChartLineIcon,
  ClipboardListIcon,
  DumbbellIcon,
  HouseIcon,
  LogOutIcon,
  ScaleIcon,
} from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { OfflineNotice } from '@/components/OfflineNotice'
import { Button } from '@/components/ui/button'
import { useLogout } from '@/features/auth/queries'
import { loadDraft, saveDraft } from '@/features/workout/draft'
import { clearOutbox } from '@/features/workout/outbox'
import { useOutbox, useOutboxSync } from '@/features/workout/useOutbox'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/', label: 'Inicio', icon: HouseIcon, end: true },
  { to: '/entrenar', label: 'Entrenar', icon: DumbbellIcon, end: false },
  { to: '/rutinas', label: 'Rutinas', icon: ClipboardListIcon, end: false },
  { to: '/medidas', label: 'Medidas', icon: ScaleIcon, end: false },
  { to: '/progreso', label: 'Progreso', icon: ChartLineIcon, end: false },
] as const

function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn('font-heading font-semibold tracking-tight', className)}>
      Gym <span className="text-primary">Tracker</span>
    </span>
  )
}

export function AppLayout() {
  const logout = useLogout()
  const navigate = useNavigate()
  const queued = useOutbox()
  useOutboxSync()

  const signOut = () => {
    // Nothing unsent may be left on the device for the next account that signs in.
    const warning =
      loadDraft() !== null
        ? 'Tienes un entreno sin guardar. Si cierras sesión se descartará. ¿Cerrar sesión?'
        : queued.length > 0
          ? 'Tienes entrenos sin subir que están solo en este móvil. Si cierras sesión se perderán. ¿Cerrar sesión?'
          : null
    if (warning !== null && !window.confirm(warning)) {
      return
    }
    const userId = queued[0]?.userId
    logout.mutate(undefined, {
      onSuccess: () => {
        saveDraft(null)
        if (userId !== undefined) clearOutbox(userId)
        navigate('/login', { replace: true })
      },
    })
  }

  return (
    <div className="min-h-dvh lg:flex">
      {/* One navigation landmark in the DOM: a fixed bottom bar on phones, a sidebar from lg up. */}
      <aside
        className={cn(
          'bg-background/95 fixed inset-x-0 bottom-0 z-30 border-t pb-[env(safe-area-inset-bottom)] backdrop-blur',
          'lg:bg-sidebar lg:sticky lg:inset-x-auto lg:top-0 lg:flex lg:h-dvh lg:w-64 lg:shrink-0 lg:flex-col lg:border-t-0 lg:border-r lg:p-4 lg:backdrop-blur-none',
        )}
      >
        <Wordmark className="hidden px-3 py-2 text-lg lg:block" />
        <nav aria-label="Principal" className="lg:mt-6 lg:flex-1">
          <ul className="mx-auto grid max-w-2xl grid-cols-5 lg:mx-0 lg:max-w-none lg:grid-cols-1 lg:gap-1">
            {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    cn(
                      'text-muted-foreground flex h-14 flex-col items-center justify-center gap-1 text-xs transition-colors',
                      'lg:hover:bg-sidebar-accent lg:hover:text-foreground lg:h-auto lg:flex-row lg:justify-start lg:gap-3 lg:rounded-lg lg:px-3 lg:py-2.5 lg:text-sm lg:font-medium',
                      isActive && 'text-primary lg:bg-sidebar-accent font-medium',
                    )
                  }
                >
                  <Icon className="size-5 shrink-0" aria-hidden />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* One sign-out control on every size: the sidebar already carries the wordmark from lg up. */}
        <header className="flex items-center justify-between border-b px-4 py-3 lg:justify-end lg:px-8">
          <Wordmark className="lg:hidden" />
          <Button variant="ghost" size="sm" onClick={signOut} disabled={logout.isPending}>
            <LogOutIcon />
            Salir
          </Button>
        </header>

        <OfflineNotice />

        <main className="mx-auto w-full max-w-2xl flex-1 px-4 pt-4 pb-40 lg:max-w-6xl lg:px-8 lg:pt-8 lg:pb-16">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
