import { ClipboardListIcon, DumbbellIcon, HouseIcon, LogOutIcon, ScaleIcon } from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { Button } from '@/components/ui/button'
import { useLogout } from '@/features/auth/queries'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/', label: 'Inicio', icon: HouseIcon, end: true },
  { to: '/entrenar', label: 'Entrenar', icon: DumbbellIcon, end: false },
  { to: '/rutinas', label: 'Rutinas', icon: ClipboardListIcon, end: false },
  { to: '/medidas', label: 'Medidas', icon: ScaleIcon, end: false },
] as const

export function AppLayout() {
  const logout = useLogout()
  const navigate = useNavigate()

  const signOut = () => logout.mutate(undefined, { onSuccess: () => navigate('/login', { replace: true }) })

  return (
    <div className="mx-auto flex min-h-dvh max-w-2xl flex-col">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <span className="font-heading font-semibold">
          Gym <span className="text-primary">Tracker</span>
        </span>
        <Button variant="ghost" size="sm" onClick={signOut} disabled={logout.isPending}>
          <LogOutIcon />
          Salir
        </Button>
      </header>

      <main className="flex-1 px-4 pt-4 pb-40">
        <Outlet />
      </main>

      <nav
        aria-label="Principal"
        className="bg-background/95 fixed inset-x-0 bottom-0 z-30 border-t pb-[env(safe-area-inset-bottom)] backdrop-blur"
      >
        <ul className="mx-auto grid max-w-2xl grid-cols-4">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    'text-muted-foreground flex h-14 flex-col items-center justify-center gap-1 text-xs',
                    isActive && 'text-primary font-medium',
                  )
                }
              >
                <Icon className="size-5" aria-hidden />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}
