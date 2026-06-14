---
name: react-composition-patterns
version: 1.0.0
description: Patrones avanzados de composición en React y Next.js para componentes reutilizables y maintainables. Usa cuando diseñes arquitecturas de componentes, crees design systems, o refactorices componentes complejos.
tags: [react, nextjs, patterns, composition, architecture, components, typescript]
author: garri333
license: MIT
source: https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns
---

# React Composition Patterns

## Cuándo usar esta skill
- Diseñar la arquitectura de un sistema de componentes
- Refactorizar un componente que se está volviendo muy complejo
- Crear componentes flexibles y reutilizables
- Código revisión sobre estructura de componentes React

## Patrones principales

### 1. Compound Components
Componentes que trabajan juntos, compartiendo estado implícitamente.

```tsx
// ✅ Compound Component pattern
interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

function useTabsContext() {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("useTabsContext must be used within Tabs");
  return ctx;
}

function Tabs({ children, defaultTab }: { children: React.ReactNode; defaultTab: string }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

Tabs.List = function TabList({ children }: { children: React.ReactNode }) {
  return <div role="tablist" className="tabs-list">{children}</div>;
};

Tabs.Tab = function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useTabsContext();
  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = function TabPanel({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab } = useTabsContext();
  if (activeTab !== id) return null;
  return <div role="tabpanel">{children}</div>;
};

// Uso:
<Tabs defaultTab="tab1">
  <Tabs.List>
    <Tabs.Tab id="tab1">Tab 1</Tabs.Tab>
    <Tabs.Tab id="tab2">Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="tab1">Contenido 1</Tabs.Panel>
  <Tabs.Panel id="tab2">Contenido 2</Tabs.Panel>
</Tabs>
```

### 2. Render Props
Pasa lógica como prop para máxima flexibilidad de renderizado.

```tsx
// ✅ Render Props
interface DataFetcherProps<T> {
  url: string;
  render: (data: T | null, loading: boolean, error: Error | null) => React.ReactNode;
}

function DataFetcher<T>({ url, render }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return render(data, loading, error);
}

// Uso:
<DataFetcher<User>
  url="/api/user"
  render={(user, loading, error) => {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <UserCard user={user!} />;
  }}
/>
```

### 3. Higher Order Components (HOC)
Envuelve un componente para añadir funcionalidad.

```tsx
// ✅ HOC para autenticación
function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  redirectTo = '/login'
) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();
    const router = useRouter();

    if (loading) return <LoadingScreen />;
    if (!user) {
      router.push(redirectTo);
      return null;
    }

    return <WrappedComponent {...props} />;
  };
}

// ✅ HOC para tracking
function withAnalytics<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  eventName: string
) {
  return function TrackedComponent(props: P) {
    useEffect(() => {
      trackEvent(eventName, { component: WrappedComponent.displayName });
    }, []);
    return <WrappedComponent {...props} />;
  };
}

// Uso combinado:
const ProtectedDashboard = withAuth(withAnalytics(Dashboard, 'dashboard_view'));
```

### 4. Custom Hooks para lógica reutilizable
Separa la lógica del componente.

```tsx
// ✅ Custom hook para formularios
function useForm<T extends Record<string, unknown>>(initialValues: T) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const handleChange = useCallback(
    (field: keyof T) => (value: T[keyof T]) => {
      setValues(prev => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleBlur = useCallback(
    (field: keyof T) => () => {
      setTouched(prev => ({ ...prev, [field]: true }));
    },
    []
  );

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return { values, errors, touched, handleChange, handleBlur, reset, setErrors };
}
```

### 5. Slots Pattern (React)
Pasar componentes como props para máxima flexibilidad de layout.

```tsx
// ✅ Slots pattern
interface CardProps {
  header?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
}

function Card({ header, children, footer, actions }: CardProps) {
  return (
    <div className="card">
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
      {actions && (
        <div className="card-actions">
          {actions}
        </div>
      )}
    </div>
  );
}

// Uso:
<Card
  header={<h2>Título</h2>}
  footer={<p>Fecha: {date}</p>}
  actions={
    <>
      <Button>Cancelar</Button>
      <Button variant="primary">Guardar</Button>
    </>
  }
>
  <p>Contenido del card</p>
</Card>
```

## Next.js — Composición con Server Components

### Server + Client Component boundary
```tsx
// app/page.tsx — Server Component (default)
import { ClientCounter } from './components/ClientCounter';
import { db } from '@/lib/db';

export default async function Page() {
  // Esto corre en el servidor — acceso directo a DB, fs, etc.
  const data = await db.users.findMany();

  return (
    <div>
      <h1>Users ({data.length})</h1>
      {/* Pasar datos serializable del servidor al cliente */}
      <ClientCounter initialCount={data.length} />
      
      {/* Pasar Server Components como children a Client Components */}
      <ClientWrapper>
        <ServerData data={data} />
      </ClientWrapper>
    </div>
  );
}
```

```tsx
// components/ClientWrapper.tsx
'use client';

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children}
    </div>
  );
}
// ✅ children puede ser un Server Component — React lo maneja correctamente
```

### Parallel Routes en Next.js
```
app/
  layout.tsx          — Shell compartido
  @analytics/         — Slot de analytics
    page.tsx
  @team/              — Slot de team members
    page.tsx
  page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <>
      {children}
      <aside>
        {analytics}
        {team}
      </aside>
    </>
  );
}
```

## Anti-patrones a evitar

```tsx
// ❌ Prop drilling excesivo
<App>
  <Page user={user}>
    <Section user={user}>
      <Card user={user}>
        <Avatar user={user} />
      </Card>
    </Section>
  </Page>
</App>

// ✅ Context o composición
const UserContext = createContext<User | null>(null);
// O usar slots/children para "piercear" los niveles

// ❌ Componentes que hacen demasiado
function UserDashboard() {
  // 500 líneas con fetch, state, render, business logic...
}

// ✅ Separar concerns
function UserDashboard() {
  const { user, stats } = useUserDashboard(); // lógica
  return <UserDashboardView user={user} stats={stats} />; // presentación
}

// ❌ Mutar props
function BadComponent({ items }) {
  items.push(newItem); // NO
}

// ✅ Immutable
function GoodComponent({ items }) {
  const newItems = [...items, newItem]; // OK
}
```

## Cuándo usar cada patrón

| Patrón | Cuándo |
|--------|--------|
| Compound Components | Componentes relacionados que comparten estado (Tabs, Accordion, Dropdown) |
| Render Props | Lógica que puede renderizarse de formas muy diferentes |
| HOC | Añadir funcionalidad crosscutting (auth, analytics, error boundary) |
| Custom Hooks | Lógica stateful reutilizable independiente del UI |
| Slots | Layouts flexibles donde el padre controla la estructura |
| Context | Estado global de una sección de la app (user, theme, i18n) |
