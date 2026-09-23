import { z } from 'zod'
import { ApiError, apiFetch } from '@/lib/api'
import type { Workout, WorkoutIn } from '@/lib/types'

export const OUTBOX_STORAGE_KEY = 'gym-tracker:workout-outbox:v1'

/**
 * Workouts finished with no connection, waiting on this device to be sent.
 *
 * Each one carries the client id of its draft, so sending it again after a request whose answer
 * never arrived cannot save it twice: the server answers with the workout it already has. Each one
 * also remembers who logged it, so it is only ever sent with that user's session.
 */
const queuedWorkoutSchema = z.object({
  userId: z.number().int(),
  queuedAt: z.iso.datetime({ offset: true }),
  // Set when the server refused it (for instance, its routine was deleted meanwhile): sending it
  // again would fail the same way, so it waits for the user to discard it.
  rejected: z.boolean().default(false),
  payload: z.custom<WorkoutIn & { client_id: string }>(
    (value) =>
      typeof value === 'object' && value !== null && typeof (value as WorkoutIn).client_id === 'string',
  ),
})

export type QueuedWorkout = z.infer<typeof queuedWorkoutSchema>

const listeners = new Set<() => void>()
let cached: { raw: string | null; items: QueuedWorkout[] } | null = null

function readRaw(): string | null {
  try {
    return window.localStorage.getItem(OUTBOX_STORAGE_KEY)
  } catch {
    return null
  }
}

/** Everything queued on this device, oldest first. Returns the same array while nothing changes. */
export function loadOutbox(): QueuedWorkout[] {
  const raw = readRaw()
  if (cached?.raw === raw) {
    return cached.items
  }
  let items: QueuedWorkout[] = []
  try {
    const parsed = z.array(queuedWorkoutSchema).safeParse(JSON.parse(raw ?? '[]'))
    items = parsed.success ? parsed.data : []
  } catch {
    items = []
  }
  cached = { raw, items }
  return items
}

function saveOutbox(items: QueuedWorkout[]): void {
  try {
    if (items.length === 0) {
      window.localStorage.removeItem(OUTBOX_STORAGE_KEY)
    } else {
      window.localStorage.setItem(OUTBOX_STORAGE_KEY, JSON.stringify(items))
    }
  } catch {
    // Storage unavailable: nothing can be kept for later, which the caller already told the user.
  }
  listeners.forEach((listener) => listener())
}

export function subscribeOutbox(listener: () => void): () => void {
  listeners.add(listener)
  // Another tab of the app may queue or send workouts too.
  const onStorage = (event: StorageEvent) => {
    if (event.key === OUTBOX_STORAGE_KEY) listener()
  }
  window.addEventListener('storage', onStorage)
  return () => {
    listeners.delete(listener)
    window.removeEventListener('storage', onStorage)
  }
}

/** Queues a workout; queuing the same client id again replaces the earlier copy. */
export function enqueueWorkout(payload: WorkoutIn & { client_id: string }, userId: number): void {
  const others = loadOutbox().filter((item) => item.payload.client_id !== payload.client_id)
  saveOutbox([...others, { userId, queuedAt: new Date().toISOString(), rejected: false, payload }])
}

export function removeQueuedWorkout(clientId: string): void {
  saveOutbox(loadOutbox().filter((item) => item.payload.client_id !== clientId))
}

/** Forgets everything the user queued, as signing out does for the draft. */
export function clearOutbox(userId: number): void {
  saveOutbox(loadOutbox().filter((item) => item.userId !== userId))
}

function markRejected(clientId: string): void {
  saveOutbox(
    loadOutbox().map((item) => (item.payload.client_id === clientId ? { ...item, rejected: true } : item)),
  )
}

/**
 * A failure worth trying again later: no connection, or the server itself failing. A 4xx answer is
 * about the request, and the same request would get it again.
 */
export function isTransient(error: unknown): boolean {
  return !(error instanceof ApiError) || error.status >= 500
}

export interface FlushResult {
  sent: number
  rejected: number
}

/**
 * Sends the user's queued workouts one by one, oldest first. Stops at the first failure that is not
 * the workout's own fault (no connection, server down, session expired) and leaves the rest queued.
 */
export async function flushOutbox(userId: number): Promise<FlushResult> {
  const result: FlushResult = { sent: 0, rejected: 0 }
  const pending = loadOutbox().filter((item) => item.userId === userId && !item.rejected)
  for (const item of pending) {
    try {
      await apiFetch<Workout>('/workouts', { method: 'POST', body: item.payload })
      removeQueuedWorkout(item.payload.client_id)
      result.sent += 1
    } catch (error) {
      if (isTransient(error) || (error instanceof ApiError && error.status === 401)) {
        break
      }
      markRejected(item.payload.client_id)
      result.rejected += 1
    }
  }
  return result
}
