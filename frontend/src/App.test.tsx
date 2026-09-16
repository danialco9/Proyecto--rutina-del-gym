import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from '@/App'

describe('App', () => {
  it('shows the main heading and every section', () => {
    render(<App />)

    expect(screen.getByRole('heading', { level: 1, name: 'Tu entrenamiento, medido' })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 2 }).map((heading) => heading.textContent)).toEqual([
      'Entrenar',
      'Rutinas',
      'Medidas',
      'Progreso',
    ])
  })
})
