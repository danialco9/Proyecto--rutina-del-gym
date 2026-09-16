import { describe, expect, it } from 'vitest'
import { ApiError } from '@/lib/api'
import { tooManyAttemptsMessage } from './errors'

describe('tooManyAttemptsMessage', () => {
  it('says how long to wait', () => {
    expect(tooManyAttemptsMessage(new ApiError(429, 'Too many', 1))).toBe(
      'Demasiados intentos. Vuelve a probar en 1 segundo.',
    )
    expect(tooManyAttemptsMessage(new ApiError(429, 'Too many', 60))).toBe(
      'Demasiados intentos. Vuelve a probar en 1 minuto.',
    )
    expect(tooManyAttemptsMessage(new ApiError(429, 'Too many', 61))).toBe(
      'Demasiados intentos. Vuelve a probar en 2 minutos.',
    )
    expect(tooManyAttemptsMessage(new ApiError(429, 'Too many'))).toBe(
      'Demasiados intentos. Espera unos minutos y vuelve a probar.',
    )
  })

  it('ignores other errors', () => {
    expect(tooManyAttemptsMessage(new ApiError(401, 'Invalid'))).toBeNull()
    expect(tooManyAttemptsMessage(new Error('offline'))).toBeNull()
  })
})
