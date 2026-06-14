---
name: frontend-design
version: 1.0.0
description: Guía completa de diseño UI/UX, accesibilidad y mejores prácticas para interfaces web. Usa cuando estés creando, revisando o auditando cualquier interfaz web.
tags: [ui, ux, design, accessibility, web, frontend, css, html]
author: garri333
license: MIT
source: https://skills.sh/anthropics/skills/frontend-design
---

# Frontend Design Guidelines

## Principios fundamentales

1. **Mobile-first** — Diseña primero para móvil, luego escala a desktop
2. **Accessibility by default** — WCAG 2.1 AA es el mínimo, no un extra
3. **Performance matters** — Si tarda más de 3 segundos, el usuario se va
4. **Consistencia** — Usa sistemas de diseño, no estilos ad-hoc
5. **Progressive enhancement** — Funciona sin JS, mejora con JS

## Layout y Spacing

### Espaciado
- Usa escala de 4px o 8px (múltiplos de 4 o 8 para márgenes/padding)
- Espacio en blanco es un elemento de diseño, no un desperdicio
- Agrupa elementos relacionados (principio Gestalt: proximidad)

### Grid
- CSS Grid para layouts 2D (filas + columnas)
- Flexbox para layouts 1D (una fila o una columna)
- Container queries donde sea posible (más preciso que media queries)

### Responsive breakpoints (Tailwind defaults)
```
sm:  640px   — Teléfonos grandes
md:  768px   — Tablets
lg:  1024px  — Laptops pequeños
xl:  1280px  — Desktops
2xl: 1536px  — Pantallas grandes
```

## Tipografía

- **Máximo 2-3 fuentes** por proyecto (1 para texto, 1 para títulos, opcional 1 para código)
- **Line height:** 1.5 para texto corrido, 1.2-1.3 para títulos
- **Tamaño mínimo:** 16px para texto corrido (14px absoluto mínimo)
- **Contraste mínimo:** 4.5:1 para texto normal, 3:1 para texto grande (WCAG AA)
- **Escala tipográfica:** Usa escala modular (1.25x o 1.333x)

```css
/* Escala modular 1.25x */
--text-xs:   0.64rem;   /* 10.24px */
--text-sm:   0.8rem;    /* 12.8px  */
--text-base: 1rem;      /* 16px    */
--text-lg:   1.25rem;   /* 20px    */
--text-xl:   1.5625rem; /* 25px    */
--text-2xl:  1.953rem;  /* 31.25px */
--text-3xl:  2.441rem;  /* 39px    */
```

## Color

### Sistema de color
- Define **design tokens** para colores (no hardcodear valores hex directamente)
- **Primary** (acción principal), **Secondary** (acción secundaria), **Neutral** (texto y fondos), **Semantic** (error, warning, success, info)
- Prueba con modo oscuro desde el principio

### Accesibilidad de color
- Nunca uses color como único indicador (añade icono, texto, o patrón)
- Herramientas de verificación: contrast.tools, Stark, APCA

```css
/* Ejemplo de design tokens */
:root {
  --color-primary-500: #3B82F6;
  --color-primary-600: #2563EB;
  --color-text-primary: #111827;
  --color-text-secondary: #6B7280;
  --color-bg-primary: #FFFFFF;
  --color-error: #EF4444;
  --color-success: #10B981;
}
```

## Componentes

### Botones
```
Size:    sm (32px), md (40px), lg (48px)
Variant: primary, secondary, ghost, destructive
State:   default, hover, focus, active, disabled, loading
```
- **Focus visible siempre** — Outline visible para usuarios de teclado
- **Touch target mínimo:** 44x44px (WCAG 2.5.5)
- Estado `loading` con spinner + texto "Cargando..." para mejor UX

### Formularios
- **Label siempre visible** (no solo placeholder)
- **Mensajes de error** debajo del campo, en rojo, con icono
- **Validación en blur** (no en tiempo real, salvo para contraseñas)
- **Autofocus** en el primer campo del formulario principal

### Modales y overlays
- `role="dialog"` + `aria-modal="true"` + `aria-labelledby`
- Trampa de foco (focus trap) dentro del modal
- Cerrar con Escape
- Click fuera del modal para cerrar (opcional pero esperable)
- Scroll bloqueado en el body cuando está abierto

## Accesibilidad (a11y)

### Checklist básica
- [ ] Todas las imágenes tienen `alt` (vacío si son decorativas)
- [ ] Encabezados en orden lógico (H1 > H2 > H3, sin saltar niveles)
- [ ] Contraste mínimo 4.5:1 para texto normal
- [ ] Navegable completamente con teclado (Tab, Enter, Escape, flechas)
- [ ] `lang` correcto en el `<html>`
- [ ] Sin `tabindex` positivos (solo 0 o -1)
- [ ] Links descriptivos (no "click aquí" o "leer más")
- [ ] ARIA solo cuando HTML semántico no es suficiente

### Semántica HTML
```html
<!-- ✅ Correcto -->
<nav aria-label="Navegación principal">
<main>
<article>
<section aria-labelledby="section-title">
<button type="button">

<!-- ❌ Evitar -->
<div class="nav">
<div class="main">
<div onclick="...">
```

## Performance

- **Core Web Vitals targets:**
  - LCP < 2.5s (Largest Contentful Paint)
  - FID < 100ms / INP < 200ms (interaction delay)
  - CLS < 0.1 (Cumulative Layout Shift)

- **Imágenes:** WebP/AVIF, lazy loading, `srcset` para responsive, dimensiones explícitas
- **Fonts:** `font-display: swap`, preload de fuentes críticas, subset de caracteres
- **CSS:** Critical CSS inline, resto en `<link>` diferido
- **JS:** Code splitting, lazy load de rutas, no bloquear el thread principal

## Patrones comunes

### Skeleton loading
Preferible a spinners para contenido que conoce su forma:
```html
<div class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2"></div>
</div>
```

### Error states
Siempre mostrar tres cosas: qué salió mal, por qué, qué puede hacer el usuario.

### Empty states
No mostrar páginas en blanco — muestra ilustración + texto descriptivo + CTA.

## Herramientas recomendadas

| Herramienta | Para qué |
|-------------|----------|
| Figma | Diseño y prototipado |
| Storybook | Documentar componentes |
| Chromatic | Visual regression testing |
| Lighthouse | Auditoría de performance y a11y |
| axe DevTools | Testing de accesibilidad |
| contrast.tools | Comprobar ratios de contraste |

## Referencias
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/)
- [Vercel Web Design Guidelines](https://github.com/vercel-labs/agent-skills)
- [Inclusive Components](https://inclusive-components.design/)
- [refactoring.ui](https://www.refactoringui.com/)
