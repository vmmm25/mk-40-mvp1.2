---
name: browser-automation
version: 1.0.0
description: Automatización de navegador headless para scraping, testing y workflows web. Usa cuando necesites automatizar acciones en páginas web, extraer datos, o ejecutar tests end-to-end.
tags: [automation, browser, scraping, testing, playwright, puppeteer, web]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Browser Automation

## Cuándo usar automatización de navegador

✅ **Casos de uso válidos:**
- Web scraping de sitios que no tienen API
- Tests E2E de tu propia aplicación
- Automatizar formularios repetitivos
- Screenshots automáticos para monitorización
- Generar PDFs desde webs

⚠️ **Consideraciones importantes:**
- Respeta el `robots.txt` del sitio
- Añade delays entre requests para no sobrecargar servidores
- Crea este tipo de automatizaciones solo en sitios donde tienes permiso o son públicos

## Playwright (recomendado — 2026)

Playwright es la herramienta estándar. Funciona con Chromium, Firefox y WebKit.

### Setup básico
```bash
npm install playwright
npx playwright install  # Instala los browsers
```

### Estructura básica
```typescript
import { chromium, Browser, Page } from 'playwright';

async function main() {
  const browser: Browser = await chromium.launch({
    headless: true,  // false para ver el browser
  });

  const page: Page = await browser.newPage();

  try {
    await page.goto('https://example.com');
    await page.waitForLoadState('networkidle');

    // Tu lógica aquí

  } finally {
    await browser.close();
  }
}

main().catch(console.error);
```

### Selectores (en orden de preferencia)

```typescript
// 1. Por role (mejor para a11y y estabilidad)
await page.getByRole('button', { name: 'Iniciar sesión' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// 2. Por texto exacto
await page.getByText('Continuar').click();

// 3. Por placeholder
await page.getByPlaceholder('Introduce tu email').fill('...');

// 4. Por test-id (para tus propias apps)
await page.getByTestId('submit-button').click();

// 5. Por CSS solo como último recurso
await page.locator('.btn-primary').click();
```

### Patterns de scraping

```typescript
// Scraping de una lista de elementos
async function scrapeList(page: Page) {
  await page.goto('https://example.com/products');
  await page.waitForSelector('.product-card');

  const products = await page.$$eval('.product-card', cards =>
    cards.map(card => ({
      name: card.querySelector('.name')?.textContent?.trim(),
      price: card.querySelector('.price')?.textContent?.trim(),
      url: card.querySelector('a')?.href,
    }))
  );

  return products;
}

// Scraping paginado
async function scrapeAllPages(url: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const allData = [];

  let currentPage = 1;
  let hasNextPage = true;

  while (hasNextPage) {
    await page.goto(`${url}?page=${currentPage}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000 + Math.random() * 1000); // delay aleatorio

    const data = await page.$$eval('.item', items =>
      items.map(item => ({
        title: item.querySelector('h2')?.textContent?.trim(),
        link: item.querySelector('a')?.href,
      }))
    );

    allData.push(...data);

    const nextButton = await page.$('a[aria-label="Siguiente página"]');
    if (!nextButton) {
      hasNextPage = false;
    } else {
      currentPage++;
    }
  }

  await browser.close();
  return allData;
}
```

### Autenticación

```typescript
// Login con guardado de estado (para no re-loguearse)
async function loginAndSaveState() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('https://example.com/login');
  await page.getByLabel('Email').fill(process.env.EMAIL!);
  await page.getByLabel('Password').fill(process.env.PASSWORD!);
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();
  await page.waitForURL('**/dashboard');

  // Guardar estado de autenticación
  await page.context().storageState({ path: 'auth.json' });
  await browser.close();
}

// Reutilizar el estado guardado
const context = await browser.newContext({
  storageState: 'auth.json'
});
const page = await context.newPage();
// Ya está logueado
```

### Tests E2E con Playwright Test

```typescript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Checkout flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/products');
  });

  test('usuario puede completar compra', async ({ page }) => {
    // Añadir al carrito
    await page.getByRole('button', { name: 'Añadir al carrito' }).first().click();
    await expect(page.getByRole('status')).toContainText('Añadido al carrito');

    // Ir al checkout
    await page.getByRole('link', { name: 'Carrito (1)' }).click();
    await expect(page).toHaveURL('/cart');

    // Completar formulario
    await page.getByLabel('Nombre').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByRole('button', { name: 'Confirmar pedido' }).click();

    // Verificar confirmación
    await expect(page).toHaveURL('/order-confirmation');
    await expect(page.getByRole('heading')).toContainText('Pedido confirmado');
  });
});
```

## Puppeteer (alternativa más ligera)

```typescript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();

// Bloquear recursos innecesarios para ir más rápido
await page.setRequestInterception(true);
page.on('request', (req) => {
  if (['image', 'stylesheet', 'font'].includes(req.resourceType())) {
    req.abort();
  } else {
    req.continue();
  }
});

await page.goto('https://example.com');
const content = await page.evaluate(() => document.body.innerText);
await browser.close();
```

## Anti-detección (cuando un sitio bloquea bots)

```typescript
// playwright-extra + stealth plugin
import { chromium } from 'playwright-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

chromium.use(StealthPlugin());

const browser = await chromium.launch({ headless: true });
// El browser ahora parece más humano

// También: añadir User-Agent realista
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  viewport: { width: 1280, height: 720 },
  locale: 'es-ES',
});
```

## Exportar datos scrapeados

```typescript
import * as fs from 'fs';

// JSON
fs.writeFileSync('output.json', JSON.stringify(data, null, 2));

// CSV
const csv = [
  Object.keys(data[0]).join(','),  // header
  ...data.map(row => Object.values(row).join(','))
].join('\n');
fs.writeFileSync('output.csv', csv);
```

## Referencias
- [Playwright Docs](https://playwright.dev/)
- [Puppeteer Docs](https://pptr.dev/)
- [Playwright Test](https://playwright.dev/docs/test-intro)
- [Agent Browser (Clawdbot)](https://clawdbotskills.org/)
