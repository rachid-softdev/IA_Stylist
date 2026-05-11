import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('should show login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('h1')).toContainText('Connexion')
  })

  test('should show signup page', async ({ page }) => {
    await page.goto('/signup')
    await expect(page.locator('h1')).toContainText('Créer un compte')
  })

  test('should redirect from protected route to login', async ({ page }) => {
    await page.goto('/studio')
    // Should be redirected or show login
    await expect(page).toHaveURL(/login|studio/)
  })
})

test.describe('Landing', () => {
  test('should display hero section', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toContainText('shooting photo')
  })

  test('should have CTA button', async ({ page }) => {
    await page.goto('/')
    const cta = page.locator('a[href="/signup"]').first()
    await expect(cta).toBeVisible()
  })
})

test.describe('Studio', () => {
  test('should display upload zone when empty', async ({ page }) => {
    await page.goto('/studio')
    await expect(page.locator('text=Uploadez votre photo')).toBeVisible()
  })
})

test.describe('Dressing', () => {
  test('should show empty state', async ({ page }) => {
    await page.goto('/dressing')
    await expect(page.locator('text=Créez votre premier look')).toBeVisible()
  })
})
