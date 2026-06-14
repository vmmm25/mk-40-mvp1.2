---
name: webapp-testing-playwright
version: 1.0.0
description: >
  End-to-end web application testing with Playwright. Covers page navigation, element selection
  (CSS, XPath, role-based locators), assertions, screenshot and video capture, network interception,
  API mocking, multi-browser testing (Chromium, Firefox, WebKit), mobile emulation, visual regression
  testing, accessibility testing, CI/CD integration, test fixtures, and the Page Object pattern.
tags:
  - testing
  - playwright
  - e2e
  - end-to-end
  - browser-testing
  - web-testing
  - visual-regression
  - accessibility
  - ci-cd
  - page-objects
  - api-mocking
  - multi-browser
author: garri333
license: MIT
source: anthropics/skills (webapp-testing)
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# webapp-testing-playwright

End-to-end web application testing with Playwright. Write, run, and maintain robust browser tests across Chromium, Firefox, and WebKit with built-in support for screenshots, video, network interception, API mocking, visual regression, and accessibility auditing.

---

## When to Activate

Activate this skill when the user:

- Wants to **write end-to-end tests** for a web application
- Needs to **set up Playwright** in a project (install, config, first test)
- Asks to **test across multiple browsers** (Chromium, Firefox, WebKit)
- Needs to **capture screenshots or video** of test runs
- Wants to **intercept network requests** or mock API responses
- Needs **mobile emulation** (viewport, device, touch events)
- Asks about **visual regression testing** (pixel comparison)
- Wants to run **accessibility audits** (axe-core integration)
- Needs to **integrate Playwright into CI/CD** (GitHub Actions, GitLab CI)
- Asks about the **Page Object Model** or test fixture patterns
- Wants to **debug flaky tests** or improve test reliability
- Uses keywords: `playwright`, `e2e`, `browser test`, `end-to-end`, `visual regression`, `accessibility test`

---

## Step-by-Step Instructions

### 1. Project Setup

```bash
# Initialize Playwright in an existing project
npm init playwright@latest

# Or install manually
npm install -D @playwright/test
npx playwright install          # Download browser binaries

# Verify installation
npx playwright --version
```

**playwright.config.ts** — Production-ready configuration:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,         // Fail CI if .only() left in
  retries: process.env.CI ? 2 : 0,      // Retry flaky tests in CI
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',            // Capture trace on retry
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit',   use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

---

### 2. Element Selection Strategies

Use the most resilient locator for each situation, in order of preference:

```
LOCATOR STRATEGY PRIORITY
══════════════════════════════════════════════════════════════
1. Role-based (best)    page.getByRole('button', { name: 'Submit' })
2. Label                page.getByLabel('Email address')
3. Placeholder          page.getByPlaceholder('Search...')
4. Text                 page.getByText('Welcome back')
5. Test ID              page.getByTestId('login-form')
6. CSS selector         page.locator('.card >> .title')
7. XPath (last resort)  page.locator('xpath=//div[@class="card"]')
══════════════════════════════════════════════════════════════
```

**Examples:**

```typescript
// Role-based — preferred for interactive elements
await page.getByRole('button', { name: 'Sign in' }).click();
await page.getByRole('link', { name: 'Dashboard' }).click();
await page.getByRole('textbox', { name: 'Username' }).fill('admin');
await page.getByRole('combobox').selectOption('Option A');
await page.getByRole('checkbox', { name: 'Remember me' }).check();

// Label — great for form fields
await page.getByLabel('Password').fill('secret123');

// Test ID — when semantic locators aren't possible
await page.getByTestId('user-avatar').click();

// Chained locators — scope to a container
const card = page.locator('[data-testid="product-card"]').first();
await card.getByRole('button', { name: 'Add to cart' }).click();

// Filtering
await page
  .getByRole('listitem')
  .filter({ hasText: 'Premium Plan' })
  .getByRole('button', { name: 'Select' })
  .click();
```

---

### 3. Core Assertions

```typescript
import { test, expect } from '@playwright/test';

test('user login flow', async ({ page }) => {
  await page.goto('/login');

  // Visibility
  await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();

  // Fill and submit
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // URL assertion
  await expect(page).toHaveURL(/\/dashboard/);

  // Title assertion
  await expect(page).toHaveTitle(/Dashboard/);

  // Element text
  await expect(page.getByTestId('welcome-msg')).toHaveText('Welcome, User!');

  // Element count
  await expect(page.getByRole('listitem')).toHaveCount(5);

  // CSS property
  await expect(page.getByTestId('status')).toHaveCSS('color', 'rgb(0, 128, 0)');

  // Attribute
  await expect(page.getByRole('link', { name: 'Profile' }))
    .toHaveAttribute('href', '/profile');

  // Not visible (element removed or hidden)
  await expect(page.getByText('Loading...')).not.toBeVisible();
});
```

---

### 4. Screenshot & Video Capture

```typescript
// Full-page screenshot
await page.screenshot({ path: 'screenshots/full-page.png', fullPage: true });

// Element screenshot
await page.getByTestId('chart').screenshot({ path: 'screenshots/chart.png' });

// Visual comparison (snapshot testing)
await expect(page).toHaveScreenshot('dashboard.png', {
  maxDiffPixelRatio: 0.01,       // Allow 1% pixel difference
  threshold: 0.2,                // Color difference threshold
  animations: 'disabled',        // Freeze animations
});

// Update snapshots: npx playwright test --update-snapshots
```

Video is configured globally in `playwright.config.ts` via `use.video`:

```typescript
use: {
  video: 'retain-on-failure',   // 'on' | 'off' | 'retain-on-failure' | 'on-first-retry'
}
```

---

### 5. Network Interception & API Mocking

```typescript
test('mock API response', async ({ page }) => {
  // Intercept API and return mock data
  await page.route('**/api/products', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Widget', price: 9.99 },
        { id: 2, name: 'Gadget', price: 19.99 },
      ]),
    });
  });

  await page.goto('/products');
  await expect(page.getByText('Widget')).toBeVisible();
  await expect(page.getByText('Gadget')).toBeVisible();
});

test('simulate network error', async ({ page }) => {
  await page.route('**/api/data', (route) => route.abort('connectionrefused'));
  await page.goto('/data');
  await expect(page.getByText('Failed to load data')).toBeVisible();
});

test('modify request headers', async ({ page }) => {
  await page.route('**/*', async (route) => {
    await route.continue({
      headers: { ...route.request().headers(), 'X-Custom-Header': 'test' },
    });
  });
});

test('wait for specific API call', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/users');
  await page.getByRole('button', { name: 'Load Users' }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
});
```

---

### 6. Mobile Emulation

```typescript
import { devices } from '@playwright/test';

// In config — use predefined device profiles
projects: [
  {
    name: 'mobile-portrait',
    use: {
      ...devices['iPhone 13'],
      locale: 'en-US',
      geolocation: { longitude: -122.4194, latitude: 37.7749 },
      permissions: ['geolocation'],
    },
  },
  {
    name: 'tablet-landscape',
    use: {
      ...devices['iPad Pro 11 landscape'],
    },
  },
]

// In test — custom viewport
test('responsive layout', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await expect(page.getByTestId('mobile-menu')).toBeVisible();
  await expect(page.getByTestId('desktop-nav')).not.toBeVisible();
});
```

---

### 7. Accessibility Testing

```typescript
import AxeBuilder from '@axe-core/playwright';

test('accessibility audit — home page', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .exclude('#third-party-widget')    // Exclude elements you don't control
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});

test('accessibility — specific component', async ({ page }) => {
  await page.goto('/forms');

  const results = await new AxeBuilder({ page })
    .include('#registration-form')
    .analyze();

  expect(results.violations).toEqual([]);
});
```

Install: `npm install -D @axe-core/playwright`

---

### 8. Page Object Model

```typescript
// pages/LoginPage.ts
import { type Locator, type Page, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test('successful login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await expect(page).toHaveURL(/\/dashboard/);
});

test('invalid credentials', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('wrong@example.com', 'wrong');
  await loginPage.expectError('Invalid email or password');
});
```

---

### 9. Test Fixtures

```typescript
import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  authenticatedPage: DashboardPage;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await use(loginPage);
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  authenticatedPage: async ({ page }, use) => {
    // Setup: log in via API (faster than UI)
    const response = await page.request.post('/api/auth/login', {
      data: { email: 'test@example.com', password: 'test123' },
    });
    const { token } = await response.json();
    await page.context().addCookies([{
      name: 'auth_token', value: token, domain: 'localhost', path: '/',
    }]);

    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await use(dashboard);
  },
});

export { expect };
```

---

### 10. Retry Strategies & Flaky Test Prevention

```typescript
// Per-test retry
test('flaky network test', async ({ page }) => {
  test.info().annotations.push({ type: 'flaky', description: 'Network dependent' });
  // ...
});

// Retry configuration in playwright.config.ts
retries: process.env.CI ? 2 : 0,

// Explicit waits — prefer auto-waiting over manual waits
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page.getByText('Success')).toBeVisible({ timeout: 15_000 });

// Wait for network idle
await page.goto('/', { waitUntil: 'networkidle' });

// Wait for specific condition
await page.waitForFunction(() => document.fonts.ready);
```

---

### 11. CI/CD Integration

**GitHub Actions:**

```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

**GitLab CI:**

```yaml
playwright:
  image: mcr.microsoft.com/playwright:v1.50.0-noble
  stage: test
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 7 days
```

---

## Best Practices

1. **Prefer role-based locators** — they mirror how users interact with the page
2. **Use auto-waiting** — Playwright auto-waits for actionability; avoid `page.waitForTimeout()`
3. **Isolate tests** — each test should be independent; use `beforeEach` for setup
4. **Mock external APIs** — don't depend on third-party services in E2E tests
5. **Test user journeys** — focus on complete workflows, not individual elements
6. **Keep tests fast** — authenticate via API, not UI, when auth isn't being tested
7. **Use trace viewer** for debugging failures: `npx playwright show-trace trace.zip`
8. **Version-control snapshots** — commit visual regression baselines to the repo
9. **Run in CI with retries** — network-dependent tests may need 1-2 retries
10. **Tag and filter tests** — use `test.describe` and `--grep` to run subsets

---

## Examples

### Complete E2E Test Suite for a Todo App

```typescript
import { test, expect } from '@playwright/test';

test.describe('Todo Application', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/todos');
  });

  test('add a new todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Buy groceries');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByTestId('todo-list')).toContainText('Buy groceries');
    await expect(page.getByTestId('todo-count')).toHaveText('1 item left');
  });

  test('complete a todo', async ({ page }) => {
    // Setup
    await page.getByPlaceholder('What needs to be done?').fill('Read book');
    await page.getByPlaceholder('What needs to be done?').press('Enter');

    // Act
    await page.getByRole('checkbox', { name: 'Read book' }).check();

    // Assert
    await expect(page.getByTestId('todo-count')).toHaveText('0 items left');
  });

  test('filter completed todos', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Task 1');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('Task 2');
    await page.getByPlaceholder('What needs to be done?').press('Enter');

    await page.getByRole('checkbox', { name: 'Task 1' }).check();
    await page.getByRole('link', { name: 'Completed' }).click();

    await expect(page.getByTestId('todo-list')).toContainText('Task 1');
    await expect(page.getByTestId('todo-list')).not.toContainText('Task 2');
  });
});
```

---

## Related Skills

- `testing-anti-patterns` — avoid common E2E testing mistakes
- `tdd-bdd-patterns` — integrate Playwright into BDD workflows
- `systematic-debugging` — debug failing Playwright tests
