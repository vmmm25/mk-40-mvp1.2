---
name: github-cli
version: 1.0.0
description: Interfaz especializada con GitHub usando el CLI gh. Usa cuando trabajas con issues, PRs, CI/CD runs, o necesitas interactuar con GitHub desde la terminal.
tags: [github, git, cli, devops, pr, issues, ci-cd, automation]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# GitHub CLI (gh)

## Setup

```bash
# Instalar
winget install GitHub.cli          # Windows
brew install gh                    # macOS
sudo apt install gh                # Ubuntu/Debian

# Autenticar
gh auth login
```

## Issues

```bash
# Listar issues
gh issue list                                    # Issues abiertos
gh issue list --state closed                     # Issues cerrados
gh issue list --label bug --assignee @me         # Filtrar
gh issue list --json number,title,state          # Como JSON

# Ver issue
gh issue view 42
gh issue view 42 --web                           # Abrir en browser

# Crear issue
gh issue create \
  --title "Bug: JWT expiry not refreshing" \
  --body "Descripción del problema..." \
  --label bug \
  --assignee @me

# Cerrar / reabrir
gh issue close 42
gh issue reopen 42

# Comentar
gh issue comment 42 --body "He reproducido el bug, investigando..."
```

## Pull Requests

```bash
# Listar PRs
gh pr list
gh pr list --state merged
gh pr list --author @me

# Ver PR
gh pr view 15
gh pr view 15 --web

# Crear PR
gh pr create \
  --title "feat(auth): add Google OAuth" \
  --body "## Cambios\n- Implementa OAuth con Google\n\n## Testing\n- Tests añadidos en /tests/auth" \
  --base main \
  --draft                          # Como borrador

# Actions comunes
gh pr merge 15 --squash            # Merge con squash
gh pr merge 15 --squash --delete-branch  # Merge + borrar branch
gh pr review 15 --approve
gh pr review 15 --request-changes --body "Ver comentarios"
gh pr checks 15                    # Ver estado de checks/CI

# Checkout local del PR
gh pr checkout 15                  # Para revisar o testear un PR
```

## CI/CD — Actions Runs

```bash
# Listar workflow runs
gh run list
gh run list --workflow "CI"
gh run list --status failure

# Ver un run específico
gh run view 12345678
gh run view 12345678 --log                   # Ver los logs

# Reintentar run fallido
gh run rerun 12345678
gh run rerun 12345678 --failed-only

# Ver workflows disponibles
gh workflow list

# Disparar workflow manualmente
gh workflow run deploy.yml
gh workflow run deploy.yml -f environment=staging

# Cancelar run
gh run cancel 12345678
```

## Repositorios

```bash
# Info del repo
gh repo view
gh repo view owner/repo

# Clonar repo
gh repo clone owner/repo

# Crear repo
gh repo create my-new-repo \
  --public \
  --description "Descripción del repo" \
  --clone

# Fork
gh repo fork owner/repo --clone

# Variables de entorno del repo
gh variable list
gh variable set DATABASE_URL --body "postgresql://..."

# Secrets
gh secret list
gh secret set API_KEY               # Pedirá el valor de forma segura
```

## API — Para casos avanzados

```bash
# Llamada directa a la API de GitHub
gh api /repos/garri333/Promts

# Con query GraphQL
gh api graphql -f query='
  query {
    viewer {
      login
      repositories(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          name
          updatedAt
        }
      }
    }
  }
'

# Obtener rate limit actual
gh api /rate_limit

# Crear release
gh api /repos/garri333/Skills/releases \
  --method POST \
  -f tag_name="v1.0.0" \
  -f name="v1.0.0 - Initial Release" \
  -f body="Primera versión con 40+ skills"
```

## Workflows comunes

### Crear y mergear PR rápido (feature branch)
```bash
git checkout -b feat/nueva-skill
# ... hacer cambios ...
git add .
git commit -m "feat(skills): add react-native skill"
git push -u origin feat/nueva-skill

# Crear PR directamente desde CLI
gh pr create --title "feat(skills): add react-native skill" --fill
# --fill usa el último commit message automáticamente

# Cuando esté aprobado
gh pr merge --squash --delete-branch
```

### Revisar qué CI está fallando
```bash
gh pr checks 15                    # Ver todos los checks del PR
gh run list --status failure       # Ver runs fallidos
gh run view --log-failed           # Solo los logs con errores
```

### Gestionar issues desde terminal
```bash
# Asignar issue a ti mismo al empezar a trabajar en él
gh issue edit 42 --add-assignee @me

# Quando termines, cierra referenciando el PR
gh issue close 42 --comment "Resuelto en #15"
```

## Alias útiles de gh

```bash
# Configurar alias
gh alias set prs 'pr list --author @me'
gh alias set my-issues 'issue list --assignee @me'
gh alias set draft 'pr create --draft --fill'

# Usar alias
gh prs
gh my-issues
gh draft
```

## Referencias
- [gh documentation](https://cli.github.com/manual/)
- [GitHub CLI (Clawdbot)](https://clawdbotskills.org/)
- [GitHub API Docs](https://docs.github.com/en/rest)
