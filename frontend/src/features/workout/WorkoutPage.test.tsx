import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { Exercise, User } from '@/lib/types'
import { mockApi } from '@/test/mock-api'
import { renderRoute } from '@/test/render'
import { DRAFT_STORAGE_KEY, type WorkoutDraft } from './draft'

const USER: User = { id: 1, email: 'dani@example.com', created_at: '2026-09-15T10:00:00Z' }

const LEG_PRESS: Exercise = {
  id: 5,
  slug: 'leg-press',
  name: 'Prensa de piernas',
  muscle_group: 'quads',
  secondary_muscles: ['glutes'],
  equipment: 'machine',
  is_custom: false,
}

const BENCH_PRESS: Exercise = {
  id: 6,
  slug: 'bench-press',
  name: 'Press banca con barra',
  muscle_group: 'chest',
  secondary_muscles: ['triceps'],
  equipment: 'barbell',
  is_custom: false,
}

describe('WorkoutPage', () => {
  it('logs a free workout and saves only the completed sets', async () => {
    const calls = mockApi({
      'GET /auth/me': { body: USER },
      'GET /routines': { body: [] },
      'GET /exercises': { body: [LEG_PRESS, BENCH_PRESS] },
      'GET /exercises/5/last-session': {
        body: {
          workout_id: 3,
          started_at: '2026-09-08T16:00:00Z',
          sets: [
            { id: 1, exercise_id: 5, set_number: 1, reps: 12, weight_kg: 110, rpe: null, is_warmup: false },
          ],
        },
      },
      'POST /workouts': { status: 201, body: { id: 99 } },
      'GET /workouts?limit=5': { body: [] },
    })
    const { user } = renderRoute('/entrenar')

    await user.click(await screen.findByRole('button', { name: /Entreno libre/ }))
    await user.click(screen.getByRole('button', { name: /Añadir ejercicio/ }))
    await user.type(await screen.findByRole('searchbox', { name: 'Buscar ejercicio' }), 'prensa')
    await user.click(screen.getByRole('button', { name: /Prensa de piernas/ }))

    expect(await screen.findByText(/110 kg × 12/)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Aumentar peso (kg)' }))
    await user.click(screen.getByRole('button', { name: 'Aumentar peso (kg)' }))
    await user.click(screen.getByRole('button', { name: /Añadir serie/ }))
    await user.click(screen.getByRole('button', { name: 'Completar serie 1' }))

    expect(screen.getByRole('timer')).toHaveTextContent(/Descanso/)

    await user.click(screen.getByRole('button', { name: 'Terminar y guardar' }))

    expect(await screen.findByRole('link', { name: /Empezar entreno/ })).toBeInTheDocument()
    expect(calls.find((call) => call.method === 'POST' && call.path === '/workouts')?.body).toMatchObject({
      routine_id: null,
      sets: [{ exercise_id: 5, set_number: 1, reps: 10, weight_kg: 5, rpe: null, is_warmup: false }],
    })
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).toBeNull()
  })

  it('restores the draft saved on this device', async () => {
    const draft: WorkoutDraft = {
      routineId: null,
      routineName: 'Pierna',
      startedAt: '2026-09-15T16:00:00.000Z',
      notes: '',
      exercises: [],
    }
    window.localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft))
    mockApi({ 'GET /auth/me': { body: USER } })

    renderRoute('/entrenar')

    expect(await screen.findByRole('heading', { name: 'Pierna' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Terminar y guardar' })).toBeDisabled()
  })
})

function draftWithDoneSet(): WorkoutDraft {
  return {
    routineId: null,
    routineName: null,
    startedAt: '2026-09-15T16:00:00.000Z',
    notes: '',
    exercises: [
      {
        id: 'entry-1',
        exerciseId: 5,
        name: 'Prensa de piernas',
        targets: [],
        sets: [{ id: 'set-1', reps: 12, weightKg: 110, rpe: null, isWarmup: false, done: true }],
      },
    ],
  }
}

describe('Session', () => {
  it('sends an expired session to the login and keeps the workout to save afterwards', async () => {
    let session: 'active' | 'expired' | 'renewed' = 'active'
    window.localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draftWithDoneSet()))
    const calls = mockApi({
      'GET /auth/me': () => (session === 'expired' ? { status: 401 } : { body: USER }),
      'POST /workouts': () => {
        if (session === 'renewed') {
          return { status: 201, body: { id: 99 } }
        }
        session = 'expired'
        return { status: 401, body: { detail: 'Not authenticated' } }
      },
      'POST /auth/login': () => {
        session = 'renewed'
        return { status: 204 }
      },
      'GET /workouts?limit=5': { body: [] },
    })
    const { user, router } = renderRoute('/entrenar')

    await user.click(await screen.findByRole('button', { name: 'Terminar y guardar' }))

    expect(await screen.findByRole('button', { name: 'Entrar' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).not.toBeNull()

    await user.type(screen.getByLabelText('Email'), 'dani@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'correct-horse-battery')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await user.click(await screen.findByRole('button', { name: 'Terminar y guardar' }))

    expect(await screen.findByRole('link', { name: /Empezar entreno/ })).toBeInTheDocument()
    expect(calls.filter((call) => call.method === 'POST' && call.path === '/workouts')).toHaveLength(2)
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).toBeNull()
  })

  it('asks before signing out with a workout in progress and then discards it', async () => {
    window.localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draftWithDoneSet()))
    let signedIn = true
    const calls = mockApi({
      'GET /auth/me': () => (signedIn ? { body: USER } : { status: 401 }),
      'POST /auth/logout': () => {
        signedIn = false
        return { status: 204 }
      },
    })
    const confirm = vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true)
    const { user, router } = renderRoute('/entrenar')

    await user.click(await screen.findByRole('button', { name: /Salir/ }))
    expect(confirm).toHaveBeenCalledTimes(1)
    expect(calls.some((call) => call.path === '/auth/logout')).toBe(false)
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).not.toBeNull()

    await user.click(screen.getByRole('button', { name: /Salir/ }))

    expect(await screen.findByRole('button', { name: 'Entrar' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')
    expect(window.localStorage.getItem(DRAFT_STORAGE_KEY)).toBeNull()
  })
})
