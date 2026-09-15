import { describe, expect, it } from 'vitest'
import type { Exercise } from '@/lib/types'
import { filterExercises } from './exercise-search'

function exercise(
  id: number,
  name: string,
  muscle_group: Exercise['muscle_group'],
  equipment: Exercise['equipment'],
) {
  return {
    id,
    slug: `exercise-${id}`,
    name,
    muscle_group,
    equipment,
    secondary_muscles: [],
    is_custom: false,
  }
}

const EXERCISES: Exercise[] = [
  exercise(1, 'Jalón al pecho', 'back', 'cable'),
  exercise(2, 'Prensa de piernas', 'quads', 'machine'),
  exercise(3, 'Press banca con barra', 'chest', 'barbell'),
]

const names = (query: string) => filterExercises(EXERCISES, query).map((item) => item.name)

describe('filterExercises', () => {
  it('returns everything for an empty query', () => {
    expect(names('  ')).toHaveLength(3)
  })

  it('ignores accents and case', () => {
    expect(names('JALON')).toEqual(['Jalón al pecho'])
  })

  it('matches muscle group and equipment labels', () => {
    expect(names('pecho')).toEqual(['Jalón al pecho', 'Press banca con barra'])
    expect(names('maquina prensa')).toEqual(['Prensa de piernas'])
  })
})
