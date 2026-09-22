import { beforeEach, expect, test } from 'vitest'
import { loadCachedUser, saveCachedUser, SESSION_STORAGE_KEY } from '@/lib/session'

const user = { id: 1, email: 'dani@example.com', created_at: '2026-09-01T10:00:00+00:00' }

beforeEach(() => {
  window.localStorage.clear()
})

test('remembers the confirmed user across reloads', () => {
  saveCachedUser(user)

  expect(loadCachedUser()).toEqual(user)
})

test('forgets the user when the session ends', () => {
  saveCachedUser(user)
  saveCachedUser(null)

  expect(loadCachedUser()).toBeNull()
})

test('ignores anything that is not a user', () => {
  window.localStorage.setItem(SESSION_STORAGE_KEY, '{"id":"not a number"}')

  expect(loadCachedUser()).toBeNull()
})
