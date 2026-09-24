import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { mockApi } from '@/test/mock-api'
import { renderRoute } from '@/test/render'

describe('Password reset', () => {
  it('asks for a link from the login page', async () => {
    const calls = mockApi({
      'GET /auth/me': { status: 401 },
      'POST /auth/password-reset': { status: 204 },
    })
    const { user } = renderRoute('/login')

    await user.click(await screen.findByRole('link', { name: '¿Olvidaste tu contraseña?' }))
    await user.type(await screen.findByLabelText('Email'), 'nuevo@gymtracker.dev')
    await user.click(screen.getByRole('button', { name: 'Enviar enlace' }))

    expect(await screen.findByRole('heading', { name: 'Revisa tu correo' })).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('nuevo@gymtracker.dev')
    expect(calls.find((call) => call.path === '/auth/password-reset')?.body).toEqual({
      email: 'nuevo@gymtracker.dev',
    })
  })

  it('sets the new password with the token from the link and goes to the login page', async () => {
    const calls = mockApi({
      'GET /auth/me': { status: 401 },
      'POST /auth/password-reset/confirm': { status: 204 },
    })
    const { user, router } = renderRoute('/restablecer#token=abc123')

    await user.type(await screen.findByLabelText('Contraseña nueva'), 'otra-contraseña')
    await user.type(screen.getByLabelText('Repite la contraseña'), 'otra-contrasena')
    await user.click(screen.getByRole('button', { name: 'Guardar contraseña' }))
    expect(await screen.findByText('Las contraseñas no coinciden')).toBeInTheDocument()
    expect(calls.some((call) => call.path === '/auth/password-reset/confirm')).toBe(false)

    await user.clear(screen.getByLabelText('Repite la contraseña'))
    await user.type(screen.getByLabelText('Repite la contraseña'), 'otra-contraseña')
    await user.click(screen.getByRole('button', { name: 'Guardar contraseña' }))

    expect(await screen.findByRole('button', { name: 'Entrar' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')
    expect(calls.find((call) => call.path === '/auth/password-reset/confirm')?.body).toEqual({
      token: 'abc123',
      password: 'otra-contraseña',
    })
  })

  it('offers a new link when this one has expired or was used', async () => {
    mockApi({
      'POST /auth/password-reset/confirm': { status: 400, body: { detail: 'Invalid or expired link' } },
    })
    const { user } = renderRoute('/restablecer#token=old')

    await user.type(await screen.findByLabelText('Contraseña nueva'), 'otra-contraseña')
    await user.type(screen.getByLabelText('Repite la contraseña'), 'otra-contraseña')
    await user.click(screen.getByRole('button', { name: 'Guardar contraseña' }))

    expect(await screen.findByText(/ha caducado o ya se usó/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Pedir un enlace nuevo' })).toHaveAttribute('href', '/recuperar')
  })

  it('explains a link that lost its token', async () => {
    renderRoute('/restablecer')

    expect(await screen.findByRole('heading', { name: 'Enlace no válido' })).toBeInTheDocument()
  })
})
