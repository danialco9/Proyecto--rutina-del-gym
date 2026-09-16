import { ActiveWorkout } from './ActiveWorkout'
import { StartWorkout } from './StartWorkout'
import { useWorkoutDraft } from './useWorkoutDraft'

export function WorkoutPage() {
  const [draft, dispatch] = useWorkoutDraft()

  if (draft === null) {
    return (
      <StartWorkout
        onStart={(routine) => dispatch({ type: 'start', startedAt: new Date().toISOString(), routine })}
      />
    )
  }
  return <ActiveWorkout draft={draft} dispatch={dispatch} />
}
