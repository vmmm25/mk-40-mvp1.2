---
name: git-conventional-commits
version: 1.0.0
description: Formato Conventional Commits para mensajes git. Usa cuando hagas commits, generes changelogs o trabajes con versionado semántico.
tags: [git, commits, versioning, changelog, devops, ci-cd]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Conventional Commits

## Formato

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Tipos

| Tipo | Descripción | Versión semver |
|------|-------------|----------------|
| `feat` | Nueva funcionalidad | MINOR (1.x.0) |
| `fix` | Corrección de bug | PATCH (1.0.x) |
| `docs` | Cambios solo en documentación | ninguna |
| `style` | Formato, espacios (no lógica) | ninguna |
| `refactor` | Refactoring (no feat ni fix) | ninguna |
| `perf` | Mejora de performance | PATCH |
| `test` | Añadir o corregir tests | ninguna |
| `build` | Build system o dependencias externas | ninguna |
| `ci` | Configuración de CI | ninguna |
| `chore` | Tareas de mantenimiento | ninguna |
| `revert` | Revierte un commit anterior | depende |

### Breaking changes
Para cambios que rompen compatibilidad (`MAJOR` en semver):
```bash
feat!: cambiar API de autenticación a JWT

BREAKING CHANGE: El endpoint /login ahora devuelve un JWT en lugar de una cookie.
Los clientes deben actualizar para usar el header Authorization: Bearer <token>
```

## Ejemplos

```bash
# Nueva funcionalidad
git commit -m "feat(auth): añadir autenticación con Google OAuth"

# Bug fix
git commit -m "fix(api): corregir error 500 cuando el email contiene mayúsculas"

# Con scope y cuerpo detallado
git commit -m "feat(payments): integrar Stripe para pagos recurrentes

- Añade webhook handler para eventos de Stripe
- Implementa lógica de reintentos para pagos fallidos
- Actualiza la UI del panel de facturación"

# Documentación
git commit -m "docs: actualizar README con instrucciones de instalación en Windows"

# Refactoring
git commit -m "refactor(database): extraer lógica de conexión a módulo separado"

# Breaking change
git commit -m "feat!: migrar de REST a GraphQL

BREAKING CHANGE: Todos los endpoints REST han sido eliminados.
Ver MIGRATION.md para guía de migración a la nueva API GraphQL."

# Chore
git commit -m "chore(deps): actualizar dependencias de seguridad (ESLint, Next.js)"

# CI
git commit -m "ci: añadir step de análisis de vulnerabilidades con Snyk"
```

## Scopes comunes

Define los scopes relevantes para tu proyecto:

```
auth        — Autenticación y autorización
api         — API endpoints
ui          — Componentes de interfaz
database    — Modelos y migraciones
config      — Configuración
deps        — Dependencias
tests       — Suite de tests
docs        — Documentación
ci          — CI/CD pipeline
deploy      — Despliegue
security    — Parches de seguridad
performance — Optimizaciones de performance
```

## Beneficios de seguir este formato

1. **Changelogs automáticos** — `standard-version`, `semantic-release`, `changesets`
2. **Versionado semántico** — Determinar el siguiente número de versión automáticamente
3. **Historial legible** — `git log --oneline` es útil de verdad
4. **CI/CD condicional** — Disparar deploys solo cuando hay feat/fix
5. **Code review más fácil** — El reviewer sabe el impacto antes de leer el código

## Configurar en tu proyecto

### commitlint + husky
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional husky

# commitlint.config.js
module.exports = { extends: ['@commitlint/config-conventional'] };

# .husky/commit-msg
npx --no -- commitlint --edit ${1}
```

### commitizen (CLI interactivo)
```bash
npm install --save-dev commitizen cz-conventional-changelog
npx commitizen init cz-conventional-changelog --save-dev --save-exact

# Luego usar: git cz (en lugar de git commit)
```

## Generar changelog automático

```bash
# Con standard-version
npm install --save-dev standard-version
npx standard-version  # bumps version + genera CHANGELOG.md + crea tag git

# Con semantic-release (CI/CD automático)
npx semantic-release
```

## Referencias
- [Conventional Commits Spec](https://www.conventionalcommits.org/)
- [semantic-release](https://github.com/semantic-release/semantic-release)
- [commitlint](https://commitlint.js.org/)
