import { zodResolver } from '@hookform/resolvers/zod'
import { MailCheckIcon } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AuthShell, FormField } from './AuthForm'
import { tooManyAttemptsMessage } from './errors'
import { useRequestPasswordReset } from './queries'
import { forgotPasswordSchema, type ForgotPasswordInput } from './schema'

const backToLogin = (
  <Link to="/login" className="text-primary font-medium underline-offset-4 hover:underline">
    Volver a iniciar sesión
  </Link>
)

export function ForgotPasswordPage() {
  const requestReset = useRequestPasswordReset()
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors },
  } = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  })

  const onSubmit = handleSubmit(({ email }) => requestReset.mutate(email))

  if (requestReset.isSuccess) {
    return (
      <AuthShell title="Revisa tu correo" description="Te hemos enviado un enlace." footer={backToLogin}>
        <div className="space-y-3 text-sm" role="status">
          <MailCheckIcon className="text-primary size-8" aria-hidden />
          <p>
            Si hay una cuenta con <strong>{getValues('email')}</strong>, te llegará un email con un enlace
            para elegir una contraseña nueva. Caduca en 30 minutos.
          </p>
          <p className="text-muted-foreground">¿No lo ves? Mira en la carpeta de spam o correo no deseado.</p>
        </div>
      </AuthShell>
    )
  }

  const errorMessage =
    requestReset.error === null
      ? null
      : (tooManyAttemptsMessage(requestReset.error) ??
        'No se pudo conectar con el servidor. Inténtalo de nuevo.')

  return (
    <AuthShell
      title="¿Olvidaste tu contraseña?"
      description="Escribe tu email y te mandamos un enlace para elegir una nueva."
      footer={backToLogin}
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
        {errorMessage && (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}
        <Button type="submit" size="lg" className="h-11 w-full text-base" disabled={requestReset.isPending}>
          {requestReset.isPending ? 'Enviando…' : 'Enviar enlace'}
        </Button>
      </form>
    </AuthShell>
  )
}
