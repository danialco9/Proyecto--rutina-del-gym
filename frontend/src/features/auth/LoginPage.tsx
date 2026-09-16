import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Navigate, useLocation, useNavigate } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ApiError } from '@/lib/api'
import { useCurrentUser, useLogin } from './queries'
import { loginSchema, type LoginInput } from './schema'

/** Only same-app paths are accepted, so the redirect cannot send the user to another site. */
function redirectTarget(state: unknown): string {
  if (typeof state === 'object' && state !== null && 'from' in state && typeof state.from === 'string') {
    const { from } = state
    if (from.startsWith('/') && !from.startsWith('//')) {
      return from
    }
  }
  return '/'
}

function loginErrorMessage(error: Error | null): string | null {
  if (error === null) {
    return null
  }
  return error instanceof ApiError && error.status === 401
    ? 'Email o contraseña incorrectos'
    : 'No se pudo conectar con el servidor. Inténtalo de nuevo.'
}

export function LoginPage() {
  const currentUser = useCurrentUser()
  const login = useLogin()
  const navigate = useNavigate()
  const location = useLocation()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({ resolver: zodResolver(loginSchema), defaultValues: { email: '', password: '' } })

  const target = redirectTarget(location.state)
  if (currentUser.data) {
    return <Navigate to={target} replace />
  }

  const onSubmit = handleSubmit(async (credentials) => {
    try {
      await login.mutateAsync(credentials)
      navigate(target, { replace: true })
    } catch {
      // The error is rendered from the mutation state.
    }
  })
  const errorMessage = loginErrorMessage(login.error)

  return (
    <main className="flex min-h-dvh items-center justify-center px-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <p className="text-primary text-sm font-semibold tracking-wide uppercase">Gym Tracker</p>
          <h1 className="font-heading text-xl font-semibold">Inicia sesión</h1>
          <CardDescription>Registra tus entrenos y sigue tu progreso.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={onSubmit} noValidate>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                className="h-11"
                aria-invalid={errors.email ? true : undefined}
                aria-describedby={errors.email ? 'email-error' : undefined}
                {...register('email')}
              />
              {errors.email && (
                <p id="email-error" className="text-destructive text-sm">
                  {errors.email.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                className="h-11"
                aria-invalid={errors.password ? true : undefined}
                aria-describedby={errors.password ? 'password-error' : undefined}
                {...register('password')}
              />
              {errors.password && (
                <p id="password-error" className="text-destructive text-sm">
                  {errors.password.message}
                </p>
              )}
            </div>
            {errorMessage && (
              <Alert variant="destructive">
                <AlertDescription>{errorMessage}</AlertDescription>
              </Alert>
            )}
            <Button type="submit" size="lg" className="h-11 w-full text-base" disabled={login.isPending}>
              {login.isPending ? 'Entrando…' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
