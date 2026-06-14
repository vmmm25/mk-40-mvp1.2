---
name: react-best-practices
version: 1.0.0
description: Patrones de performance y mejores prácticas de React y Next.js según Vercel Engineering. Usa cuando escribas, revises o refactorices código React/Next.js.
tags: [react, nextjs, javascript, typescript, performance, frontend]
author: garri333
license: MIT
source: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
---

# React & Next.js Best Practices

## Reglas fundamentales

### Componentes
1. **Un componente, una responsabilidad** — Si necesitas comentar "hace X y Y", sepáralo
2. **Menos de 200 líneas por componente** — Más → refactoriza
3. **Props explícitas** — Nunca spread `{...props}` sin control
4. **Keys estables** — Nunca usar índice de array como key si la lista puede reordenarse

### Estado
```tsx
// ✅ Estado local para UI ephemeral
const [isOpen, setIsOpen] = useState(false);

// ✅ Estado derivado en lugar de duplicar
const fullName = `${firstName} ${lastName}`; // no state

// ❌ Nunca sincronizar state con props
// ✅ Usa useEffect solo para efectos externos (fetch, subscription, DOM)
```

### Performance

```tsx
// useMemo: para cálculos costosos
const sortedList = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// useCallback: para funciones pasadas como props a componentes memorizados
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);

// memo: para componentes que re-renderizan innecesariamente
export const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{data}</div>;
});
```

⚠️ **No optimices prematuramente** — Usa estas técnicas solo cuando React DevTools muestre problemas reales.

## Next.js App Router

### Server vs Client Components

```
✅ Server Components (por defecto):
- Fetch de datos
- Acceso a base de datos
- Variables de entorno
- Componentes que no necesitan interactividad

✅ Client Components ('use client'):
- useState, useEffect, useReducer
- Event handlers (onClick, onChange)
- Browser-only APIs (window, localStorage)
- Librerías que usan hooks
```

### Data fetching

```tsx
// ✅ Fetch en Server Component — automáticamente deduplicado y cacheado
async function Page() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 } // revalidar cada hora
  });
  return <div>{data}</div>;
}

// ✅ Streaming con Suspense
<Suspense fallback={<Loading />}>
  <SlowComponent />
</Suspense>

// ✅ Parallel fetching
const [user, posts] = await Promise.all([
  fetchUser(id),
  fetchPosts(id)
]);
```

### Layouts y páginas

```
app/
├── layout.tsx          ← Root layout (HTML, body)
├── page.tsx            ← Página /
├── loading.tsx         ← Loading UI con Suspense
├── error.tsx           ← Error boundary
├── not-found.tsx       ← 404
└── (marketing)/        ← Route group (sin segmento de URL)
    ├── layout.tsx
    └── about/
        └── page.tsx    ← Página /about
```

### Metadata

```tsx
// app/layout.tsx o app/page.tsx
export const metadata: Metadata = {
  title: { template: '%s | Mi App', default: 'Mi App' },
  description: 'Descripción de la app',
  openGraph: { ... },
};

// metadata dinámica
export async function generateMetadata({ params }): Promise<Metadata> {
  const product = await fetchProduct(params.id);
  return { title: product.name };
}
```

## Patrones de composición

### Compound components
```tsx
// Para componentes con multiple sub-partes relacionadas
<Select>
  <Select.Trigger>Selecciona...</Select.Trigger>
  <Select.Content>
    <Select.Item value="a">Opción A</Select.Item>
    <Select.Item value="b">Opción B</Select.Item>
  </Select.Content>
</Select>
```

### Render props / children as function
```tsx
// Para lógica reutilizable con UI flexible
<DataFetcher url="/api/users">
  {({ data, loading, error }) => (
    loading ? <Spinner /> : <UserList users={data} />
  )}
</DataFetcher>
```

### Custom hooks para lógica reutilizable
```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = useCallback((value: T) => {
    setValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  }, [key]);

  return [value, setStoredValue] as const;
}
```

## TypeScript en React

```tsx
// Props con tipos explícitos
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  disabled?: boolean;
}

// Forwardref con tipos
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, ...props }, ref) => (
    <div>
      <label>{label}</label>
      <input ref={ref} {...props} />
      {error && <span>{error}</span>}
    </div>
  )
);
Input.displayName = 'Input';

// Generic components
function List<T extends { id: string }>({
  items,
  renderItem,
}: {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}) {
  return <ul>{items.map(item => <li key={item.id}>{renderItem(item)}</li>)}</ul>;
}
```

## Testing

```tsx
// @testing-library/react — siempre testear comportamiento, no implementación
import { render, screen, userEvent } from '@testing-library/react';

test('muestra mensaje de error cuando el form es inválido', async () => {
  render(<LoginForm />);

  await userEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));

  expect(screen.getByRole('alert')).toHaveTextContent('Email es requerido');
});
```

## Errores comunes a evitar

| ❌ Evitar | ✅ Hacer |
|-----------|----------|
| `useEffect` para datos iniciales en Client Components | Server Components + fetch directo |
| `useState` para datos del servidor | React Query / SWR / Server Actions |
| Fetch en cada componente que lo necesite | Fetch en el nivel superior, pasar como props o usar context |
| Manipular DOM directamente | refs + apis de React |
| `any` en TypeScript | Tipos explícitos o `unknown` |
| Index como key en listas dinámicas | ID único del elemento |

## Referencias
- [React Docs](https://react.dev/)
- [Next.js Docs](https://nextjs.org/docs)
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [React DevTools](https://react.dev/learn/react-developer-tools)
