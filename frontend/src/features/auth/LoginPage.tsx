import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ApiError } from '@/lib/api'
import { AuthShell, FormField } from './AuthForm'
import { tooManyAttemptsMessage } from './errors'
import { useCurrentUser, useLogin } from './queries'
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
        {errorMessage && (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}
        <Button type="submit" size="lg" className="h-11 w-full text-base" disabled={login.isPending}>
          {login.isPending ? 'Entrando…' : 'Entrar'}
        </Button>
      </form>
    </AuthShell>
  )
}
