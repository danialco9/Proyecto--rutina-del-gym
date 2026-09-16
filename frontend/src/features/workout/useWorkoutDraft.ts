import { useCallback, useEffect, useReducer } from 'react'
import { draftReducer, loadDraft, saveDraft, type DraftAction } from './draft'

/** Workout draft state, restored from and persisted to this device's storage. */
export function useWorkoutDraft() {
  const [draft, dispatch] = useReducer(draftReducer, null, () => loadDraft())

  useEffect(() => {
    saveDraft(draft)
  }, [draft])

  const update = useCallback((action: DraftAction) => {
    dispatch(action)
    if (action.type === 'discard') {
      // Clear right away: the page may unmount (navigation) before the effect runs.
      saveDraft(null)
    }
  }, [])

  return [draft, update] as const
}
