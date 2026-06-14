---
name: coding-agent
version: 1.0.0
description: Ejecutar agentes de codificación autónomos como Codex CLI, Claude Code, OpenCode o Aider como sub-agentes. Usa cuando necesites delegare tareas de programación complejas a un agente especializado.
tags: [agents, coding, codex, claude-code, aider, opencode, automation, subagent]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Coding Agent Skill

## Cuándo usar esta skill
- Delegar una tarea de programación compleja a un agente especializado
- Ejecutar refactorizaciones grandes de forma autónoma
- Hacer implementaciones multi-archivo mientras el agente gestiona el contexto
- Quieres que el agente escriba, testee, y corrija código de forma autónoma

## Agentes disponibles

### Claude Code (Anthropic)
```bash
# Instalar
npm install -g @anthropic-ai/claude-code

# Uso básico
claude "Implementa un endpoint REST para gestión de usuarios con Express y TypeScript"

# Con contexto de directorio
cd /mi-proyecto
claude "Refactoriza todos los componentes en src/components para usar React.memo donde sea beneficioso"

# Modo no interactivo (para CI/CD)
claude --dangerously-skip-permissions --print "Escribe tests unitarios para todos los archivos en src/utils/"

# Con contexto específico
claude --add-to-context="REQUIREMENTS.md" "Implementa las funcionalidades descritas en los requisitos"
```

### Codex CLI (OpenAI)
```bash
# Instalar
npm install -g @openai/codex

# Uso básico
codex "crea una función Python para parsear archivos CSV con manejo de errores"

# Modo quiet (para automatización)
codex --quiet "añade type hints a todos los archivos Python en este directorio"

# Con archivo de entrada
codex "explica este código y sugiere mejoras" < mi-archivo.py
```

### Aider (popular, open source)
```bash
# Instalar
pip install aider-chat

# Initiar sesión con archivos específicos
aider src/api/users.py src/models/user.py

# Comandos dentro de aider:
# /add archivo.py    — Añadir archivo al contexto
# /drop archivo.py   — Quitar archivo del contexto
# /run npm test      — Ejecutar comando
# /diff              — Ver cambios actuales
# /undo              — Deshacer último cambio

# Con modelo específico
aider --model gpt-4o src/app.py

# Modo sin git (para experimentación)
aider --no-git src/experiment.py

# Batch mode con instrucciones de archivo
echo "Añade manejo de errores a todas las funciones async" | aider --yes mi-archivo.py
```

### OpenCode
```bash
# Ver documentación actualizada en: https://github.com/opencode-ai/opencode
npx opencode "implementa autenticación JWT en este proyecto"
```

## Mejores prácticas para usar coding agents

### 1. Instrucciones efectivas

```markdown
✅ Instrucciones claras y específicas:
"Refactoriza la función `processUsers` en `src/utils/users.js` para:
1. Usar TypeScript con tipos explícitos
2. Añadir manejo de errores con try/catch
3. Retornar un Result<T, E> type en lugar de throw
4. Añadir JSDoc comments
Mantén la funcionalidad existente y el API público idéntico."

❌ Instrucciones vagas:
"Mejora el código de usuarios"
```

### 2. Dar contexto relevante
```bash
# Proporcionar archivos de contexto relevantes
claude --add-to-context="docs/architecture.md" \
       --add-to-context="src/types/index.ts" \
       "Implementa el módulo de notificaciones siguiendo la arquitectura existente"

# O crear un prompt file
cat > agent-task.md << 'EOF'
## Tarea: Implementar sistema de caché

### Contexto
- Proyecto: API REST con Node.js/Express
- Base de datos: PostgreSQL
- Ya existe lib/db.ts con la conexión

### Requisitos
1. Implementar caché con Redis para las queries más frecuentes
2. TTL configurable por tipo de query
3. Invalidar caché en mutations
4. Métricas de hit/miss ratio

### Archivos a crear/modificar
- src/lib/cache.ts (nuevo)
- src/lib/db.ts (modificar para usar caché)
- .env.example (añadir REDIS_URL)
EOF

claude --add-to-context="agent-task.md" "Implementa lo descrito en agent-task.md"
```

### 3. Revisar antes de aplicar
```bash
# Ver diff antes de aceptar cambios (aider)
aider --dry-run src/api.py < instrucciones.txt

# Claude Code muestra diffs por defecto antes de escribir

# Siempre con git para poder revertir
git status
git add .
git commit -m "checkpoint before agent"
# ... ejecutar agente ...
git diff HEAD  # revisar cambios
git checkout . # revertir si no convence
```

## Automatización con coding agents

### Script de automatización básico
```bash
#!/bin/bash
# auto-review.sh — Revisión automática de código con agente

set -e

echo "=== Auto Review Pipeline ==="

# 1. Asegurar que los tests pasan antes
npm test || { echo "Tests failing, fix first"; exit 1; }

# 2. Lint
npm run lint 2>&1 | head -50

# 3. Delegar a agente para sugerencias
echo "=== Running coding agent review ==="
claude --dangerously-skip-permissions --print \
  "Revisa el diff de git actual (git diff HEAD~1) y:
   1. Identifica posibles bugs
   2. Sugiere mejoras de performance
   3. Verifica que los tests cubren los cambios
   Solo da recomendaciones, no modifiques archivos."
```

### Pipeline CI/CD con agente
```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on: [pull_request]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code
      
      - name: Run AI Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff origin/main...HEAD > pr-diff.txt
          claude --dangerously-skip-permissions --print \
            "Revisa este pull request diff y:
             - Identifica bugs críticos o problemas de seguridad
             - Señala violaciones de best practices
             - Máximo 10 comentarios, ordenados por severidad
             
             Diff:
             $(cat pr-diff.txt)" > review.txt
          cat review.txt
```

## Casos de uso típicos

### 1. Generación de tests
```bash
claude "Para cada función en src/utils/math.ts, 
genera tests unitarios con Jest que incluyan:
- Happy path
- Edge cases (null, undefined, vacío, overflow)
- Casos de error
Coloca los tests en src/utils/__tests__/math.test.ts"
```

### 2. Migración de código
```bash
claude "Migra todo el código de callbacks en src/api/ 
a async/await manteniendo la misma funcionalidad. 
Asegúrate de que los tests siguen pasando."
```

### 3. Documentación automática
```bash
claude "Añade JSDoc/docstrings a todas las funciones 
públicas en src/ que no tengan documentación.
Incluye @param, @returns, y un ejemplo de uso."
```

### 4. Refactorización de estructura
```bash
claude "Reorganiza los archivos en src/ siguiendo una 
arquitectura hexagonal:
- src/domain/ (entities, value objects)
- src/application/ (use cases)
- src/infrastructure/ (repos, external APIs)
- src/interfaces/ (controllers, API routes)
Actualiza todos los imports."
```

## Limitaciones y precauciones

```
⚠️  Siempre revisar el diff antes de hacer commit
⚠️  Usar git para poder revertir cambios del agente
⚠️  No usar --dangerously-skip-permissions en producción
⚠️  Los agentes pueden introducir bugs sutiles — revisar tests
⚠️  Cuidado con código que accede a sistemas externos
⚠️  Los cambios de large refactors son difíciles de revisar — divide en pasos
```

## Referencias
- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Codex CLI GitHub](https://github.com/openai/codex)
- [Aider documentation](https://aider.chat/)
