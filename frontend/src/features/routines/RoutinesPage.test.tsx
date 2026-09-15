import { screen } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { Exercise, Routine, User } from '@/lib/types'
import { mockApi } from '@/test/mock-api'
import { renderRoute } from '@/test/render'

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

const SQUAT: Exercise = {
  id: 11,
  slug: 'back-squat',
  name: 'Sentadilla con barra',
  muscle_group: 'quads',
  secondary_muscles: ['glutes'],
  equipment: 'barbell',
  is_custom: false,
}

function legDay(overrides: Partial<Routine> = {}): Routine {
  return {
    id: 7,
    name: 'Pierna',
    description: 'Miércoles',
    created_at: '2026-09-15T10:00:00Z',
    exercises: [
      {
        id: 1,
        position: 1,
        exercise: SQUAT,
        target_sets: 4,
        target_reps: 8,
        target_weight_kg: 60,
        target_rpe: null,
      },
    ],
    ...overrides,
  }
}

async function addExercise(user: UserEvent, search: string, name: string) {
  await user.click(screen.getByRole('button', { name: /Añadir ejercicio/ }))
  const searchbox = await screen.findByRole('searchbox', { name: 'Buscar ejercicio' })
  await user.clear(searchbox)
  await user.type(searchbox, search)
  await user.click(screen.getByRole('button', { name: new RegExp(name) }))
}

describe('Routines', () => {
  it('creates a routine with ordered exercises and targets', async () => {
    let routines: Routine[] = []
    const calls = mockApi({
      'GET /auth/me': { body: USER },
      'GET /routines': () => ({ body: routines }),
      'GET /exercises': { body: [LEG_PRESS, SQUAT] },
      'POST /routines': () => {
        routines = [legDay()]
        return { status: 201, body: routines[0] }
      },
    })
    const { user } = renderRoute('/rutinas')

    await user.click(await screen.findByRole('link', { name: /Nueva rutina/ }))
    await user.type(await screen.findByLabelText('Nombre'), 'Pierna')
    await addExercise(user, 'prensa', 'Prensa de piernas')
    await addExercise(user, 'sentadilla', 'Sentadilla con barra')
    await user.click(screen.getByRole('button', { name: 'Subir Sentadilla con barra' }))
    await user.type(screen.getAllByLabelText('Series')[0], '4')
    await user.type(screen.getAllByLabelText('Peso (kg)')[0], '60,5')
    await user.click(screen.getByRole('button', { name: 'Guardar rutina' }))

    expect(await screen.findByRole('link', { name: /Pierna/ })).toBeInTheDocument()
    expect(calls.find((call) => call.method === 'POST' && call.path === '/routines')?.body).toEqual({
      name: 'Pierna',
      description: null,
      exercises: [
        { exercise_id: 11, target_sets: 4, target_reps: null, target_weight_kg: 60.5, target_rpe: null },
        { exercise_id: 5, target_sets: null, target_reps: null, target_weight_kg: null, target_rpe: null },
      ],
    })
  })

  it('edits and deletes an existing routine', async () => {
    let routines: Routine[] = [legDay()]
    const calls = mockApi({
      'GET /auth/me': { body: USER },
      'GET /routines': () => ({ body: routines }),
      'GET /exercises': { body: [SQUAT] },
      'PUT /routines/7': () => {
        routines = [legDay({ name: 'Pierna A' })]
        return { body: routines[0] }
      },
      'DELETE /routines/7': () => {
        routines = []
        return { status: 204 }
      },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const { user } = renderRoute('/rutinas')

    await user.click(await screen.findByRole('link', { name: /Pierna/ }))
    const name = await screen.findByLabelText('Nombre')
    expect(name).toHaveValue('Pierna')
    expect(screen.getByLabelText('Peso (kg)')).toHaveValue('60')
    await user.clear(name)
    await user.type(name, 'Pierna A')
    await user.click(screen.getByRole('button', { name: 'Guardar rutina' }))

    expect(await screen.findByRole('link', { name: /Pierna A/ })).toBeInTheDocument()
    expect(calls.find((call) => call.method === 'PUT')?.body).toMatchObject({
      name: 'Pierna A',
      description: 'Miércoles',
      exercises: [{ exercise_id: 11, target_sets: 4, target_reps: 8, target_weight_kg: 60 }],
    })

    await user.click(screen.getByRole('link', { name: /Pierna A/ }))
    await user.click(await screen.findByRole('button', { name: /Eliminar rutina/ }))

    expect(await screen.findByText(/Aún no tienes rutinas/)).toBeInTheDocument()
    expect(calls.some((call) => call.method === 'DELETE' && call.path === '/routines/7')).toBe(true)
  })

  it('validates the form and explains duplicate names', async () => {
    mockApi({
      'GET /auth/me': { body: USER },
      'GET /routines': { body: [] },
      'POST /routines': { status: 409, body: { detail: 'A routine with this name already exists' } },
    })
    const { user } = renderRoute('/rutinas/nueva')

    await user.click(await screen.findByRole('button', { name: 'Guardar rutina' }))
    expect(await screen.findByText('Ponle un nombre a la rutina')).toBeInTheDocument()

    await user.type(screen.getByLabelText('Nombre'), 'Pierna')
    await user.click(screen.getByRole('button', { name: 'Guardar rutina' }))
    expect(await screen.findByText('Ya tienes una rutina con ese nombre')).toBeInTheDocument()
  })
})
