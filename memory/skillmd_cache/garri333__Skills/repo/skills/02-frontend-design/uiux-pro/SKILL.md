---
name: uiux-pro
version: 1.0.0
description: Sistema de diseño profesional con design tokens, APIs de componentes, integración Figma-to-code y accesibilidad WCAG. Usa cuando construyas un design system desde cero o necesites llevar el UI de un proyecto al nivel de productos premium.
tags: [uiux, design-system, design-tokens, storybook, figma, tailwind, accessibility, react, vue, svelte]
author: garri333
license: MIT
source: https://skills.sh/
---

# UI/UX Pro Skill

## Cuándo usar esta skill

- Construir un design system completo para un equipo
- Paso de Figma a código de alta fidelidad
- Auditar y mejorar accesibilidad de un producto existente
- Crear una librería de componentes reutilizables
- Establecer tokens de diseño que funcionen en múltiples frameworks

## Design Tokens — el sistema base

```css
/* tokens.css — fuente de verdad del design system */
:root {
  /* ─── Colors ──────────────────────────────────── */
  --color-brand-50: oklch(97% 0.02 250);
  --color-brand-100: oklch(93% 0.05 250);
  --color-brand-200: oklch(85% 0.10 250);
  --color-brand-300: oklch(75% 0.15 250);
  --color-brand-400: oklch(65% 0.18 250);
  --color-brand-500: oklch(55% 0.20 250);   /* Primary */
  --color-brand-600: oklch(45% 0.20 250);
  --color-brand-700: oklch(35% 0.18 250);
  --color-brand-800: oklch(25% 0.15 250);
  --color-brand-900: oklch(15% 0.10 250);

  /* Semantic tokens (referencian escala) */
  --color-bg: var(--color-brand-50);
  --color-surface: white;
  --color-primary: var(--color-brand-500);
  --color-primary-hover: var(--color-brand-600);
  --color-text: oklch(15% 0.02 250);
  --color-text-muted: oklch(45% 0.04 250);
  --color-border: oklch(88% 0.02 250);

  /* ─── Typography ──────────────────────────────── */
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-mono: "Fira Code", "JetBrains Mono", monospace;

  /* Escala modular (ratio 1.25 = Major Third) */
  --text-xs:   0.64rem;   /* 10.2px */
  --text-sm:   0.80rem;   /* 12.8px */
  --text-base: 1.00rem;   /* 16px */
  --text-lg:   1.25rem;   /* 20px */
  --text-xl:   1.56rem;   /* 25px */
  --text-2xl:  1.95rem;   /* 31.2px */
  --text-3xl:  2.44rem;   /* 39px */
  --text-4xl:  3.05rem;   /* 48.8px */

  /* Line heights */
  --leading-tight:  1.25;
  --leading-normal: 1.5;
  --leading-loose:  1.75;

  /* ─── Spacing (4px grid) ──────────────────────── */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.50rem;   /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1.00rem;   /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.50rem;   /* 24px */
  --space-8: 2.00rem;   /* 32px */
  --space-10: 2.50rem;  /* 40px */
  --space-12: 3.00rem;  /* 48px */
  --space-16: 4.00rem;  /* 64px */
  --space-20: 5.00rem;  /* 80px */
  --space-24: 6.00rem;  /* 96px */

  /* ─── Border Radius ───────────────────────────── */
  --radius-sm: 0.25rem;    /* 4px */
  --radius-md: 0.50rem;    /* 8px */
  --radius-lg: 0.75rem;    /* 12px */
  --radius-xl: 1.00rem;    /* 16px */
  --radius-2xl: 1.50rem;   /* 24px */
  --radius-full: 9999px;

  /* ─── Shadows ─────────────────────────────────── */
  --shadow-sm: 0 1px 2px oklch(0% 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px oklch(0% 0 0 / 0.07), 0 2px 4px -2px oklch(0% 0 0 / 0.05);
  --shadow-lg: 0 10px 15px -3px oklch(0% 0 0 / 0.08), 0 4px 6px -4px oklch(0% 0 0 / 0.06);
  --shadow-xl: 0 20px 25px -5px oklch(0% 0 0 / 0.10), 0 8px 10px -6px oklch(0% 0 0 / 0.07);
  --shadow-colored: 0 8px 24px -4px var(--color-primary, oklch(55% 0.20 250) / 0.25);

  /* ─── Transitions ─────────────────────────────── */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.27, 1.55);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* ─── Z-Index scale ───────────────────────────── */
  --z-base: 0;
  --z-raised: 10;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-toast: 500;
  --z-tooltip: 600;
}

/* Dark mode (usando prefers-color-scheme O clase .dark) */
@media (prefers-color-scheme: dark), .dark {
  :root {
    --color-bg: oklch(12% 0.02 250);
    --color-surface: oklch(18% 0.02 250);
    --color-text: oklch(95% 0.01 250);
    --color-text-muted: oklch(65% 0.03 250);
    --color-border: oklch(28% 0.03 250);
  }
}
```

## API de componentes — patrones profesionales

### Patrón Polymorphic (componente que cambia su elemento HTML)
```tsx
// Button.tsx — polymorphic con TypeScript
import { ComponentPropsWithoutRef, ElementType, ReactNode } from "react";

type ButtonProps<T extends ElementType = "button"> = {
  as?: T;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
} & ComponentPropsWithoutRef<T>;

export function Button<T extends ElementType = "button">({
  as,
  variant = "primary",
  size = "md",
  loading = false,
  leftIcon,
  rightIcon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps<T>) {
  const Component = as ?? "button";

  const variantClasses = {
    primary: "bg-[--color-primary] text-white hover:bg-[--color-primary-hover]",
    secondary: "bg-[--color-surface] border border-[--color-border] hover:bg-gray-50",
    ghost: "hover:bg-gray-100",
    danger: "bg-red-500 text-white hover:bg-red-600",
  };

  const sizeClasses = {
    sm: "h-8 px-3 text-sm gap-1.5",
    md: "h-10 px-4 text-base gap-2",
    lg: "h-12 px-6 text-lg gap-2.5",
  };

  return (
    <Component
      className={[
        "inline-flex items-center justify-center font-medium rounded-[--radius-md]",
        "transition-all duration-[--duration-fast] ease-[--ease-smooth]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--color-primary] focus-visible:ring-offset-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].filter(Boolean).join(" ")}
      disabled={disabled ?? loading}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <span className="animate-spin size-4 border-2 border-current border-t-transparent rounded-full" aria-hidden="true" />
      ) : leftIcon}
      <span>{children}</span>
      {!loading && rightIcon}
    </Component>
  );
}

// Uso:
// <Button>Click me</Button>
// <Button as="a" href="/docs" variant="secondary">Docs</Button>
// <Button loading>Guardando...</Button>
// <Button leftIcon={<PlusIcon />} size="sm">Nuevo</Button>
```

### Patrón Compound Components (para componentes complejos)
```tsx
// Card compound component
import { createContext, useContext, HTMLAttributes, ReactNode } from "react";

const CardContext = createContext<{ variant: "default" | "outline" | "elevated" }>({
  variant: "default",
});

function Card({
  variant = "default",
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement> & { variant?: "default" | "outline" | "elevated" }) {
  const variantClasses = {
    default: "bg-[--color-surface] border border-[--color-border]",
    outline: "bg-transparent border-2 border-[--color-primary]",
    elevated: "bg-[--color-surface] shadow-[--shadow-lg]",
  };

  return (
    <CardContext.Provider value={{ variant }}>
      <div
        className={`rounded-[--radius-xl] overflow-hidden ${variantClasses[variant]} ${className ?? ""}`}
        {...props}
      >
        {children}
      </div>
    </CardContext.Provider>
  );
}

Card.Header = function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`px-6 py-4 border-b border-[--color-border] ${className ?? ""}`}
      {...props}
    />
  );
};

Card.Body = function CardBody({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`px-6 py-5 ${className ?? ""}`} {...props} />;
};

Card.Footer = function CardFooter({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`px-6 py-4 border-t border-[--color-border] bg-gray-50 ${className ?? ""}`}
      {...props}
    />
  );
};

export { Card };

// Uso:
// <Card variant="elevated">
//   <Card.Header><h2>Título</h2></Card.Header>
//   <Card.Body>Contenido</Card.Body>
//   <Card.Footer><Button>Acción</Button></Card.Footer>
// </Card>
```

## Figma-to-code workflow

```
1. En Figma:
   - Inspeccionar → Dev Mode (Ctrl+Shift+D)
   - Copiar variables de diseño → mapear a tu tokens.css
   - Exportar assets: SVG para iconos, WebP para imágenes

2. Plugins recomendados de Figma:
   - "Tokens Studio" — exportar design tokens en JSON
   - "Export to Codegen" — generar código React/Tailwind
   - "Figma to Code" — HTML/CSS básico desde componentes

3. Mapeo de tokens (tokens.json → tokens.css):
   # Con Style Dictionary
   npm install -g style-dictionary
   style-dictionary build --config sd.config.json

4. Verificar fidelidad:
   - Screenshot del Figma + captura del web en misma resolución
   - Comparar spacing, tipografía, colores con DevTools
```

## Accesibilidad WCAG 2.1 AA — checklist en código

```tsx
// Patrones de accesibilidad críticos

// 1. Nombre accesible para elementos interactivos
<button aria-label="Cerrar modal">
  <XIcon aria-hidden="true" />
</button>

// 2. Estado de error en formularios
<div>
  <label htmlFor="email">Email *</label>
  <input
    id="email"
    type="email"
    aria-describedby={error ? "email-error" : undefined}
    aria-invalid={!!error}
  />
  {error && (
    <p id="email-error" role="alert" className="text-red-600 text-sm">
      {error}
    </p>
  )}
</div>

// 3. Foco visible siempre
// En CSS global:
// :focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
// :focus:not(:focus-visible) { outline: none; }

// 4. Región live para notificaciones
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {notification}
</div>

// 5. Trap de foco en modales
import { useEffect, useRef } from "react";

function Modal({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) {
  const modalRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!isOpen) return;
    
    const modal = modalRef.current;
    const focusable = modal?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstEl = focusable?.[0];
    const lastEl = focusable?.[focusable.length - 1];
    
    firstEl?.focus();
    
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== "Tab") return;
      
      if (e.shiftKey && document.activeElement === firstEl) {
        e.preventDefault();
        lastEl?.focus();
      } else if (!e.shiftKey && document.activeElement === lastEl) {
        e.preventDefault();
        firstEl?.focus();
      }
    }
    
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);
  
  if (!isOpen) return null;
  
  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {children}
    </div>
  );
}
```

## Storybook — documentación de componentes

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "UI/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: { type: "select" },
      options: ["primary", "secondary", "ghost", "danger"],
    },
    size: {
      control: { type: "select" },
      options: ["sm", "md", "lg"],
    },
    loading: { control: "boolean" },
    disabled: { control: "boolean" },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    children: "Click me",
    variant: "primary",
    size: "md",
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-3 flex-wrap">
      {(["primary", "secondary", "ghost", "danger"] as const).map((v) => (
        <Button key={v} variant={v}>{v}</Button>
      ))}
    </div>
  ),
};
```

## Checklist de calidad UX/UI

```
LAYOUT
□ Grid consistente (4px o 8px)
□ Espaciado coherente entre secciones
□ Alineación correcta (texto, iconos, elementos)
□ Max-width establecido para lectura (60-75ch para texto)

TIPOGRAFÍA
□ Jerarquía clara (H1 > H2 > H3 > body)
□ Contraste mínimo 4.5:1 para texto normal
□ Contraste mínimo 3:1 para texto grande (>18px o 14px bold)
□ Interlineado readable (1.4-1.6 para body)

INTERACCIÓN
□ Hover states en todos los elementos clickables
□ Focus visible en todos los elementos focusables
□ Feedback inmediato en acciones (loading, success, error)
□ Transiciones suaves (150-250ms)

ACCESIBILIDAD
□ Todos los imgs tienen alt text descriptivo
□ Labels asociados a inputs
□ Errores anunciados con role="alert"
□ Compatibilidad con navegación por teclado
□ Probado con lector de pantalla (VoiceOver / NVDA)

RESPONSIVE
□ Mobile-first: diseñado para 375px primero
□ Breakpoints: 375 → 768 → 1024 → 1280 → 1440
□ Táctil: targets mínimo 44×44px
□ Sin overflow horizontal en ningún breakpoint
```

## Referencias
- [Radix UI](https://www.radix-ui.com/) — Primitivos accesibles sin estilos
- [shadcn/ui](https://ui.shadcn.com/) — Componentes React con Radix + Tailwind
- [Tokens Studio](https://tokens.studio/) — Design tokens en Figma
- [Style Dictionary](https://amzn.github.io/style-dictionary/) — Build tokens para múltiples plataformas
- [Accessible Colors](https://accessible-colors.com/) — Verificar contraste WCAG
- [Storybook](https://storybook.js.org/) — Documentación interactiva de componentes
