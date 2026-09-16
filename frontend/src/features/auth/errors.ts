import { ApiError } from '@/lib/api'
import { plural } from '@/lib/format'

const SECONDS_PER_MINUTE = 60

/** Spanish message for a rate-limited request (`429`), or null for any other error. */
export function tooManyAttemptsMessage(error: Error): string | null {
  if (!(error instanceof ApiError) || error.status !== 429) {
    return null
  }
  const seconds = error.retryAfterSeconds
  if (seconds === null) {
    return 'Demasiados intentos. Espera unos minutos y vuelve a probar.'
  }
  if (seconds < SECONDS_PER_MINUTE) {
    return `Demasiados intentos. Vuelve a probar en ${seconds} ${plural(seconds, 'segundo', 'segundos')}.`
  }
  const minutes = Math.ceil(seconds / SECONDS_PER_MINUTE)
  return `Demasiados intentos. Vuelve a probar en ${minutes} ${plural(minutes, 'minuto', 'minutos')}.`
}
