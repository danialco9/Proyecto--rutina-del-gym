import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { User } from '@/lib/types'
import { mockApi } from '@/test/mock-api'
import { renderRoute } from '@/test/render'

const USER: User = { id: 1, email: 'dani@example.com', created_at: '2026-09-15T10:00:00Z' }
const SIGNED_OUT = { status: 401, body: { detail: 'Not authenticated' } }

describe('LoginPage', () => {
  it('redirects signed-out visitors to the login page', async () => {
    mockApi({ 'GET /auth/me': SIGNED_OUT })

    renderRoute('/entrenar')

    expect(await screen.findByRole('heading', { name: 'Inicia sesión' })).toBeInTheDocument()
  })

  it('validates the form before calling the API', async () => {
    const calls = mockApi({ 'GET /auth/me': SIGNED_OUT })
    const { user } = renderRoute('/login')

    await user.click(await screen.findByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Introduce un email válido')).toBeInTheDocument()
    expect(screen.getByText('Introduce tu contraseña')).toBeInTheDocument()
    expect(calls.some((call) => call.path === '/auth/login')).toBe(false)
  })

  it('shows an error for wrong credentials', async () => {
    mockApi({
      'GET /auth/me': SIGNED_OUT,
      'POST /auth/login': { status: 401, body: { detail: 'Invalid email or password' } },
    })
    const { user } = renderRoute('/login')

    await user.type(await screen.findByLabelText('Email'), 'dani@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Email o contraseña incorrectos')).toBeInTheDocument()
  })

  it('asks to wait after too many attempts', async () => {
    mockApi({
      'GET /auth/me': SIGNED_OUT,
      'POST /auth/login': {
        status: 429,
        body: { detail: 'Too many attempts, try again later' },
        headers: { 'Retry-After': '42' },
      },
    })
    const { user } = renderRoute('/login')

    await user.type(await screen.findByLabelText('Email'), 'dani@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByText('Demasiados intentos. Vuelve a probar en 42 segundos.'),
    ).toBeInTheDocument()
  })

  it('signs in and returns to the requested page', async () => {
    let signedIn = false
    const calls = mockApi({
      'GET /auth/me': () => (signedIn ? { body: USER } : SIGNED_OUT),
      'POST /auth/login': () => {
        signedIn = true
        return { status: 204 }
      },
      'GET /routines': { body: [] },
    })
    const { user } = renderRoute('/entrenar')

    await user.type(await screen.findByLabelText('Email'), 'dani@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'correct-horse-battery')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('heading', { name: 'Nuevo entreno' })).toBeInTheDocument()
    expect(calls.find((call) => call.path === '/auth/login')?.body).toEqual({
      email: 'dani@example.com',
      password: 'correct-horse-battery',
    })
  })
})
