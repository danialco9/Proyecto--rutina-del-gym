import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ApiError } from '@/lib/api'
import { AuthShell, FormField } from './AuthForm'
import { tooManyAttemptsMessage } from './errors'
import { useCurrentUser, useRegister } from './queries'
import { redirectTarget } from './redirect'
import { registerSchema, type RegisterInput } from './schema'

function registerErrorMessage(error: Error | null): string | null {
  if (error === null) {
    return null
  }
  if (error instanceof ApiError && error.status === 409) {
    return 'Ya existe una cuenta con ese email'
  }
  return tooManyAttemptsMessage(error) ?? 'No se pudo crear la cuenta. Inténtalo de nuevo.'
}

export function RegisterPage() {
  const currentUser = useCurrentUser()
  const registerAccount = useRegister()
  const navigate = useNavigate()
  const location = useLocation()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  })

  const target = redirectTarget(location.state)
  if (currentUser.data) {
    return <Navigate to={target} replace />
  }

  const onSubmit = handleSubmit(async ({ email, password }) => {
    try {
      await registerAccount.mutateAsync({ email, password })
      navigate(target, { replace: true })
    } catch {
      // The error is rendered from the mutation state.
    }
  })
  const errorMessage = registerErrorMessage(registerAccount.error)

  return (
    <AuthShell
      title="Crea tu cuenta"
      description="Empieza a registrar tus entrenos en un minuto."
      footer={
        <>
          ¿Ya tienes cuenta?
          <Link
            to="/login"
            state={location.state}
            className="text-primary font-medium underline-offset-4 hover:underline"
          >
            Inicia sesión
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
          autoComplete="new-password"
          error={errors.password?.message}
          {...register('password')}
        />
        <FormField
          id="confirm-password"
          label="Repite la contraseña"
          type="password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        {errorMessage && (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}
        <Button
          type="submit"
          size="lg"
          className="h-11 w-full text-base"
          disabled={registerAccount.isPending}
        >
          {registerAccount.isPending ? 'Creando cuenta…' : 'Crear cuenta'}
        </Button>
      </form>
    </AuthShell>
  )
}
