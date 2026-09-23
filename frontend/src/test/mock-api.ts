import { vi } from 'vitest'

interface MockResponse {
  /** Fail the way `fetch` does with no connection, instead of answering. */
  networkError?: boolean
  status?: number
  body?: unknown
  headers?: Record<string, string>
}

type MockHandler = MockResponse | ((request: { body: unknown }) => MockResponse)

export interface ApiCall {
  method: string
  path: string
  body: unknown
}

/**
 * Stubs `fetch` for `/api` requests. Handler keys look like `"GET /routines"` (query string included);
 * unmatched requests answer 404. Returns the list of calls made, for assertions.
 */
export function mockApi(handlers: Record<string, MockHandler>): ApiCall[] {
  const calls: ApiCall[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
      const path = String(input).replace(/^\/api/, '')
      const method = init?.method ?? 'GET'
      const body: unknown = typeof init?.body === 'string' ? JSON.parse(init.body) : undefined
      calls.push({ method, path, body })

      const handler = handlers[`${method} ${path}`] ?? { status: 404, body: { detail: 'Not mocked' } }
      const response = typeof handler === 'function' ? handler({ body }) : handler
      if (response.networkError === true) {
        throw new TypeError('Failed to fetch')
      }
      const status = response.status ?? 200
      if (status === 204) {
        return new Response(null, { status })
      }
      return new Response(JSON.stringify(response.body ?? null), {
        status,
        headers: { 'Content-Type': 'application/json', ...response.headers },
      })
    }),
  )
  return calls
}
