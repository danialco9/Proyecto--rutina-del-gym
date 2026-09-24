import { z } from 'zod'

const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 128

const email = z.email('Introduce un email válido')

export const loginSchema = z.object({
  email,
  password: z
    .string()
    .min(1, 'Introduce tu contraseña')
    .max(MAX_PASSWORD_LENGTH, 'La contraseña es demasiado larga'),
})

const newPassword = z
  .string()
  .min(MIN_PASSWORD_LENGTH, `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`)
  .max(MAX_PASSWORD_LENGTH, 'La contraseña es demasiado larga')

const passwordsMatch = {
  check: (values: { password: string; confirmPassword: string }) =>
    values.password === values.confirmPassword,
  params: { message: 'Las contraseñas no coinciden', path: ['confirmPassword'] },
}

export const registerSchema = z
  .object({ email, password: newPassword, confirmPassword: z.string() })
  .refine(passwordsMatch.check, passwordsMatch.params)

export const forgotPasswordSchema = z.object({ email })

export const newPasswordSchema = z
  .object({ password: newPassword, confirmPassword: z.string() })
  .refine(passwordsMatch.check, passwordsMatch.params)

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>
export type NewPasswordInput = z.infer<typeof newPasswordSchema>
