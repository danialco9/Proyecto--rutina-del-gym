import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router'
import { toast } from 'sonner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ApiError } from '@/lib/api'
import { AuthShell, FormField } from './AuthForm'
import { tooManyAttemptsMessage } from './errors'
import { useConfirmPasswordReset } from './queries'
import { newPasswordSchema, type NewPasswordInput } from './schema'

const askAgain = (
  <Link to="/recuperar" className="text-primary font-medium underline-offset-4 hover:underline">
    Pedir un enlace nuevo
  </Link>
)

function resetErrorMessage(error: Error): string {
  if (error instanceof ApiError && error.status === 400) {
    return 'Este enlace ha caducado o ya se usó. Pide uno nuevo.'
  }
  return tooManyAttemptsMessage(error) ?? 'No se pudo conectar con el servidor. Inténtalo de nuevo.'
}

/** Opened from the emailed link, which carries the token after `#` so it never reaches a server log. */
export function ResetPasswordPage() {
  const { hash } = useLocation()
  const [token] = useState(() => new URLSearchParams(hash.slice(1)).get('token'))
  const confirmReset = useConfirmPasswordReset()
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<NewPasswordInput>({
    resolver: zodResolver(newPasswordSchema),
    defaultValues: { password: '', confirmPassword: '' },
  })

  if (token === null) {
    return (
      <AuthShell title="Enlace no válido" description="Le falta una parte al enlace." footer={askAgain}>
        <p className="text-sm">Ábrelo directamente desde el email, o pide uno nuevo.</p>
      </AuthShell>
    )
  }

  const onSubmit = handleSubmit(({ password }) =>
    confirmReset.mutate(
      { token, password },
      {
        onSuccess: () => {
          toast.success('Contraseña cambiada. Ya puedes entrar con la nueva.')
          navigate('/login', { replace: true })
        },
      },
    ),
  )

  return (
    <AuthShell
      title="Nueva contraseña"
      description="Elige la contraseña con la que entrarás a partir de ahora."
      footer={askAgain}
    >
      <form className="space-y-4" onSubmit={onSubmit} noValidate>
        <FormField
          id="password"
          label="Contraseña nueva"
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
        {confirmReset.error !== null && (
          <Alert variant="destructive">
            <AlertDescription>{resetErrorMessage(confirmReset.error)}</AlertDescription>
          </Alert>
        )}
        <Button type="submit" size="lg" className="h-11 w-full text-base" disabled={confirmReset.isPending}>
          {confirmReset.isPending ? 'Guardando…' : 'Guardar contraseña'}
        </Button>
      </form>
    </AuthShell>
  )
}
