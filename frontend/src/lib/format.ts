const LOCALE = 'es-ES'

const decimalFormatter = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 2 })
const signedDecimalFormatter = new Intl.NumberFormat(LOCALE, {
  maximumFractionDigits: 2,
  signDisplay: 'exceptZero',
})
const dateFormatter = new Intl.DateTimeFormat(LOCALE, { weekday: 'short', day: 'numeric', month: 'short' })
const shortDateFormatter = new Intl.DateTimeFormat(LOCALE, { day: '2-digit', month: '2-digit' })
const timeFormatter = new Intl.DateTimeFormat(LOCALE, { hour: '2-digit', minute: '2-digit' })

export const formatDecimal = (value: number) => decimalFormatter.format(value)

export const formatKg = (value: number) => `${formatDecimal(value)} kg`

export const formatSignedKg = (value: number) => `${signedDecimalFormatter.format(value)} kg`

export const formatDate = (iso: string) => dateFormatter.format(new Date(iso))

/** Parses a calendar date (`YYYY-MM-DD`) as local midnight, so the day never shifts with the time zone. */
function parseDay(isoDate: string): Date {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export const formatDay = (isoDate: string) => dateFormatter.format(parseDay(isoDate))

export const formatShortDay = (isoDate: string) => shortDateFormatter.format(parseDay(isoDate))

export const formatShortDate = (iso: string) => shortDateFormatter.format(new Date(iso))

export const formatTime = (iso: string) => timeFormatter.format(new Date(iso))

export function formatDuration(startIso: string, endIso: string | null): string | null {
  if (endIso === null) {
    return null
  }
  const minutes = Math.max(0, Math.round((Date.parse(endIso) - Date.parse(startIso)) / 60_000))
  return minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)} h ${minutes % 60} min`
}

export function formatSeconds(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
}

export const plural = (count: number, singular: string, pluralForm: string) =>
  count === 1 ? singular : pluralForm
