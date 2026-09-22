import { expect, test } from '@playwright/test'

test('logs the body weight of the day and shows it in the history', async ({ page }) => {
  await page.goto('/medidas')

  await expect(page.getByRole('heading', { name: 'Medidas' })).toBeVisible()
  await page.getByLabel('Peso (kg)').fill('78')
  await page.getByRole('button', { name: 'Guardar medida' }).click()

  await expect(page.getByText('Medida guardada')).toBeVisible()

  const history = page.getByRole('list').filter({ hasText: '78 kg' })
  await expect(history.getByText('78 kg')).toBeVisible()
  // The day already has an entry, so the form switches from creating to editing it.
  await expect(page.getByRole('heading', { name: 'Editar medida' })).toBeVisible()
})
