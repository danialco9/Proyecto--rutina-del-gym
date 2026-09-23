import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import { QueryStatus } from '@/components/QueryStatus'

type Query = Parameters<typeof QueryStatus>[0]['query']

const pending: Query = { isPending: true, isError: false, fetchStatus: 'fetching' }
const paused: Query = { isPending: true, isError: false, fetchStatus: 'paused' }
const failed: Query = { isPending: false, isError: true, fetchStatus: 'idle' }
const done: Query = { isPending: false, isError: false, fetchStatus: 'idle' }

function setOnline(value: boolean) {
  vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(value)
}

function renderStatus(query: Query) {
  return render(
    <QueryStatus query={query} loading="Cargando rutinas…" error="No se pudieron cargar las rutinas." />,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
})

test('says it is loading while the first answer is on its way', () => {
  setOnline(true)
  renderStatus(pending)

  expect(screen.getByText('Cargando rutinas…')).toBeInTheDocument()
})

test('says the connection is missing instead of loading forever when the query is paused', () => {
  setOnline(false)
  renderStatus(paused)

  expect(screen.getByRole('status')).toHaveTextContent('Sin conexión. Se cargará cuando vuelva la cobertura.')
  expect(screen.queryByText('Cargando rutinas…')).toBeNull()
})

test('says the connection is missing while an app opened offline is still retrying', () => {
  setOnline(false)
  renderStatus(pending)

  expect(screen.getByRole('status')).toHaveTextContent('Sin conexión')
})

test('does not blame the server for a request that failed because the connection dropped', () => {
  setOnline(false)
  renderStatus(failed)

  expect(screen.getByRole('status')).toHaveTextContent('Sin conexión')
  expect(screen.queryByText('No se pudieron cargar las rutinas.')).toBeNull()
})

test('reports a real error when the connection is there', () => {
  setOnline(true)
  renderStatus(failed)

  expect(screen.getByText('No se pudieron cargar las rutinas.')).toBeInTheDocument()
  expect(screen.queryByRole('status')).toBeNull()
})

test('renders nothing once the data is there', () => {
  setOnline(true)
  const { container } = renderStatus(done)

  expect(container).toBeEmptyDOMElement()
})
