import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query'
import { ApiError } from './api'
import { currentUserQueryKey } from './session'

const MAX_RETRIES = 2

/**
 * A 401 from any request means the session cookie expired or was revoked. Forgetting the user
 * makes the protected routes redirect to the login page, which then returns to the same page;
 * anything kept on the device (like a workout draft) is still there.
 */
function endExpiredSession(queryClient: QueryClient, error: Error): void {
  if (error instanceof ApiError && error.status === 401 && queryClient.getQueryData(currentUserQueryKey)) {
    queryClient.setQueryData(currentUserQueryKey, null)
  }
}

export function createQueryClient(): QueryClient {
  const queryClient: QueryClient = new QueryClient({
    queryCache: new QueryCache({ onError: (error) => endExpiredSession(queryClient, error) }),
    mutationCache: new MutationCache({ onError: (error) => endExpiredSession(queryClient, error) }),
    defaultOptions: {
      queries: {
        // Client errors (401, 404, 422...) will not succeed on retry; network and server errors might.
        retry: (failureCount, error) =>
          !(error instanceof ApiError && error.status < 500) && failureCount < MAX_RETRIES,
        refetchOnWindowFocus: false,
      },
    },
  })
  return queryClient
}
