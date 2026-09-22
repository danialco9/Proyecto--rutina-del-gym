import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import { OfflineNotice } from '@/components/OfflineNotice'

function setOnline(value: boolean) {
  vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(value)
  window.dispatchEvent(new Event(value ? 'online' : 'offline'))
}

afterEach(() => {
  vi.restoreAllMocks()
})

test('says nothing while the connection holds', () => {
  setOnline(true)
  render(<OfflineNotice />)

  expect(screen.queryByRole('status')).toBeNull()
})

test('tells the user what still works once the connection drops', () => {
  setOnline(false)
  render(<OfflineNotice />)

  expect(screen.getByRole('status')).toHaveTextContent('Sin conexión')
})
