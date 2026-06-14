---
name: vercel-platform
version: 1.0.0
description: Domina la plataforma Vercel más allá del deploy básico — Edge Functions, Middleware, KV/Blob/Postgres, Speed Insights, ISR, Feature Flags y monorepos. Usa cuando necesites aprovechar el stack completo de Vercel para una app de producción.
tags: [vercel, edge-functions, middleware, isr, kv, blob, postgres, speed-insights, analytics, monorepo]
author: garri333
license: MIT
source: https://skills.sh/
---

# Vercel Platform Skill

> Para el flujo básico de deploy, ver `vercel-deploy`. Esta skill cubre las **features avanzadas de la plataforma**.

## Edge Runtime vs Node.js Runtime

```typescript
// Edge Function — corre en la red de Vercel (latencia <1ms worldwide)
// Limitaciones: no tiene acceso a fs, APIs nativas de Node, max 1MB bundle

// app/api/edge-hello/route.ts
export const runtime = "edge";  // ← Clave

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get("name") ?? "World";

  return new Response(
    JSON.stringify({ message: `Hello, ${name}!` }),
    {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, s-maxage=60",
      },
    }
  );
}

// Node.js Runtime — potencia total, pero latencia más alta
export async function GET(request: Request) {
  // Aquí puedes usar fs, child_process, etc.
  const data = await heavyProcessing();
  return Response.json(data);
}
```

## Middleware — interceptar requests

```typescript
// middleware.ts (en la raíz del proyecto)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // 1. Auth guard
  const token = request.cookies.get("auth-token")?.value;
  if (pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 2. A/B Testing con cookies persistentes
  if (pathname === "/") {
    const bucket = request.cookies.get("ab-bucket")?.value ?? (
      Math.random() < 0.5 ? "control" : "variant-a"
    );

    const response = NextResponse.next();
    response.cookies.set("ab-bucket", bucket, { maxAge: 60 * 60 * 24 * 30 });
    response.headers.set("x-ab-bucket", bucket);
    return response;
  }

  // 3. Geolocalización (metadata de Vercel)
  const country = request.geo?.country ?? "US";
  if (pathname === "/pricing") {
    // Redirigir a pricing regional
    if (country === "ES") {
      return NextResponse.rewrite(new URL("/pricing/eu", request.url));
    }
  }

  // 4. Rate limiting básico (por IP con Edge KV)
  // Ver sección Vercel KV más abajo

  return NextResponse.next();
}

// ¿A qué rutas aplica el middleware?
export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
```

## Vercel KV (Redis en el Edge)

```typescript
// npm install @vercel/kv
import { kv } from "@vercel/kv";

// Ejemplo: Rate limiting en middleware
export async function middleware(request: NextRequest) {
  const ip = request.ip ?? "anonymous";
  const key = `rate-limit:${ip}`;

  const count = await kv.incr(key);
  if (count === 1) {
    // Primera request: establecer TTL de 1 minuto
    await kv.expire(key, 60);
  }

  if (count > 100) {
    return new Response("Too Many Requests", { status: 429 });
  }

  return NextResponse.next();
}

// En una API route: caché de sesiones
export async function POST(request: Request) {
  const body = await request.json();
  const sessionId = crypto.randomUUID();

  await kv.set(`session:${sessionId}`, body, { ex: 3600 }); // TTL 1h
  
  return Response.json({ sessionId });
}

// Leer sesión
export async function GET(request: Request) {
  const sessionId = new URL(request.url).searchParams.get("id");
  const session = await kv.get(`session:${sessionId}`);
  
  return Response.json(session);
}

// Operaciones avanzadas
await kv.lpush("queue:jobs", JSON.stringify({ type: "email", to: "..." }));
await kv.zadd("leaderboard", { score: 1500, member: "user:123" });
const topUsers = await kv.zrange("leaderboard", 0, 9, { rev: true, withScores: true });
```

## Vercel Blob (almacenamiento de archivos)

```typescript
// npm install @vercel/blob
import { put, del, list, head } from "@vercel/blob";

// Subir archivo (desde API route)
export async function POST(request: Request) {
  const form = await request.formData();
  const file = form.get("file") as File;

  const blob = await put(`uploads/${file.name}`, file, {
    access: "public",    // "public" o "private"
    addRandomSuffix: true, // Evitar colisiones de nombre
  });

  // blob.url → URL pública para compartir
  // blob.downloadUrl → URL con header de descarga
  return Response.json({ url: blob.url });
}

// Listar archivos
const { blobs } = await list({ prefix: "uploads/" });

// Eliminar
await del(blobUrl);

// Verificar existencia
const blobInfo = await head(blobUrl);
// blobInfo.size, blobInfo.contentType, blobInfo.uploadedAt
```

## Vercel Postgres

```typescript
// npm install @vercel/postgres
import { sql } from "@vercel/postgres";

// Query directa
const { rows } = await sql`
  SELECT id, email, name 
  FROM users 
  WHERE created_at > NOW() - INTERVAL '7 days'
`;

// Con parámetros (previene SQL injection)
const userId = 123;
const { rows } = await sql`
  SELECT * FROM orders WHERE user_id = ${userId}
`;

// En migraciones (usar @vercel/postgres con drizzle o prisma)
// Con Drizzle ORM:
import { drizzle } from "drizzle-orm/vercel-postgres";
import { sql as sqlClient } from "@vercel/postgres";

export const db = drizzle(sqlClient);
```

## Incremental Static Regeneration (ISR)

```typescript
// app/posts/[slug]/page.tsx
import { notFound } from "next/navigation";

// ISR: regenerar cada 60 segundos
export const revalidate = 60;

// O dinámicamente por demanda
export async function generateStaticParams() {
  const posts = await fetchAllPosts();
  return posts.map(post => ({ slug: post.slug }));
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug);
  if (!post) notFound();
  
  return <PostContent post={post} />;
}

// Revalidar on-demand desde una webhook
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from "next/cache";

export async function POST(request: Request) {
  const { secret, slug, tag } = await request.json();
  
  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  
  if (slug) revalidatePath(`/posts/${slug}`);
  if (tag) revalidateTag(tag);
  
  return Response.json({ revalidated: true });
}

// En el fetch: etiquetar para revalidación
const post = await fetch(`/api/posts/${slug}`, {
  next: { tags: [`post-${slug}`] }
});
```

## Speed Insights y Web Analytics

```typescript
// app/layout.tsx
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Analytics } from "@vercel/analytics/react";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />  {/* Core Web Vitals automáticos */}
        <Analytics />      {/* Pageviews y custom events */}
      </body>
    </html>
  );
}

// Registrar eventos custom con Analytics
import { track } from "@vercel/analytics";

// En un componente
function SignupButton() {
  return (
    <button onClick={() => {
      track("signup_clicked", { plan: "pro", source: "hero" });
    }}>
      Sign up
    </button>
  );
}
```

## Feature Flags con Edge Config

```typescript
// npm install @vercel/edge-config
import { get, getAll } from "@vercel/edge-config";

// En middleware — leer sin latencia (Edge Config = distribución global)
export async function middleware(request: NextRequest) {
  const isMaintenanceMode = await get("maintenance_mode");
  
  if (isMaintenanceMode && !request.nextUrl.pathname.startsWith("/maintenance")) {
    return NextResponse.redirect(new URL("/maintenance", request.url));
  }
}

// Flags de features
const flags = await getAll(["new_checkout", "beta_dashboard", "ai_search"]);

if (flags.new_checkout) {
  // Mostrar nuevo checkout
}
```

## Monorepos en Vercel

```json
// vercel.json en la raíz del monorepo
{
  "projects": [
    {
      "name": "web",
      "directory": "apps/web",
      "framework": "nextjs"
    },
    {
      "name": "dashboard",
      "directory": "apps/dashboard",
      "framework": "nextjs"
    }
  ]
}
```

```bash
# Configurar proyecto en monorepo con CLI
vercel link --project=web
vercel env pull .env.local

# Deploy solo el app afectado (Turbo + Vercel Remote Cache)
npx turbo deploy --filter=web
```

## Configuración avanzada de vercel.json

```json
{
  "framework": "nextjs",
  "regions": ["iad1", "fra1"],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 60,
      "memory": 512
    },
    "app/api/ai/**/*.ts": {
      "maxDuration": 300
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" }
      ]
    }
  ],
  "rewrites": [
    { "source": "/blog/(.*)", "destination": "https://my-cms.vercel.app/blog/$1" }
  ],
  "redirects": [
    { "source": "/old-page", "destination": "/new-page", "permanent": true }
  ]
}
```

## Variables de entorno por entornos

```bash
# Ver variables actuales
vercel env ls

# Añadir variable a producción
vercel env add DATABASE_URL production

# Añadir a todos los entornos
vercel env add NEXT_PUBLIC_API_URL production preview development

# Descargar variables locales desde Vercel
vercel env pull .env.local

# Variables de sistema disponibles en runtime:
# VERCEL_ENV — "production" | "preview" | "development"
# VERCEL_GIT_COMMIT_SHA — SHA del commit actual
# VERCEL_URL — URL del deployment actual
# VERCEL_BRANCH_URL — URL de la rama
# VERCEL_PROJECT_PRODUCTION_URL — URL de producción
```

## Referencias
- [Vercel Edge Runtime](https://vercel.com/docs/concepts/functions/edge-functions/edge-runtime) — APIs disponibles
- [Vercel KV docs](https://vercel.com/docs/storage/vercel-kv) — Redis en el Edge
- [Vercel Blob docs](https://vercel.com/docs/storage/vercel-blob) — File storage
- [Vercel Postgres docs](https://vercel.com/docs/storage/vercel-postgres) — Serverless Postgres
- [Edge Config docs](https://vercel.com/docs/storage/edge-config) — Feature flags
- [ISR en Next.js](https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating) — Estrategias de cache
