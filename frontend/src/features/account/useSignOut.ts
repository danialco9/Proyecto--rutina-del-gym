import { useNavigate } from 'react-router'
import { useLogout } from '@/features/auth/queries'
import { loadDraft, saveDraft } from '@/features/workout/draft'
import { clearOutbox } from '@/features/workout/outbox'
import { useOutbox } from '@/features/workout/useOutbox'

/** Signs out, first asking whether to drop a workout in progress or one still waiting to upload. */
export function useSignOut() {
  const logout = useLogout()
  const navigate = useNavigate()
  const queued = useOutbox()

  const signOut = () => {
    // Nothing unsent may be left on the device for the next account that signs in.
    const warning =
      loadDraft() !== null
        ? 'Tienes un entreno sin guardar. Si cierras sesión se descartará. ¿Cerrar sesión?'
        : queued.length > 0
          ? 'Tienes entrenos sin subir que están solo en este móvil. Si cierras sesión se perderán. ¿Cerrar sesión?'
          : null
    if (warning !== null && !window.confirm(warning)) {
      return
    }
    const userId = queued[0]?.userId
    logout.mutate(undefined, {
      onSuccess: () => {
        saveDraft(null)
        if (userId !== undefined) clearOutbox(userId)
        navigate('/login', { replace: true })
      },
    })
  }

  return { signOut, pending: logout.isPending }
}
