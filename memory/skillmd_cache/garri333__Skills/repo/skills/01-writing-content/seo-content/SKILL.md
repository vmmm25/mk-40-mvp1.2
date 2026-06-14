---
name: seo-content
version: 1.0.0
description: Guía completa de SEO y estructura editorial para contenido web. Usa cuando crees blog posts, landing pages o cualquier contenido web que necesite posicionamiento en buscadores.
tags: [seo, content, writing, blog, marketing, web]
author: garri333
license: MIT
---

# SEO Content Guidelines

## Principios SEO fundamentales

1. **Escribe para personas primero, buscadores segundo** — La experiencia del usuario es la señal más importante
2. **Una keyword principal por página** — Enfoca, no diluyas
3. **Responde la pregunta real** — Google premia el contenido que satisface la intención de búsqueda
4. **E-E-A-T** — Experience, Expertise, Authoritativeness, Trustworthiness

## Tipos de intención de búsqueda

| Tipo | Ejemplos | Formato ideal |
|------|----------|---------------|
| **Informacional** | "qué es ISO 27001", "cómo funciona el RGPD" | Guía educativa, definición |
| **Navegacional** | "Privalex Partners", "GitHub login" | Página de marca |
| **Transaccional** | "comprar hosting", "contratar DPO" | Landing page, pricing |
| **Comercial** | "mejor software CRM", "alternativas a Notion" | Comparativa, listicle |

## Estructura On-Page

### Título (H1)
- **Máximo 60 caracteres**
- Incluye la keyword principal de forma natural
- No uses dos puntos (:) ao inicio
- Formatos por intención:
  - Informacional: "Cómo hacer X en [contexto]"
  - Comercial: "Los X mejores [producto/servicio] para [audiencia]"
  - Comparativa: "[A] vs [B]: cuál elegir en [año]"

### Meta description
- **Máximo 155 caracteres**
- Incluye la keyword principal completa
- Incluye un beneficio o razón para hacer click
- Termina con algo que genere curiosidad o urgencia

### URL / Slug
- Solo la keyword, sin palabras extra
- Minúsculas, guiones, sin acentos
- `keyword-principal` (no `keyword-principal-guia-completa-2026`)

### Estructura de headings
```
H1: Una sola vez — el título principal con la keyword
  H2: Secciones principales (incluyen keywords secundarias cuando es natural)
    H3: Subsecciones dentro de cada H2
      H4: Raramente necesario
```
- Nunca saltes niveles (H1 → H3)
- Los H2 deben funcionar como tabla de contenidos independiente

### Cuerpo del contenido
- **Keyword principal en los primeros 100 palabras**
- Párrafos cortos: 2-4 líneas máximo en web
- Use negrita para términos clave en su primera mención
- Mínimo 800 palabras para posts estándar, 1.500+ para guías pillar

## Estructura por tipo de contenido

### Listicle (Best X for Y)
```
H1: Los X mejores [producto] para [audiencia]
[Intro: 2-3 párrafos con keyword, qué vas a comparar]
[Índice numerado]
H2: Cómo elegir el mejor [producto]
  H3: Criterio 1
  H3: Criterio 2
H2: Los X mejores [producto]
  H3: 1. [Nombre] — [tagline]
  H3: 2. [Nombre] — [tagline]
  ...
H2: Tabla comparativa
H2: Conclusión: cuál elegimos nosotros
H2: Preguntas frecuentes
  H3: ¿Pregunta 1?
  H3: ¿Pregunta 2?
```

### How-to (Cómo hacer X)
```
H1: Cómo [hacer X] paso a paso
[Intro: problema que resuelve + resultado esperado]
H2: Qué necesitas antes de empezar
H2: Cómo [hacer X]: guía paso a paso
  H3: Paso 1: [título]
  H3: Paso 2: [título]
H2: Errores comunes y cómo evitarlos
H2: Preguntas frecuentes
```

### What is (Qué es X)
```
H1: Qué es [X]: guía completa para [audiencia]
[Intro con definición + contexto]
H2: Definición de [X]
H2: Cómo funciona [X]
H2: Para quién es [X]
H2: Ventajas y desventajas
H2: [X] vs [alternativa]
H2: Cómo implementar [X]
H2: Preguntas frecuentes
```

## FAQ Section — crítica para featured snippets

- **Title**: `## Preguntas Frecuentes` o `## Frequently Asked Questions`
- **Cada pregunta**: H3 (`### ¿Pregunta?`)
- Mínimo 5-6 preguntas
- Incluir la keyword en al menos 2-3 preguntas
- Respuestas: 2-5 frases, directas y completas
- Optimizado para Google FAQ rich snippets

## Links

### Balance ideal
- **3-5 links internos** por post — A páginas relacionadas de tu mismo dominio
- **2-3 links externos** — A fuentes autoritativas (.gov, .edu, publicaciones conocidas)

### Reglas de links
- Texto ancla descriptivo (no "haz click aquí" o "leer más")
- Los links internos antes de los externos cuando sea posible
- Nunca links en headings
- Links distribuidos naturalmente (no todos al principio o al final)

## Imágenes

- **Alt text**: descriptivo, incluye keyword cuando sea natural
- **Nombre de archivo**: `como-implementar-iso-27001.webp` (no `IMG_4892.jpg`)
- **Formato**: WebP para web (comprimir antes de subir)
- **Dimensiones**: Especificar siempre (evita Cumulative Layout Shift)

## Metadata final (plantilla)

```
Título: [MAX 60 chars, keyword exacta, sin :]
Meta: [MAX 155 chars, keyword completa, persuasivo]
Slug: [solo-la-keyword]
Keyword: [principal], [secundaria-1], [secundaria-2]
```

## Checklist pre-publicación

- [ ] H1 contiene keyword principal (max 60 chars, sin :)
- [ ] Meta description max 155 chars, keyword incluida, persuasiva
- [ ] Keyword en los primeros 100 palabras
- [ ] Al menos 2 H2s contienen keyword secundaria o variación
- [ ] Mínimo 800 palabras (1.500 para pillar content)
- [ ] Párrafos de max 3-4 líneas
- [ ] 3-5 links internos con anclas descriptivos
- [ ] 2-3 links externos a fuentes autorizadas
- [ ] Imágenes con alt text y nombres descriptivos
- [ ] Sección FAQ con H3s y 5+ preguntas
- [ ] URL es solo la keyword (sin palabras extra)
- [ ] La responde la INTENCIÓN real del buscador

## Referencias
- [Google Search Central](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Semrush SEO Writing Guide](https://www.semrush.com/blog/seo-writing/)
- [Backlinko On-Page SEO](https://backlinko.com/on-page-seo)
