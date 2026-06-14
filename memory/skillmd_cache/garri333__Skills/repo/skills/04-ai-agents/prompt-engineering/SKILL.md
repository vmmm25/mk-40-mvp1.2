---
name: prompt-engineering
version: 1.0.0
description: Técnicas avanzadas de prompt engineering para optimizar prompts de agentes IA. Usa cuando crees, mejores o depures prompts para cualquier modelo IA.
tags: [ai, prompts, llm, gpt, claude, engineering, agents]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Prompt Engineering Expert

## Fundamentos del prompting

### Anatomía de un buen prompt

```
[ROLE]       — Quién es el modelo (experto, asistente, personaje)
[CONTEXT]    — Información de fondo que el modelo necesita
[TASK]       — Qué debe hacer exactamente
[FORMAT]     — Cómo debe presentar la respuesta
[CONSTRAINTS]— Límites, restricciones, lo que NO debe hacer
[EXAMPLES]   — Few-shot examples (opcional pero muy efectivo)
```

### Ejemplo: Prompt mal vs bien estructurado

```
❌ MAL:
"Escribe un email de ventas"

✅ BIEN:
Actúa como un copywriter especializado en B2B SaaS.

Contexto: Somos una startup de ciberseguridad (Privalex) que ofrece certificaciones ISO 27001.
El lead es un CTO de una fintech de 50 personas que acaba de perder un deal por no tener ISO 27001.

Tarea: Escribe un email de seguimiento (200-250 palabras) que:
1. Empatice con la situación sin ser condescendiente
2. Haga el ROI tangible (certificación → deals)
3. Termine con un CTA específico (agendar 20 min de llamada)

Restricciones: Sin jargon legal. Sin "solución integral". Tono directo y humano.
Formato: Asunto + cuerpo del email. Un solo párrafo de apertura, 3 bullets, CTA.
```

## Técnicas avanzadas

### Chain of Thought (CoT)
Hace que el modelo "piense en voz alta" antes de responder:
```
"Analiza este problema paso a paso antes de dar tu respuesta final.
Explica tu razonamiento para cada paso."
```

### Few-shot prompting
Proporciona ejemplos del output esperado:
```
"Clasifica el sentimiento de estas reseñas:

Reseña: 'El producto llegó en buen estado y el servicio fue excelente'
Sentimiento: POSITIVO

Reseña: 'Tardó 3 semanas y llegó roto'
Sentimiento: NEGATIVO

Reseña: 'Cumple con lo básico pero nada más'
Sentimiento: [COMPLETA]"
```

### Role prompting
Define un rol específico con expertise real:
```
✅ ESPECÍFICO: "Actúa como un CISO con 15 años de experiencia implementando ISO 27001
en startups europeas. Eres práctico, no teórico."

❌ VAGO: "Eres un experto en seguridad"
```

### Structured output
Pide outputs en formato estructurado para facilitar el procesamiento:
```
"Responde en JSON con esta estructura exacta:
{
  "puntuacion": number (1-10),
  "fortalezas": string[],
  "debilidades": string[],
  "recomendacion": string
}"
```

### Self-consistency
Para respuestas más fiables, pide múltiples razonamientos:
```
"Analiza este código desde tres perspectivas diferentes:
1. Como un desarrollador enfocado en performance
2. Como un desarrollador enfocado en seguridad
3. Como un desarrollador enfocado en mantenibilidad
Luego da una evaluación integrada."
```

### Tree of Thought
Para problemas complejos con múltiples caminos:
```
"Genera 3 enfoques diferentes para resolver este problema.
Para cada enfoque, evalúa sus pros y contras.
Luego selecciona el mejor y desarrolla una solución completa."
```

## Prompting para código

### Revisión de código
```
"Revisa este código como un senior engineer con foco en:
1. Bugs potenciales
2. Problemas de performance
3. Problemas de seguridad
4. Legibilidad y mantenibilidad

Para cada problema encontrado:
- Ubícalo (línea o función)
- Explica por qué es un problema
- Sugiere la solución correcta con código

[CÓDIGO AQUÍ]"
```

### Generación de código
```
"Implementa [FUNCIONALIDAD] en [LENGUAJE/FRAMEWORK].

Requisitos:
- [REQ 1]
- [REQ 2]

Restricciones:
- Compatible con [VERSIÓN]
- No uses [LIBRERÍA/PATRÓN] porque [RAZÓN]
- Sigue el patrón [PATRÓN] del código existente

Incluye:
- Código completo y funcional
- Comentarios en las partes no obvias
- Tests unitarios básicos"
```

### Debugging
```
"Ayúdame a debuggear este error.

Error: [PEGAR ERROR COMPLETO CON STACK TRACE]

Contexto:
- Cuándo ocurre: [DESCRIBE]
- Frecuencia: [siempre / a veces / raramente]
- Cambios recientes: [SI APLICA]

Código relevante:
[PEGAR CÓDIGO]

Analiza las causas posibles y propón soluciones, empezando por la más probable."
```

## Prompting para agentes

### System prompt de agente efectivo
```
# Rol y objetivo
Eres [NOMBRE], un agente especializado en [DOMINIO].
Tu objetivo es [OBJETIVO PRINCIPAL].

# Contexto
[INFORMACIÓN RELEVANTE QUE SIEMPRE NECESITAS]

# Herramientas disponibles
- [HERRAMIENTA 1]: Úsala para [CUÁNDO]
- [HERRAMIENTA 2]: Úsala para [CUÁNDO]

# Proceso
1. [PASO 1]
2. [PASO 2]
3. [PASO 3]

# Restricciones
- Nunca [RESTRICCIÓN 1]
- Siempre [RESTRICCIÓN 2]
- Si [SITUACIÓN], entonces [RESPUESTA]

# Formato de respuesta
[ESTRUCTURA ESPERADA]
```

### Prompt para tareas con pasos
```
"Completa esta tarea siguiendo exactamente estos pasos:

1. PRIMERO: Analiza [X] y lista lo que encuentres
2. LUEGO: Basándote en el análisis anterior, haz [Y]
3. FINALMENTE: Produce [Z] en formato [FORMATO]

No pases al siguiente paso sin completar el anterior.
Confirma con 'Paso X completado: [resumen]' después de cada paso."
```

## Errores comunes a evitar

| ❌ Error | ✅ Corrección |
|---------|---------------|
| Prompts ambiguos | Define exactamente qué quieres |
| Sin formato del output | Especifica estructura, longitud, formato |
| Sin contexto | Proporciona background relevante |
| Pedir todo a la vez | Divide tareas complejas en pasos |
| Instructions contradictorias | Revisa conflictos en tus instrucciones |
| Asumir conocimiento implícito | Hace explícito lo que "está claro" |

## Evaluación de prompts

Después de un prompt, evalúa:
1. **Relevancia** — ¿Respondió lo que pregunté?
2. **Completitud** — ¿Cubrió todos los aspectos pedidos?
3. **Precisión** — ¿La información es correcta?
4. **Formato** — ¿El output es usable tal cual?
5. **Tono** — ¿Suena como quería?

Si falla en 2+: Reescribe el prompt con más contexto o más ejemplos.

## Iteración de prompts

```
v1: Prompt inicial
v2: Añade examples si el formato es incorrecto
v3: Añade restricciones si incluye cosas no deseadas
v4: Añade role si el tono/expertise no es el correcto
v5: Añade chain-of-thought si el razonamiento falla
```

## Referencias
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Clawdbot Prompt Engineering Expert](https://clawdbotskills.org/)
- [Learn Prompting](https://learnprompting.org/)
