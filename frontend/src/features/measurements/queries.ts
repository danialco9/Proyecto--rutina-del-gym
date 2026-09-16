import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from '@/lib/api'
import type { BodyMeasurement, BodyMeasurementIn } from '@/lib/types'

export const measurementKeys = {
  all: ['measurements'] as const,
}

/** All of the user's measurements, oldest first (as the API returns them). */
export function useMeasurements() {
  return useQuery({
    queryKey: measurementKeys.all,
    queryFn: ({ signal }) => apiFetch<BodyMeasurement[]>('/measurements', { signal }),
  })
}

interface SaveMeasurementInput {
  /** Updates this measurement when set; creates a new one otherwise. */
  id?: number
  payload: BodyMeasurementIn
}

export function useSaveMeasurement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: SaveMeasurementInput) =>
      id === undefined
        ? apiFetch<BodyMeasurement>('/measurements', { method: 'POST', body: payload })
        : apiFetch<BodyMeasurement>(`/measurements/${id}`, { method: 'PUT', body: payload }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: measurementKeys.all }),
  })
}

export function useDeleteMeasurement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiFetch<void>(`/measurements/${id}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: measurementKeys.all }),
  })
}
