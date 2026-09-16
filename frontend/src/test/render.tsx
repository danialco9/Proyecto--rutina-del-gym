import { QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { createQueryClient } from '@/lib/query-client'
import { routes } from '@/routes'

/** Renders the full app route tree at `path` with a fresh query cache. */
export function renderRoute(path: string) {
  // The app's client (with its session handling), without retries so failures show up at once.
  const queryClient = createQueryClient()
  queryClient.setDefaultOptions({
    queries: { retry: false, refetchOnWindowFocus: false },
    mutations: { retry: false },
  })
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  const user = userEvent.setup()
  const view = render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
  return { ...view, user, router }
}
