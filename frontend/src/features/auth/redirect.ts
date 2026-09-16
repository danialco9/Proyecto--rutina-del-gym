/** Page to open after signing in. Only same-app paths are accepted, so it cannot point to another site. */
export function redirectTarget(state: unknown): string {
  if (typeof state === 'object' && state !== null && 'from' in state && typeof state.from === 'string') {
    const { from } = state
    if (from.startsWith('/') && !from.startsWith('//')) {
      return from
    }
  }
  return '/'
}
