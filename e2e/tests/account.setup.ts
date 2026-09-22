import { randomUUID } from 'node:crypto'
import { expect, test as setup } from '@playwright/test'

const STORAGE_STATE = '.auth/user.json'

/**
 * Every run works on an account of its own, registered through the API. The suite can then create
 * routines and workouts without reading anything another run left behind, and without touching the
 * public demo account, which is a fixture the README points visitors at.
 */
setup('register the account the suite works on', async ({ request }) => {
  const response = await request.post('/api/auth/register', {
    data: { email: `e2e-${randomUUID()}@example.test`, password: `e2e-${randomUUID()}` },
  })
  expect(response.ok(), `registration failed: ${response.status()} ${await response.text()}`).toBe(true)

  await request.storageState({ path: STORAGE_STATE })
})
