import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, apiFetch } from '@/lib/api'
import type { User } from '@/lib/types'
import { currentUserQueryKey } from '@/lib/session'
import type { LoginInput } from './schema'

export { currentUserQueryKey }

/** The signed-in user, or `null` when there is no valid session cookie. */
export function useCurrentUser() {
  return useQuery({
    queryKey: currentUserQueryKey,
    queryFn: async ({ signal }) => {
      try {
        return await apiFetch<User>('/auth/me', { signal })
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          return null
        }
        throw error
      }
    },
    staleTime: 5 * 60_000,
    retry: false,
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (account: LoginInput) => apiFetch<User>('/auth/register', { method: 'POST', body: account }),
    onSuccess: (user) => queryClient.setQueryData(currentUserQueryKey, user),
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (credentials: LoginInput) =>
      apiFetch<void>('/auth/login', { method: 'POST', body: credentials }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: currentUserQueryKey }),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiFetch<void>('/auth/logout', { method: 'POST' }),
    onSuccess: () => {
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== 'auth' })
      queryClient.setQueryData(currentUserQueryKey, null)
    },
  })
}
