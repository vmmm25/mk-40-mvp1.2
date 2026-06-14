---
name: humanizer
version: 1.0.0
description: Detecta y elimina marcadores de texto generado por IA para hacer el contenido más natural y humano. Usa cuando revises textos antes de publicarlos o enviarlos.
tags: [writing, ai, content, editing, humanizing, copywriting]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Humanizer — Eliminar marcadores de IA

## Señales de texto generado por IA (detectar y eliminar)

### 1. Simbolismo inflado
El texto asigna significado profundo a cosas mundanas:

```
❌ IA: "Esta herramienta no es solo software; es un faro de innovación que ilumina el camino hacia el futuro digital."
✅ Humano: "Esta herramienta ahorra 3 horas por semana en tareas repetitivas."
```

### 2. Lenguaje promocional vacío
Afirmaciones grandiosas sin datos concretos:

```
❌ IA: "revolucionario", "sin precedentes", "world-class", "líder del sector", "de vanguardia"
✅ Humano: Datos específicos. "El único X que hace Y" solo si es verificable.
```

### 3. Análisis superficial con -ing
Especialmente en inglés, pero también en patrones traducidos:

```
❌ IA: "Siendo una empresa innovadora, priorizando la excelencia, manteniendo el foco en..."
✅ Humano: Oraciones directas. "Priorizamos X porque Y."
```

### 4. Atribuciones vagas
Referencias a "estudios", "expertos", o "la industria" sin citar fuentes:

```
❌ IA: "Según expertos del sector, las empresas que adoptan X experimentan un crecimiento significativo."
✅ Humano: "Según McKinsey (2025), el 67% de empresas que..." O eliminar la atribución vaga.
```

### 5. Abuso del em dash (—)
El em dash es el signo de puntuación favorito de los LLMs:

```
❌ IA: "Esta solución — que combina IA con experiencia humana — ofrece resultados — tanto a corto como a largo plazo — que superan las expectativas."
✅ Humano: Reformular. Usar comas, puntos o reorganizar la frase.
```

### 6. La regla de tres
Los LLMs adoran las listas de exactamente tres. Siempre. Sin falta.

```
❌ IA: "La plataforma ofrece velocidad, simplicidad y potencia."
✅ Humano: Uno, dos, o cuatro también existen. O desarrollar cada punto con sustancia.
```

### 7. Vocabulario específico de IA
Palabras y frases hiper-características de LLMs:

```
Palabras a evitar:
- "delve into" / "adentrarnos en"
- "tapestry" / "tejido" (en contexto metafórico)
- "nuances" / "matices" (usado en exceso)
- "leverage" / "apalancarse en" (genérico)
- "journey" / "viaje" (como metáfora de proceso)
- "crucial" / "vital" (overused)
- "transform" / "transformar" (sin contexto concreto)
- "synergy" / "sinergia"
- "holistic" / "holístico"
- "paradigm shift" / "cambio de paradigma"
- "empower" / "empoderar"
- "streamline" / "optimizar" (genérico)
```

### 8. Negativismo paralelo
Estructura "no solo X, sino también Y":

```
❌ IA: "No solo es una herramienta de colaboración, sino también una plataforma de innovación y, al mismo tiempo, un catalizador de transformación digital."
✅ Humano: Di qué es directamente. "Es una herramienta de colaboración que también gestiona proyectos y centraliza la comunicación del equipo."
```

### 9. Frases conjuntivas excesivas
"Furthermore", "Moreover", "Additionally" al inicio de cada párrafo:

```
❌ IA: "Además, cabe destacar que... Por otro lado, es importante mencionar que... Asimismo, conviene señalar que..."
✅ Humano: Transiciones naturales que fluyen del contenido, no fórmulas pegadas.
```

### 10. Apertura de email/mensaje genérica

```
❌ IA: "Espero que este mensaje te encuentre bien." / "Hope this email finds you well."
✅ Humano: Ve directo al punto, o conecta con algo real ("Vi que tu empresa acaba de...")
```

## Proceso de humanización

### Paso 1: Escaneo de señales
Lee el texto completo y marca:
- 🚩 Lenguaje promotional vacío
- 🚩 Em dashes en exceso (—)
- 🚩 Regla de tres exacta
- 🚩 Palabras del vocabulario IA
- 🚩 Atribuciones vagas

### Paso 2: Transformaciones clave

| Técnica | Descripción |
|---------|-------------|
| **Especificar** | Reemplaza vago por concreto ("muy rápido" → "en menos de 200ms") |
| **Acortar** | Si se puede decir en menos palabras, hazlo |
| **Personalizar** | Añadir anécdota, opinión, o punto de vista específico |
| **Variar estructura** | Mezcla frases largas y muy cortas. El AI tiende a uniformidad |
| **Añadir imperfección** | Una palabra coloquial, una metáfora propia, una duda real |
| **Eliminar redundancia** | "En el mundo actual de hoy en día" → "Hoy" |

### Paso 3: Test final
Lee el texto en voz alta. Si suena raro o artificial al escucharlo, reescríbelo.

## Tests de humanización

### Test del primo inteligente
¿Lo diría tu primo más listo en una cena? Si no, reformula.

### Test de la búsqueda
Copia una frase de 10-12 palabras del texto y búscala en Google. Si aparece word-for-word en otro lugar, es una frase genérica de IA.

### Test de la specificity
¿Podría esta frase aplicarse a cualquier empresa/producto/persona? Si sí, añade datos específicos o elimínala.

## Estructura que sí parece humana

Los textos humanos naturales tienen:
- Frases de longitud variable (no todas de 15-20 palabras)
- Opiniones con "creo que", "en mi experiencia"
- Referencias concretas y verificables
- Transiciones que fluyen, no etiquetas de transición
- Alguna imperfección o matiz personal

## Herramientas para detectar IA

- [GPTZero](https://gptzero.me/) — Detecta % de texto IA
- [Originality.ai](https://originality.ai/) — Detección + SEO
- [Copyleaks](https://copyleaks.com/) — AI detector + plagiarism

## Referencias
- [Wikipedia: Signs of AI Writing](https://en.wikipedia.org/wiki/Signs_of_AI_writing)
- [Humanizer (Clawdbot)](https://clawdbotskills.org/)
