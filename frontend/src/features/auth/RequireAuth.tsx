import { Navigate, Outlet, useLocation } from 'react-router'
import { useCurrentUser } from './queries'

function FullPageMessage({ children }: { children: string }) {
  return (
    <main className="text-muted-foreground flex min-h-dvh items-center justify-center px-4 text-center">
      <p>{children}</p>
    </main>
  )
}

/** Renders the child routes only for a signed-in user; otherwise redirects to the login page. */
export function RequireAuth() {
  const currentUser = useCurrentUser()
  const location = useLocation()

  if (currentUser.isPending) {
    return <FullPageMessage>Cargando…</FullPageMessage>
  }
  if (currentUser.isError) {
    return (
      <FullPageMessage>No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.</FullPageMessage>
    )
  }
  if (currentUser.data === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
