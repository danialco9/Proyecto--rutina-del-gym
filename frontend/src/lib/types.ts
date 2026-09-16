// Mirrors the backend response and request schemas (backend/src/gym_tracker/schemas.py).

export type MuscleGroup =
  | 'chest'
  | 'back'
  | 'lower_back'
  | 'traps'
  | 'shoulders'
  | 'biceps'
  | 'triceps'
  | 'forearms'
  | 'abs'
  | 'quads'
  | 'hamstrings'
  | 'glutes'
  | 'adductors'
  | 'abductors'
  | 'calves'

export type Equipment =
  | 'barbell'
  | 'ez_bar'
  | 'dumbbell'
  | 'kettlebell'
  | 'machine'
  | 'smith_machine'
  | 'cable'
  | 'bodyweight'
  | 'band'

export interface User {
  id: number
  email: string
  created_at: string
}

export interface Exercise {
  id: number
  slug: string
  name: string
  muscle_group: MuscleGroup
  secondary_muscles: MuscleGroup[]
  equipment: Equipment | null
  is_custom: boolean
}

export interface RoutineExercise {
  id: number
  position: number
  exercise: Exercise
  target_sets: number | null
  target_reps: number | null
  target_weight_kg: number | null
  target_rpe: number | null
}

export interface Routine {
  id: number
  name: string
  description: string | null
  created_at: string
  exercises: RoutineExercise[]
}

export interface WorkoutSet {
  id: number
  exercise_id: number
  set_number: number
  reps: number
  weight_kg: number
  rpe: number | null
  is_warmup: boolean
}

export interface Workout {
  id: number
  routine_id: number | null
  started_at: string
  ended_at: string | null
  notes: string | null
  sets: WorkoutSet[]
}

export type WorkoutSetIn = Omit<WorkoutSet, 'id'>

export interface WorkoutIn {
  routine_id: number | null
  started_at: string
  ended_at: string | null
  notes: string | null
  sets: WorkoutSetIn[]
}

export interface LastSession {
  workout_id: number
  started_at: string
  sets: WorkoutSet[]
}

export interface BodyMeasurement {
  id: number
  measured_on: string
  weight_kg: number | null
  body_fat_pct: number | null
  waist_cm: number | null
  chest_cm: number | null
  arm_cm: number | null
  thigh_cm: number | null
  notes: string | null
}
