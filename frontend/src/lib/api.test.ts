import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch } from './api'

function jsonResponse(payload: unknown, status: number): Response {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

describe('apiFetch', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sends JSON to the /api prefix and parses the response', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: 1 }, 201))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiFetch('/routines', { method: 'POST', body: { name: 'Pierna' } })).resolves.toEqual({
      id: 1,
    })
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/routines',
      expect.objectContaining({ method: 'POST', body: '{"name":"Pierna"}', credentials: 'same-origin' }),
    )
  })

  it('returns undefined for empty responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })))

    await expect(apiFetch('/auth/logout', { method: 'POST' })).resolves.toBeUndefined()
  })

  it('throws ApiError with the server detail', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Invalid email or password' }, 401)),
    )

    const request = apiFetch('/auth/login', { method: 'POST', body: {} })

    await expect(request).rejects.toBeInstanceOf(ApiError)
    await expect(request).rejects.toMatchObject({ status: 401, message: 'Invalid email or password' })
  })
})
