import { randomUUID } from 'node:crypto'
import { expect, test as base } from '@playwright/test'

/**
 * Every test starts signed in to an account of its own, registered through the API a moment
 * before. A test then never reads what another one left behind, even when the suite runs in
 * parallel or is repeated, and none of them touches the public demo account, which is a fixture
 * the README points visitors at.
 */
export const test = base.extend({
  storageState: async ({ playwright, baseURL }, use) => {
    const request = await playwright.request.newContext({ baseURL })
    const response = await request.post('/api/auth/register', {
      data: { email: `e2e-${randomUUID()}@gymtracker.dev`, password: `e2e-${randomUUID()}` },
    })
    expect(response.ok(), `registration failed: ${response.status()} ${await response.text()}`).toBe(true)

    const state = await request.storageState()
    await request.dispose()
    await use(state)
  },
})

export { expect }
