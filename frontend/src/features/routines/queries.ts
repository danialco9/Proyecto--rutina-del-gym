import { useMutation, useQueryClient } from '@tanstack/react-query'
import { progressKeys } from '@/features/progress/queries'
import { queryKeys } from '@/features/workout/queries'
import { apiFetch } from '@/lib/api'
import type { Routine, RoutineIn } from '@/lib/types'

export function useCreateRoutine() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RoutineIn) => apiFetch<Routine>('/routines', { method: 'POST', body: payload }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.routines }),
  })
}

export function useUpdateRoutine(routineId: number | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RoutineIn) =>
      apiFetch<Routine>(`/routines/${routineId}`, { method: 'PUT', body: payload }),
    // Routine targets feed the progression recommendations.
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.routines }),
        queryClient.invalidateQueries({ queryKey: progressKeys.all }),
      ]),
  })
}

export function useDeleteRoutine() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (routineId: number) => apiFetch<void>(`/routines/${routineId}`, { method: 'DELETE' }),
    // Past workouts keep their data but lose the link to the routine.
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.routines }),
        queryClient.invalidateQueries({ queryKey: queryKeys.workouts }),
        queryClient.invalidateQueries({ queryKey: progressKeys.all }),
      ]),
  })
}
