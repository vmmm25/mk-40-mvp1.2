---
name: self-improving-agent
version: 1.0.0
description: Sistema para capturar aprendizajes, errores y outputs de tareas para mejorar performance del agente. Usa cuando quieras que el agente aprenda de sus errores y mejore entre sesiones.
tags: [ai, agents, learning, memory, improvement, self-correction]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Self-Improving Agent

## Concepto

Un agente que aprende de su propia experiencia captura tres tipos de información:
1. **Aprendizajes** — Lo que funcionó mejor de lo esperado
2. **Errores y correcciones** — Dónde se equivocó y cómo se corrigió
3. **Outputs de calidad** — Ejemplos de trabajo bien hecho para referenciar

## Archivos de captura

### LEARNINGS.md — Captura de aprendizajes
```markdown
# Agent Learnings

## Formato
[FECHA] [CATEGORÍA] | Aprendizaje | Contexto en que se aplica

---

## Aprendizajes

### Código
2026-02-18 [Python] | Cuando se usa asyncio.gather, wrappear cada coroutine en asyncio.create_task mejora el error handling | Aplica en cualquier código async que deba continuar aunque falle uno

2026-02-15 [SQL] | Para queries con GROUP BY + HAVING, añadir índice compuesto en (columna_group, columna_having) reduce el tiempo de query un 80% | Aplica en cualquier tabla con >100k filas

### Comunicación
2026-02-10 [Writing] | Los emails de ventas que mencionan una empresa específica en la primera línea tienen CTR 3x mayor | Aplica en cold outreach B2B

### Herramientas
2026-02-08 [Git] | Siempre verificar el branch actual antes de hacer commit, especialmente en proyectos multi-branch | Aplica siempre
```

### ERRORS.md — Registro de errores y correcciones
```markdown
# Agent Errors & Corrections

## Formato
[FECHA] | Error cometido | Causa raíz | Corrección aplicada | Cómo evitarlo

---

## Errores

2026-02-18 | Generé un schema SQL con tipos incorrectos para PostgreSQL (usé INT en lugar de BIGINT para IDs) | Asumí tipos genéricos de SQL sin considerar el motor específico | Corregí los tipos y añadí constraintss apropiados | Siempre preguntar qué motor de DB se usa antes de generar schemas

2026-02-16 | El copy del email era genérico y no mencionaba el contexto específico del lead | Generé sin suficiente información del prospect | Reescribí con los datos de la empresa del lead | Preguntar por empresa, cargo, y contexto reciente del lead antes de escribir email de ventas
```

### EXAMPLES.md — Outputs de referencia
```markdown
# Ejemplos de Referencia de Calidad

## Código — Ejemplo aprobado: Auth middleware Express
[Código de ejemplo aquí — el que el usuario aprobó como bien hecho]

## Copy — Email de ventas aprobado: B2B SaaS
[Email de ventas exacto que el cliente aprobó y funcionó]

## Documentación — README aprobado: API docs
[README que recibió feedback positivo]
```

## Instrucciones para el agente

Añadir al system prompt o `.cursorrules`:

```
## Self-Improvement Protocol

### Al inicio de cada sesión:
1. Lee LEARNINGS.md — aplica los aprendizajes relevantes
2. Lee ERRORS.md — evita los errores já cometidos en contextos similares
3. Si hay EXAMPLES.md, úsalos como referencia de calidad

### Durante la sesión:
- Si cometes un error y lo corriges, apúntalo mentalmente
- Nota qué enfoques funcionan especialmente bien

### Al finalizar tareas complejas:
Si el usuario aprueba el resultado:
1. Añade a LEARNINGS.md: qué técnica o enfoque fue efectivo
2. Si fue sustancialmente mejor de lo esperado, añade a EXAMPLES.md

Si el usuario corrige el resultado:
1. Añade a ERRORS.md: qué salió mal, por qué, y la corrección
2. Actualiza tu enfoque para el resto de la sesión
```

## Implementación manual vs automática

### Manual (más simple)
El usuario dice: _"Apunta este aprendizaje"_ o _"Anota este error"_
El agente edita el archivo correspondiente.

### Automática (más potente)
El agente propone al final de sesiones largas:
```
"Esta sesión tuvimos un insight importante sobre [tema]. ¿Quieres que lo añada
a LEARNINGS.md para recordarlo en futuras sesiones?"
```

## Revisión periódica

Una vez por semana o por sprint:
```
"Revisa ERRORS.md y LEARNINGS.md de las últimas 2 semanas.
Identifica:
1. Patrones de errores que se repiten (señal de algo sistemático)
2. Skills que debería añadir a este repositorio
3. Entradas que ya no son relevantes para limpiar"
```

## Integración con skills del repositorio

Cuando un aprendizaje es suficientemente genérico y reutilizable, promovelo de LEARNINGS.md a una skill:

```
Criterio para promover a skill:
- Se aplicaría en ≥3 proyectos diferentes
- Es conocimiento especializado, no específico de un proyecto
- Sería valioso compartirlo con otros
```

## Template de inicio rápido

Copia estos archivos a la raíz de tu proyecto:

```bash
# LEARNINGS.md
echo "# Agent Learnings\n\n## Código\n\n## Comunicación\n\n## Herramientas" > LEARNINGS.md

# ERRORS.md  
echo "# Agent Errors & Corrections\n\n[FECHA] | Error | Causa | Corrección | Prevención" > ERRORS.md
```

## Referencias
- [Self-Improving Agent (Clawdbot)](https://clawdbotskills.org/)
- [Anthropic Constitutional AI](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)
