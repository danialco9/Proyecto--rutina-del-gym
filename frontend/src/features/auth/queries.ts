import { type QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, apiFetch } from '@/lib/api'
import { isOnline } from '@/lib/online'
import type { User } from '@/lib/types'
import { currentUserQueryKey, loadCachedUser, saveCachedUser } from '@/lib/session'
import type { LoginInput } from './schema'

export { currentUserQueryKey }

/**
 * The signed-in user, or `null` when there is no valid session cookie.
 *
 * With no connection the question cannot be asked, so the last confirmed user stands in for the
 * answer: otherwise the app installed on a phone could only ever show its login page in the gym,
 * which is exactly where the connection fails. The stand-in lasts only as long as the outage.
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: currentUserQueryKey,
    queryFn: async ({ signal }) => {
      try {
        const user = await apiFetch<User>('/auth/me', { signal })
        saveCachedUser(user)
        return user
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          saveCachedUser(null)
          return null
        }
        const cachedUser = loadCachedUser()
        if (!isOnline() && cachedUser !== null) {
          return cachedUser
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
    onSuccess: (user) => {
      saveCachedUser(user)
      queryClient.setQueryData(currentUserQueryKey, user)
    },
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

export function useDemoLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiFetch<void>('/auth/demo', { method: 'POST' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: currentUserQueryKey }),
  })
}

/** Forgets everything cached for the account that just left, so the next one starts clean. */
function forgetSession(queryClient: QueryClient) {
  saveCachedUser(null)
  queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== 'auth' })
  queryClient.setQueryData(currentUserQueryKey, null)
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiFetch<void>('/auth/logout', { method: 'POST' }),
    onSuccess: () => forgetSession(queryClient),
  })
}

/** Asks for a reset link by email. The server answers the same whether the account exists or not. */
export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: (email: string) =>
      apiFetch<void>('/auth/password-reset', { method: 'POST', body: { email } }),
  })
}

export function useConfirmPasswordReset() {
  return useMutation({
    mutationFn: (reset: { token: string; password: string }) =>
      apiFetch<void>('/auth/password-reset/confirm', { method: 'POST', body: reset }),
  })
}

/** Deletes the account and all its data. The server asks for the password again to confirm. */
export function useDeleteAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (password: string) => apiFetch<void>('/auth/me', { method: 'DELETE', body: { password } }),
    onSuccess: () => forgetSession(queryClient),
  })
}
