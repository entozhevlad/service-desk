import { test, expect } from '@playwright/test'

test('visits the app root url', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Mini Service Desk')
  await expect(page.getByRole('button', { name: '+ Create ticket' })).toBeVisible()
  await expect(page.getByText('Filters: no filters')).toBeVisible()
})
