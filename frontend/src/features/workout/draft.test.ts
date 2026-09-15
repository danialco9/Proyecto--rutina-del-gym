import { beforeEach, describe, expect, it } from 'vitest'
import type { Routine } from '@/lib/types'
import {
  completedSetCount,
  DRAFT_STORAGE_KEY,
  draftReducer,
  loadDraft,
  saveDraft,
  toWorkoutPayload,
  type DraftAction,
  type WorkoutDraft,
} from './draft'

const STARTED_AT = '2026-09-15T16:00:00.000Z'
const ENDED_AT = '2026-09-15T17:10:00.000Z'

const legDay: Routine = {
  id: 7,
  name: 'Pierna',
  description: null,
  created_at: STARTED_AT,
  exercises: [
    {
      id: 1,
      position: 1,
      target_sets: 3,
      target_reps: 8,
      target_weight_kg: 60,
      target_rpe: 8,
      exercise: {
        id: 11,
        slug: 'back-squat',
        name: 'Sentadilla con barra',
        muscle_group: 'quads',
        secondary_muscles: ['glutes'],
        equipment: 'barbell',
        is_custom: false,
      },
    },
  ],
}

function apply(draft: WorkoutDraft | null, ...actions: DraftAction[]): WorkoutDraft {
  const result = actions.reduce(draftReducer, draft)
  if (result === null) {
    throw new Error('Expected an active draft')
  }
  return result
}

const start = (routine?: Routine) => apply(null, { type: 'start', startedAt: STARTED_AT, routine })

describe('draftReducer', () => {
  it('prefills planned sets from the routine targets', () => {
    const draft = start(legDay)

    expect(draft.routineId).toBe(7)
    expect(draft.exercises).toHaveLength(1)
    expect(draft.exercises[0].sets.map(({ reps, weightKg, done }) => ({ reps, weightKg, done }))).toEqual([
      { reps: 8, weightKg: 60, done: false },
      { reps: 8, weightKg: 60, done: false },
      { reps: 8, weightKg: 60, done: false },
    ])
  })

  it('copies the previous set and clamps adjustments', () => {
    let draft = apply(start(), { type: 'addExercise', exercise: { id: 5, name: 'Prensa de piernas' } })
    const entryId = draft.exercises[0].id
    const firstSetId = draft.exercises[0].sets[0].id

    draft = apply(
      draft,
      { type: 'adjustSet', entryId, setId: firstSetId, field: 'weightKg', delta: -2.5 },
      { type: 'updateSet', entryId, setId: firstSetId, changes: { weightKg: 120.004, reps: 12 } },
      { type: 'addSet', entryId },
    )
    const secondSetId = draft.exercises[0].sets[1].id
    draft = apply(draft, { type: 'adjustSet', entryId, setId: secondSetId, field: 'reps', delta: 1 })

    expect(draft.exercises[0].sets.map(({ reps, weightKg }) => [reps, weightKg])).toEqual([
      [12, 120],
      [13, 120],
    ])
  })

  it('removes sets and exercises and discards the draft', () => {
    const draft = start(legDay)
    const entry = draft.exercises[0]

    expect(
      apply(draft, { type: 'removeSet', entryId: entry.id, setId: entry.sets[0].id }).exercises[0].sets,
    ).toHaveLength(2)
    expect(apply(draft, { type: 'removeExercise', entryId: entry.id }).exercises).toEqual([])
    expect(draftReducer(draft, { type: 'discard' })).toBeNull()
  })
})

describe('toWorkoutPayload', () => {
  it('sends only completed sets, numbered per exercise', () => {
    let draft = start(legDay)
    const entry = draft.exercises[0]
    draft = apply(
      draft,
      { type: 'toggleDone', entryId: entry.id, setId: entry.sets[0].id },
      { type: 'toggleDone', entryId: entry.id, setId: entry.sets[2].id },
      { type: 'addExercise', exercise: { id: 11, name: 'Sentadilla con barra' } },
      { type: 'setNotes', notes: '   ' },
    )
    const extra = draft.exercises[1]
    draft = apply(draft, { type: 'toggleDone', entryId: extra.id, setId: extra.sets[0].id })

    const payload = toWorkoutPayload(draft, ENDED_AT)

    expect(completedSetCount(draft)).toBe(3)
    expect(payload).toMatchObject({ routine_id: 7, started_at: STARTED_AT, ended_at: ENDED_AT, notes: null })
    expect(payload.sets.map((set) => [set.exercise_id, set.set_number, set.weight_kg])).toEqual([
      [11, 1, 60],
      [11, 2, 60],
      [11, 3, 0],
    ])
  })
})

describe('draft storage', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('restores a saved draft and clears it', () => {
    const draft = start(legDay)

    saveDraft(draft)
    expect(loadDraft()).toEqual(draft)

    saveDraft(null)
    expect(loadDraft()).toBeNull()
  })

  it('ignores corrupt or outdated data', () => {
    window.localStorage.setItem(DRAFT_STORAGE_KEY, '{not json')
    expect(loadDraft()).toBeNull()

    window.localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify({ startedAt: 'yesterday' }))
    expect(loadDraft()).toBeNull()
  })
})
