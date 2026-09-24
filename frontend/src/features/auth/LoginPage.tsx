import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ApiError } from '@/lib/api'
import { AuthShell, FormField } from './AuthForm'
import { tooManyAttemptsMessage } from './errors'
import { useCurrentUser, useDemoLogin, useLogin } from './queries'
import { redirectTarget } from './redirect'
import { loginSchema, type LoginInput } from './schema'

function loginErrorMessage(error: Error | null): string | null {
  if (error === null) {
    return null
  }
  if (error instanceof ApiError && error.status === 401) {
    return 'Email o contraseña incorrectos'
  }
  return tooManyAttemptsMessage(error) ?? 'No se pudo conectar con el servidor. Inténtalo de nuevo.'
}

// Set VITE_DEMO_ENABLED=true at build time where the API has the public demo account.
const DEMO_ENABLED = import.meta.env.VITE_DEMO_ENABLED === 'true'

function demoErrorMessage(error: Error | null): string | null {
  if (error === null) {
    return null
  }
  if (error instanceof ApiError && error.status === 404) {
    return 'La demo no está disponible ahora mismo.'
  }
  return tooManyAttemptsMessage(error) ?? 'No se pudo abrir la demo. Inténtalo de nuevo.'
}

export function LoginPage() {
  const currentUser = useCurrentUser()
  const login = useLogin()
  const demoLogin = useDemoLogin()
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
  const errorMessage = loginErrorMessage(login.error) ?? demoErrorMessage(demoLogin.error)

  const openDemo = async () => {
    login.reset()
    try {
      await demoLogin.mutateAsync()
      navigate(target, { replace: true })
    } catch {
      // The error is rendered from the mutation state.
    }
  }

  return (
    <AuthShell
      title="Inicia sesión"
      description="Registra tus entrenos y sigue tu progreso."
      footer={
        <>
          ¿No tienes cuenta?
          <Link
            to="/registro"
            state={location.state}
            className="text-primary font-medium underline-offset-4 hover:underline"
          >
            Crear cuenta
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={onSubmit} noValidate>
        <FormField
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
        />
        <FormField
          id="password"
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register('password')}
        />
        <p className="-mt-2 text-right text-sm">
          <Link
            to="/recuperar"
            className="text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
          >
            ¿Olvidaste tu contraseña?
          </Link>
        </p>
        {errorMessage && (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}
        <Button type="submit" size="lg" className="h-11 w-full text-base" disabled={login.isPending}>
          {login.isPending ? 'Entrando…' : 'Entrar'}
        </Button>
        {DEMO_ENABLED && (
          <div className="space-y-2">
            <p className="text-muted-foreground text-center text-xs">
              ¿Solo quieres echar un vistazo? La demo tiene 12 semanas de entrenos de ejemplo y se restablece
              cada noche.
            </p>
            <Button
              type="button"
              variant="outline"
              size="lg"
              className="h-11 w-full text-base"
              disabled={demoLogin.isPending}
              onClick={openDemo}
            >
              {demoLogin.isPending ? 'Abriendo la demo…' : 'Probar la demo'}
            </Button>
          </div>
        )}
      </form>
    </AuthShell>
  )
}
