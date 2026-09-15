import { z } from 'zod'

export const loginSchema = z.object({
  email: z.email('Introduce un email válido'),
  password: z.string().min(1, 'Introduce tu contraseña').max(128, 'La contraseña es demasiado larga'),
})

export type LoginInput = z.infer<typeof loginSchema>
