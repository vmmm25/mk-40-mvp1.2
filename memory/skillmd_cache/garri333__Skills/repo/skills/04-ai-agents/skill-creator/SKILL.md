---
name: skill-creator
version: 1.0.0
description: Guía para crear skills nuevas efectivas para agentes IA. Usa cuando un usuario quiera crear una nueva skill o extender las capacidades del agente con conocimiento especializado.
tags: [meta, skills, agent-skills, knowledge, documentation]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Skill Creator

## ¿Qué es una skill?

Una skill es un **archivo de conocimiento estructurado** (SKILL.md) que le dice al agente:
- Qué sabe hacer en este dominio
- Cuándo debe aplicar ese conocimiento
- Cómo debe comportarse cuando la skill es relevante

El agente detecta automáticamente las skills disponibles y las aplica cuando el contexto de la conversación las hace relevantes.

## Cuándo crear una skill

Crea una skill cuando:
- 🔄 **Repites las mismas instrucciones** en múltiples sesiones
- 📚 **Tienes conocimiento específico** de tu empresa/proyecto que el agente no tiene
- 🎯 **Quieres comportamiento consistente** en un dominio específico
- 🚀 **Integras una herramienta/API** que el agente necesita aprender a usar

NO crees una skill para:
- Tareas únicas (usa un prompt directamente)
- Conocimiento genérico que el modelo ya tiene
- Instrucciones específicas de una sola sesión

## Proceso para crear una skill

### Paso 1: Definir el alcance

Antes de escribir, responde:
1. ¿Qué problema resuelve esta skill?
2. ¿Cuándo debería el agente usarla automáticamente?
3. ¿Qué conocimiento necesita el agente que no tiene?
4. ¿Qué restricciones o reglas debe seguir?

### Paso 2: Elegir el nombre

```
✅ Buenos nombres:
- descriptivos: "react-best-practices"
- accionables: "api-design"
- específicos: "privalex-voice-and-tone"

❌ Malos nombres:
- vagos: "helpers", "utils"
- genéricos: "good-code", "write-well"
- abreviados sin contexto: "rbp", "wag"
```

Formato: `kebab-case`, sin espacios, sin caracteres especiales.

### Paso 3: Escribir el SKILL.md

```markdown
---
name: nombre-de-la-skill
version: 1.0.0
description: UNA FRASE que describe qué hace y cuándo usarla. Crítico — esto es lo que lee el agente para decidir si activar la skill.
tags: [tag1, tag2, tag3]  # Para búsqueda y organización
author: tu-nombre
license: MIT
---

# Título de la Skill

## ¿Cuándo usar esta skill?
Lista explícita de triggers:
- Cuando el usuario pide X
- Cuando se trabaja con tecnología Y
- Cuando el contexto incluye Z

## [Sección de contenido principal]
El conocimiento real de la skill...

## Ejemplos
Ejemplos concretos de cómo aplicar la skill...
```

### Paso 4: La descripción es crítica

La `description` en el frontmatter es lo primero que lee el agente para decidir si usar la skill. Debe:
- Ser una sola frase (max 120 caracteres)
- Incluir "Usa cuando..." para disparar automáticamente
- Ser específica, no genérica

```yaml
# ✅ Buena descripción
description: "Guía de SEO para contenido PrivaLex. Usa cuando generes blog posts o contenido web para asegurar la estructura correcta de keywords."

# ❌ Mala descripción  
description: "SEO guidelines"
```

## Estructura recomendada para el contenido

### Skill de "cómo hacer X" (how-to)
```markdown
# ¿Qué es esta skill?
# Cuándo usar
# Proceso paso a paso
## Paso 1
## Paso 2
# Casos de uso con ejemplos
# Errores comunes a evitar
# Referencias
```

### Skill de "reglas y estilo" (guidelines)
```markdown
# Principios fundamentales
# Reglas específicas por área
## Área 1
## Área 2
# Lo que SÍ hacer vs lo que NO hacer
# Ejemplos buenos vs malos
# Checklist de calidad
```

### Skill de "conocimiento de dominio" (knowledge base)
```markdown
# Qué es [dominio]
# Conceptos clave y definiciones
# Cómo funciona
## Aspecto 1
## Aspecto 2
# Casos prácticos
# Terminología / Glosario
# Referencias
```

### Skill de "integración con herramienta" (integration)
```markdown
# Qué es esta herramienta y para qué sirve
# Cuándo usar esta herramienta
# Comandos disponibles
## Comando 1: [nombre]
## Comando 2: [nombre]
# Ejemplos de uso
# Limitaciones y precauciones
# Configuración necesaria
```

## Ejemplo de skill bien hecha vs mal hecha

### ❌ Skill mal hecha
```markdown
---
name: write-code
description: For writing code
tags: [code]
---
# Write Good Code
Write clean, maintainable code following best practices.
```
Problemas: descripción vaga, sin triggers, sin conocimiento concreto, no aporta valor.

### ✅ Skill bien hecha
```markdown
---
name: python-async-patterns
version: 1.0.0
description: Patrones async/await de Python para I/O concurrente. Usa cuando escribas código Python que hace múltiples llamadas de red, base de datos o archivos simultáneamente.
tags: [python, async, performance, concurrency, backend]
---

# Python Async Patterns

## Cuándo usar async vs threads vs processes

| Scenario | Solución |
|----------|----------|
| I/O bound (network, DB) | asyncio |
| CPU bound (computaciones) | multiprocessing |
| Mezcla I/O + CPU | asyncio + ProcessPoolExecutor |

## Pattern 1: Concurrent requests
[código concreto con asyncio.gather...]

## Pattern 2: Semaphore para rate limiting
[código concreto...]
```

## Dónde colocar la skill

```
# Global (para todos los proyectos):
~/.cursor/skills/nombre-skill/SKILL.md
~/.claude/skills/nombre-skill/SKILL.md

# Por proyecto:
.cursor/skills/nombre-skill/SKILL.md
.claude/skills/nombre-skill/SKILL.md
```

## Iterar y mejorar skills

Una skill buena se itera:
1. Usa la skill en un proyecto real
2. Observa dónde el agente falla o ignora la skill
3. Mejora la `description` si no se activa cuando debería
4. Añade ejemplos en las secciones donde el agente da respuestas incorrectas
5. Añade restricciones donde el agente hace cosas no deseadas

## Checklist de calidad

Antes de publicar una skill, verifica:

- [ ] La `description` tiene "Usa cuando..." y es específica
- [ ] El nombre es descriptivo y en kebab-case
- [ ] El contenido es específico y útil (no genérico)
- [ ] Hay ejemplos concretos
- [ ] Hay sección de "cuándo usar"
- [ ] Los tags son relevantes para búsqueda
- [ ] El contenido no contradice otras skills del repositorio
- [ ] La skill es independiente (no requiere otra skill específica para funcionar)

## Referencias
- [Agent Skills Standard](https://agentskills.io/specification)
- [skills.sh](https://skills.sh/)
- [K-Dense Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills)
