import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { SLOW_REQUEST_MS, SlowServerNotice } from '@/components/SlowServerNotice'

let answer: (value: string) => void

function Screen() {
  useQuery({
    queryKey: ['slow'],
    queryFn: () => new Promise<string>((resolve) => (answer = resolve)),
  })
  return <SlowServerNotice />
}

/** Renders a screen whose request is on its way; TanStack reports it on the next tick. */
function renderWithClient() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <Screen />
    </QueryClientProvider>,
  )
  act(() => vi.advanceTimersByTime(0))
}

beforeEach(() => {
  vi.useFakeTimers()
  vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true)
})

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
})

test('says nothing while the server answers quickly', () => {
  renderWithClient()
  act(() => vi.advanceTimersByTime(SLOW_REQUEST_MS - 1))

  expect(screen.queryByRole('status')).toBeNull()
})

test('explains a slow request, and goes away once the answer arrives', async () => {
  renderWithClient()
  act(() => vi.advanceTimersByTime(SLOW_REQUEST_MS))

  expect(screen.getByRole('status')).toHaveTextContent('Arrancando el servidor')

  await act(async () => answer('ok'))
  act(() => vi.advanceTimersByTime(0))

  expect(screen.queryByRole('status')).toBeNull()
})

test('leaves the offline notice to speak when there is no connection', () => {
  vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(false)
  renderWithClient()
  act(() => vi.advanceTimersByTime(SLOW_REQUEST_MS))

  expect(screen.queryByRole('status')).toBeNull()
})
