---
name: web-design-guidelines
version: 1.0.0
description: Guía de mejores prácticas para interfaces web: accesibilidad, UX, rendimiento y código limpio. Usa cuando revises UI, audites diseño o implementes interfaces.
tags: [ui, ux, web, accessibility, design, css, frontend, html]
author: garri333
license: MIT
source: https://skills.sh/vercel-labs/agent-skills/web-design-guidelines
---

# Web Design Guidelines

## Usar esta skill cuando
- El usuario pide "revisa mi UI"
- Se pide auditar accesibilidad o UX
- Se pide revisar código CSS/HTML
- Se necesita comprobar si el diseño sigue best practices

## Principios de diseño web

### Visual Hierarchy
1. **Contraste de tamaño** — Los elementos más importantes son más grandes
2. **Contraste de color** — Los CTAs deben destacar visualmente
3. **Espacio en blanco** — Respiración visual, no es espacio vacío
4. **Alineación** — Todo debe tener una razón para estar donde está
5. **Repetición** — Consistencia crea confianza y aprendizaje

### Layout Patterns

```css
/* Container con max-width centrado */
.container {
  max-width: 1200px;
  margin-inline: auto;
  padding-inline: 1rem;
}

/* Grid responsive sin media queries */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: 1.5rem;
}

/* Stack vertical con gap homogéneo */
.stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
```

### Typography Scale
```css
:root {
  /* Escala tipográfica perfecta (ratio 1.25) */
  --step--1: clamp(0.80rem, 0.77rem + 0.13vw, 0.88rem);
  --step-0:  clamp(1.00rem, 0.96rem + 0.16vw, 1.10rem); /* Base: 16-17.6px */
  --step-1:  clamp(1.25rem, 1.20rem + 0.20vw, 1.38rem);
  --step-2:  clamp(1.56rem, 1.50rem + 0.25vw, 1.72rem);
  --step-3:  clamp(1.95rem, 1.88rem + 0.32vw, 2.16rem);
  --step-4:  clamp(2.44rem, 2.34rem + 0.40vw, 2.70rem);
  --step-5:  clamp(3.05rem, 2.93rem + 0.50vw, 3.37rem);
}
```

## Accesibilidad web

### Checklist WAI-WCAG 2.1 AA

#### Visión
- [ ] Contraste texto normal: ≥ 4.5:1
- [ ] Contraste texto grande (>18pt): ≥ 3:1
- [ ] Contraste componentes UI: ≥ 3:1
- [ ] El contenido es legible al 200% de zoom
- [ ] No solo color para transmitir información

#### Motor
- [ ] Toda funcionalidad accesible con teclado
- [ ] No hay trampa de foco (focus trap solo en modales apropiados)
- [ ] Focus visible y claramente distinguible
- [ ] Touch targets ≥ 44x44px (móvil)

#### Comprensión
- [ ] `lang` attribute en `<html>`
- [ ] Etiquetas de formularios visibles (no solo placeholders)
- [ ] Mensajes de error descriptivos y útiles
- [ ] Tiempo de sesión con aviso extendible

#### Robustez
- [ ] HTML válido y semántico
- [ ] ARIA usado correctamente (no sobre-usado)
- [ ] Compatible con principales screen readers

### HTML Semántico
```html
<!-- Estructura de página correcta -->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Título descriptivo - Marca</title>
</head>
<body>
  <a href="#main" class="skip-link">Saltar al contenido principal</a>
  
  <header>
    <nav aria-label="Navegación principal">
      <ul>
        <li><a href="/">Inicio</a></li>
        <li><a href="/about" aria-current="page">Sobre nosotros</a></li>
      </ul>
    </nav>
  </header>
  
  <main id="main">
    <h1>Título principal de la página</h1>
    <!-- Contenido -->
  </main>
  
  <aside aria-label="Contenido relacionado">
    <!-- Sidebar -->
  </aside>
  
  <footer>
    <!-- Footer -->
  </footer>
</body>
</html>
```

### Formularios accesibles
```html
<!-- ✅ Correcto -->
<div class="form-group">
  <label for="email">
    Email
    <span aria-hidden="true">*</span>
    <span class="sr-only">(requerido)</span>
  </label>
  <input
    type="email"
    id="email"
    name="email"
    autocomplete="email"
    required
    aria-describedby="email-error"
  >
  <span id="email-error" role="alert" class="error" hidden>
    Introduce un email válido
  </span>
</div>

<!-- ✅ Botón de submit con loading state -->
<button type="submit" aria-busy="true" disabled>
  <span class="spinner" aria-hidden="true"></span>
  <span>Enviando...</span>
</button>
```

## Performance web

### Core Web Vitals objetivos
```
LCP (Largest Contentful Paint): < 2.5s
INP (Interaction to Next Paint): < 200ms
CLS (Cumulative Layout Shift): < 0.1
```

### Critical rendering path
```html
<!-- 1. CSS crítico inline (above-the-fold) -->
<style>
  /* Styles para lo que se ve sin scroll */
  header, .hero { ... }
</style>

<!-- 2. Resto de CSS con preload -->
<link rel="preload" href="/styles/main.css" as="style">
<link rel="stylesheet" href="/styles/main.css" media="print" onload="this.media='all'">

<!-- 3. Fuentes con preconnect -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

### Imágenes optimizadas
```html
<!-- Responsive images -->
<img
  src="imagen-800.webp"
  srcset="imagen-400.webp 400w, imagen-800.webp 800w, imagen-1200.webp 1200w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="Descripción descriptiva del contenido"
  width="800"
  height="450"
  loading="lazy"
  decoding="async"
>

<!-- Imagen de hero (no lazy - está above the fold) -->
<img src="hero.webp" alt="..." width="1200" height="600" fetchpriority="high">
```

## Dark mode

```css
/* Sistema de color para ambos modos */
:root {
  --color-bg: #ffffff;
  --color-text: #111827;
  --color-surface: #f9fafb;
  --color-border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f172a;
    --color-text: #f8fafc;
    --color-surface: #1e293b;
    --color-border: #334155;
  }
}

/* O con clase manual */
[data-theme="dark"] {
  --color-bg: #0f172a;
  /* ... */
}
```

## CSS Modern Patterns

```css
/* Centering */
.center {
  display: grid;
  place-items: center;
}

/* Responsive sin media queries */
.sidebar-layout {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.sidebar-layout > :first-child {
  flex-basis: 300px;
  flex-grow: 1;
}
.sidebar-layout > :last-child {
  flex-basis: 0;
  flex-grow: 999;
  min-width: min(50%, 500px);
}

/* Smooth scrolling respetuoso */
@media (prefers-reduced-motion: no-preference) {
  html {
    scroll-behavior: smooth;
  }
}

/* Aspect ratio */
.video-wrapper {
  aspect-ratio: 16/9;
}
```

## Audit checklist rápida

Cuando revisas una interfaz:

**Visual:**
- [ ] Jerarquía visual clara (sé qué es lo más importante)
- [ ] Consistencia de espaciado
- [ ] Colores consistentes con suficiente contraste

**Funcional:**
- [ ] Funciona con solo teclado
- [ ] Mobile-friendly (mínimo 375px de ancho)
- [ ] Estados de carga y error explícitos

**Performance:**
- [ ] Imágenes con dimensiones explícitas (sin CLS)
- [ ] Imágenes fuera de viewport en lazy loading
- [ ] Sin web fonts bloqueantes del render

## Referencias
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [web.dev - Core Web Vitals](https://web.dev/vitals/)
- [Vercel Web Design Guidelines](https://github.com/vercel-labs/agent-skills)
- [Every Layout](https://every-layout.dev/)
- [SmolCSS](https://smolcss.dev/)
