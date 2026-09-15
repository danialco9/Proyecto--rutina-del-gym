import { QueryClient } from '@tanstack/react-query'
import { ApiError } from './api'

const MAX_RETRIES = 2

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Client errors (401, 404, 422...) will not succeed on retry; network and server errors might.
        retry: (failureCount, error) =>
          !(error instanceof ApiError && error.status < 500) && failureCount < MAX_RETRIES,
        refetchOnWindowFocus: false,
      },
    },
  })
}
