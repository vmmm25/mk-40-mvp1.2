---
name: superdesign
version: 1.0.0
description: Guía de diseño frontend de nivel experto para crear interfaces visualmente excepcionales. Usa cuando el usuario quiera un diseño que destaque por encima de lo normal, con atención al detalle de nivel profesional.
tags: [design, ui, frontend, tailwind, animation, typography, color, expert]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# SuperDesign Skill

## Cuándo usar esta skill
- El usuario quiere una interfaz "de nivel", "premium" o "beautiful"
- Diseño de landing pages, aplicaciones SaaS, portfolios
- Cuando el diseño estándar/básico no es suficiente
- Para revisar y elevar la calidad visual de una UI existente

## Principios del SuperDesign

### 1. Espaciado que respira
```
El espaciado define la elegancia. Más espacio = más premium.

Space scale estandard:
Base: 16px (1rem)
xs:   4px   (0.25rem)
sm:   8px   (0.5rem)
md:   16px  (1rem)
lg:   24px  (1.5rem)
xl:   32px  (2rem)
2xl:  48px  (3rem)
3xl:  64px  (4rem)
4xl:  96px  (6rem)

Regla: Si no sabes cuánto espacio poner, dobla tu propuesta inicial.
```

### 2. Tipografía que habla
```css
/* Combinaciones de fuentes que funcionan */

/* Opción A: Moderna y limpia */
heading: 'Inter'    /* Números: 800, 700, 600 */
body:    'Inter'    /* Tamaño: 15-16px, line-height: 1.6-1.7 */

/* Opción B: Editorial y sofisticada */
heading: 'Playfair Display' /* Serif para títulos */
body:    'Source Sans 3'   /* Sans para el cuerpo */

/* Opción C: Técnica y confiable */
heading: 'DM Sans'
body:    'DM Sans'
mono:    'JetBrains Mono'

/* Escala tipográfica con fluid */
:root {
  --text-xs:   clamp(0.75rem,  0.70rem + 0.25vw,  0.875rem);
  --text-sm:   clamp(0.875rem, 0.82rem + 0.28vw,  1rem);
  --text-base: clamp(1rem,     0.95rem + 0.25vw,  1.125rem);
  --text-lg:   clamp(1.125rem, 1.05rem + 0.38vw,  1.375rem);
  --text-xl:   clamp(1.25rem,  1.15rem + 0.50vw,  1.625rem);
  --text-2xl:  clamp(1.5rem,   1.35rem + 0.75vw,  2rem);
  --text-3xl:  clamp(1.875rem, 1.65rem + 1.13vw,  2.625rem);
  --text-4xl:  clamp(2.25rem,  1.95rem + 1.50vw,  3.25rem);
  --text-5xl:  clamp(3rem,     2.55rem + 2.25vw,  4.5rem);
}
```

### 3. Color con propósito y profundidad
```css
/* Sistema de color con 12 pasos (como Radix UI Colors) */
:root {
  /* Primary: Azul */
  --blue-1:  #fafeff;   /* App bg */
  --blue-2:  #f2faff;   /* Subtle bg */
  --blue-3:  #e4f6ff;   /* UI element bg */
  --blue-4:  #cdeeff;   /* Hovered UI element bg */
  --blue-5:  #b5e2ff;   /* Active/Selected UI element bg */
  --blue-6:  #9acffc;   /* Subtle borders */
  --blue-7:  #77b5f8;   /* UI borders */
  --blue-8:  #4890ef;   /* Hovered borders */
  --blue-9:  #2B5CE6;   /* Solid bg MAIN */
  --blue-10: #2452d6;   /* Hovered solid bg */
  --blue-11: #1d3dba;   /* Low-contrast text */
  --blue-12: #162353;   /* High-contrast text */
  
  /* Neutral */
  --gray-1:  #fcfcfc;
  --gray-2:  #f8f8f8;
  --gray-3:  #f3f3f3;
  --gray-4:  #ededed;
  --gray-5:  #e8e8e8;
  --gray-6:  #e2e2e2;
  --gray-7:  #d9d9d9;
  --gray-8:  #c7c7c7;
  --gray-9:  #8d8d8d;
  --gray-10: #838383;
  --gray-11: #646464;
  --gray-12: #202020;
}
```

### 4. Layers y profundidad
```css
/* Sombras que crean profundidad real */
:root {
  /* Sombras suaves (Material-like pero más sutiles) */
  --shadow-xs:  0px 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-sm:  0px 1px 3px rgba(0, 0, 0, 0.08), 0px 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md:  0px 4px 8px rgba(0, 0, 0, 0.06), 0px 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-lg:  0px 12px 24px rgba(0, 0, 0, 0.06), 0px 4px 8px rgba(0, 0, 0, 0.06);
  --shadow-xl:  0px 24px 48px rgba(0, 0, 0, 0.08), 0px 8px 16px rgba(0, 0, 0, 0.06);
  
  /* Sombras con color (para elementos primarios) */
  --shadow-blue: 0px 8px 16px rgba(43, 92, 230, 0.25);
}
```

### 5. Animaciones que se sienten bien
```css
/* Easings que se sienten naturales */
:root {
  --ease-out-expo:   cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Con "bounce" */
  --ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);
}

/* Micro-interacciones */
.button {
  transition: 
    transform 0.1s var(--ease-out-expo),
    background-color 0.15s var(--ease-in-out),
    box-shadow 0.15s var(--ease-in-out);
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.button:active {
  transform: translateY(0px) scale(0.98);
}

/* Entrance animations con Tailwind */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-up {
  animation: fade-up 0.4s var(--ease-out-expo) both;
}

/* Stagger con --delay */
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
```

## Componentes de nivel premium

### Gradient borders
```css
/* Border con gradiente (sin outline, solo pseudo-element) */
.gradient-border {
  position: relative;
  background: white;
  border-radius: 12px;
}

.gradient-border::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 13px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s;
}

.gradient-border:hover::before {
  opacity: 1;
}
```

### Glassmorphism (cuando toca)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 4px 24px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-radius: 16px;
}

/* Dark glassmorphism */
.glass-dark {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Hero section que impacta
```tsx
// Componente Hero de nivel premium
export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Gradient orb background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 -left-1/4 w-1/2 aspect-square bg-blue-400/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 -right-1/4 w-1/2 aspect-square bg-purple-400/20 rounded-full blur-[120px]" />
      </div>
      
      <div className="max-w-5xl mx-auto px-4 py-32 text-center">
        {/* Badge/eyebrow */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-sm font-medium mb-8">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          Nuevo: Feature X ya disponible
        </div>
        
        {/* Headline con gradient */}
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
          Diseño que{' '}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            se nota
          </span>
        </h1>
        
        {/* Subheadline */}
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          La diferencia entre bueno y excepcional está en los detalles.
        </p>
        
        {/* CTA Group */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-[0_8px_16px_rgba(43,92,230,0.25)] hover:shadow-[0_12px_24px_rgba(43,92,230,0.35)] transition-all duration-200 hover:-translate-y-0.5">
            Empezar gratis
          </button>
          <button className="px-8 py-4 text-gray-600 hover:text-gray-900 font-semibold flex items-center gap-2 transition-colors">
            Ver demo
            <span>→</span>
          </button>
        </div>
      </div>
    </section>
  );
}
```

## Checklist de "¿Es nivel SuperDesign?"

```
Tipografía:
□ ¿La jerarquía visual es inmediatamente clara?
□ ¿El line-height del body es ≥ 1.6?
□ ¿Los headings tienen tracking negativo en tamaños grandes?

Espaciado:
□ ¿Hay suficiente espacio entre secciones (mínimo 80-120px)?
□ ¿Los componentes respiran internamente?

Color:
□ ¿El color principal tiene múltiples tonos (no solo uno)?
□ ¿Los grises son realmente grises (o neutros con tinte)?

Interacciones:
□ ¿Todos los elementos interactivos tienen hover state?
□ ¿Los hover states son sutiles (no agresivos)?
□ ¿Las transiciones son ≤ 300ms?

Detalles:
□ ¿Las sombras tienen 2 capas (cercana + difusa)?
□ ¿Los border-radii son consistentes?
□ ¿Las imágenes tienen proporciones definidas (no se distorsionan)?
```

## Referencias
- [Radix UI Colors](https://www.radix-ui.com/colors)  
- [Tailwind UI — componentes premium](https://tailwindui.com/)
- [Shadcn/ui](https://ui.shadcn.com/)
- [Refactoring UI (libro)](https://www.refactoringui.com/)
- [Every Layout](https://every-layout.dev/)
- [Super Designer en clawdbotskills.org](https://clawdbotskills.org/)
