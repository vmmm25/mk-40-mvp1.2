---
name: vercel-deploy
version: 1.0.0
description: Desplegar y gestionar aplicaciones en Vercel con el CLI y la API. Usa cuando necesites hacer deploy, gestionar dominios, variables de entorno, o automatizar despliegues de proyectos Next.js, React, o cualquier framework soportado.
tags: [vercel, deployment, hosting, nextjs, frontend, backend, serverless, cli]
author: garri333
license: MIT
source: https://skills.sh/vercel-labs/agent-skills/vercel-deploy
---

# Vercel Deploy Skill

## Cuándo usar esta skill
- Hacer deploy de una aplicación a Vercel
- Configurar variables de entorno en Vercel
- Gestionar dominios y DNS en Vercel
- Consultar logs de producción
- Automatizar despliegues en CI/CD

## Setup inicial

### Instalar Vercel CLI
```bash
npm install -g vercel
# O con pnpm
pnpm add -g vercel

# Login
vercel login
# Abre el browser para autenticarse — o usar token:
vercel login --token $VERCEL_TOKEN
```

### Enlazar proyecto existente
```bash
cd mi-proyecto
vercel link
# Elige tu equipo/cuenta y el proyecto existente
```

## Comandos principales

### Deploy

```bash
# Deploy a producción
vercel --prod

# Deploy a preview (para revisión antes de producción)
vercel

# Deploy sin confirmar prompts
vercel --prod --yes

# Deploy con variables de entorno
vercel --prod -e DATABASE_URL=postgres://...

# Ver URL del último deploy
vercel inspect $(vercel ls --prod | head -1 | awk '{print $1}')
```

### Variables de entorno

```bash
# Añadir variable de entorno
vercel env add DATABASE_URL
# Luego pega el valor y selecciona los entornos (Production/Preview/Development)

# Añadir sin interacción
echo "postgres://user:pass@host/db" | vercel env add DATABASE_URL production

# Listar variables
vercel env ls

# Eliminar variable
vercel env rm DATABASE_URL production

# Descargar .env.local para desarrollo
vercel env pull .env.local
```

### Dominios

```bash
# Añadir dominio custom
vercel domains add midominio.com

# Listar dominios
vercel domains ls

# Asignar dominio a proyecto
vercel alias set mi-deployment.vercel.app midominio.com

# Ver configuración DNS recomendada
vercel domains inspect midominio.com
```

### Logs y monitorización

```bash
# Ver logs en tiempo real
vercel logs midominio.com --follow

# Ver logs de las últimas N horas
vercel logs midominio.com --since 2h

# Ver lista de deployments
vercel ls

# Rollback al deployment anterior
vercel rollback

# Rollback a un deployment específico
vercel rollback dpl_xxxxx
```

## Configuración — vercel.json

```json
{
  "version": 2,
  "name": "mi-proyecto",
  
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  
  "routes": [
    {
      "src": "/api/(.*)",
      "headers": {
        "cache-control": "no-store"
      },
      "continue": true
    },
    {
      "src": "/blog/(.*)",
      "headers": {
        "cache-control": "s-maxage=60, stale-while-revalidate=3600"
      },
      "continue": true
    }
  ],
  
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ],
  
  "rewrites": [
    {
      "source": "/api/proxy/:path*",
      "destination": "https://api.externa.com/:path*"
    }
  ],
  
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ],
  
  "regions": ["mad1"],
  
  "functions": {
    "api/**/*.ts": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

## Next.js en Vercel — configuraciones

### next.config.js optimizado para Vercel
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Imágenes desde dominios externos
  images: {
    remotePatterns: [
      { hostname: 'cdn.ejemplo.com' },
      { hostname: '*.cloudinary.com' },
    ],
  },
  
  // Variables de entorno públicas
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  
  // Compresión y optimizaciones
  compress: true,
  poweredByHeader: false,
  
  // ISR fallback a no-store si la data cambia mucho
  experimental: {
    staleTimes: {
      dynamic: 30,     // segundos para páginas dinámicas
      static: 3600,    // para páginas estáticas
    },
  },
};

export default nextConfig;
```

### Cache headers en Next.js App Router
```tsx
// Con ISR (Incremental Static Regeneration)
export const revalidate = 3600; // Revalidar cada hora

// Con fetch
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 }  // Revalidar cada 60 segundos
});

// Sin caché (siempre fresco)
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store'
});
```

## Automatización con GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]
  pull_request:

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Vercel CLI
        run: npm install -g vercel
      
      - name: Pull Vercel Environment Information
        run: vercel pull --yes --environment=${{ github.ref == 'refs/heads/main' && 'production' || 'preview' }} --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Build Project
        run: vercel build ${{ github.ref == 'refs/heads/main' && '--prod' || '' }} --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Deploy to Vercel
        id: deploy
        run: |
          URL=$(vercel deploy --prebuilt ${{ github.ref == 'refs/heads/main' && '--prod' || '' }} --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$URL" >> $GITHUB_OUTPUT
      
      - name: Comment PR with preview URL
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview: ${{ steps.deploy.outputs.url }}'
            })
```

## Obtener tokens y IDs necesarios

```bash
# Token de Vercel
vercel token create ci-deploy

# Project ID y Org ID
vercel project ls  # Ver proyectos
cat .vercel/project.json  # Después de vercel link
# {
#   "orgId": "team_xxxx",
#   "projectId": "prj_xxxx"
# }
```

## Vercel API (REST)

```bash
BASE="https://api.vercel.com"
TOKEN="tu-vercel-token"

# Listar deployments
curl "$BASE/v6/deployments?projectId=prj_xxx" \
  -H "Authorization: Bearer $TOKEN"

# Crear deployment via API
curl -X POST "$BASE/v13/deployments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project", "gitSource": {"type": "github", "repo": "user/repo", "ref": "main"}}'

# Obtener logs de un deployment
curl "$BASE/v2/deployments/dpl_xxx/events" \
  -H "Authorization: Bearer $TOKEN"
```

## Referencias
- [Vercel CLI reference](https://vercel.com/docs/cli)
- [vercel.json configuration](https://vercel.com/docs/projects/project-configuration)
- [Vercel REST API](https://vercel.com/docs/rest-api)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
