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

export const registerSchema = z
  .object({
    email,
    password: z
      .string()
      .min(MIN_PASSWORD_LENGTH, `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`)
      .max(MAX_PASSWORD_LENGTH, 'La contraseña es demasiado larga'),
    confirmPassword: z.string(),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: 'Las contraseñas no coinciden',
    path: ['confirmPassword'],
  })

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
