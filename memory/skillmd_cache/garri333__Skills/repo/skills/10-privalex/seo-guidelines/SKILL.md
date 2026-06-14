---
name: seo-guidelines
description: SEO optimization guidelines for PrivaLex content. Use when generating blog posts or any web-published content to ensure proper keyword strategy and structure.
---

# SEO Guidelines

Rules for optimizing PrivaLex content for search visibility while maintaining quality.

## Core SEO Principles

1. **Write for humans first, search engines second** — Never sacrifice readability for keywords
2. **One primary keyword per post** — Focus, don't dilute
3. **Answer the actual question** — Google rewards content that satisfies search intent
4. **Technical accuracy = authority** — E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)

## Keyword Strategy

### Primary Keyword Clusters

#### ISO 27001
- "certificación ISO 27001"
- "cómo obtener ISO 27001"
- "ISO 27001 para startups"
- "auditoría ISO 27001"
- "controles ISO 27001"
- "ISO 27001 España"
- "SGSI ISO 27001"
- "ISO 27001 vs SOC 2"
- "coste certificación ISO 27001"
- "ISO 27001 certification EU"
- "ISO 27001 for startups"

#### RGPD / GDPR
- "cumplimiento RGPD"
- "auditoría RGPD"
- "DPO externo"
- "evaluación de impacto RGPD"
- "GDPR compliance for startups"
- "external DPO services"

#### NIS2
- "cumplimiento NIS2"
- "NIS2 empresas afectadas"
- "prepararse para NIS2"
- "NIS2 compliance"
- "NIS2 requirements"

#### ENS
- "Esquema Nacional de Seguridad"
- "certificación ENS"
- "ENS para proveedores"

#### ISO 42001 / AI
- "ISO 42001 certificación"
- "gobernanza inteligencia artificial"
- "ISO 42001 vs ISO 27001"
- "AI Act cumplimiento"

#### DORA
- "DORA fintech"
- "DORA compliance"
- "resiliencia digital financiera"

#### Training / Formation
- "formación ISO 27001"
- "formación ciberseguridad empresa"
- "FUNDAE formación seguridad"
- "plan formación compliance"

## On-Page SEO Rules

### Title (H1)
- **Maximum 63 characters** including spaces — this is a hard limit
- **MUST NOT contain colons (:)** — Use natural phrasing without ":" separators
- **MUST sound natural and complete** — Like a real sentence that makes sense on its own
- **CRITICAL: ALWAYS respect the exact keyword** — If keyword is "software NIS2", use "software", NOT "herramientas"
- **Format based on keyword pattern:**
  - If keyword = "[Company] + [Framework]" (e.g., "Vanta HIPAA") → "Mejores alternativas a [Company] [Framework]"
  - If keyword = "software + [Regulatory Framework]" (e.g., "software NIS2") → "Mejor software para facilitar el cumplimiento [Framework]"
  - If keyword = "[Framework]" only (e.g., "certificación ISO 27001") → "Mejores opciones para [action verb] con/en [Framework]"
- Good examples:
  - "Mejores alternativas a Vanta HIPAA para healthtech"
  - "Mejor software para facilitar el cumplimiento NIS2" (respects "software")
  - "Mejor software para facilitar el cumplimiento HIPAA" (respects "software")
  - "Mejores opciones para certificarte con ISO 27001"
- Bad examples:
  - "Vanta HIPAA: mejores opciones en 2026" (uses colon)
  - "Mejores herramientas para NIS2" (should be "software" if keyword is "software NIS2")
- Include primary keyword naturally
- Prefer listicle format for conversion-oriented posts
- Use question format when matching informational intent (e.g., "¿Cómo obtener la certificación ISO 27001?")
- Use action format for how-to content (e.g., "Cómo documentar los controles de ISO 27001")
- Count characters carefully — titles over 63 chars MUST be shortened

### Meta Description
- **Max 135 characters** — this is a hard limit
- MUST include the FULL primary keyword (never broken up or rephrased)
- MUST be persuasive — sell the click, create urgency or curiosity
- Include a benefit or outcome
- Example: "Compara Bureau Veritas ISO 27001 con las mejores opciones del mercado. Descubre cuál te conviene más y certifícate a la primera."

### URL / Slug
- **Slug = ONLY the keyword** converted to slug format
- Lowercase, hyphens, no accents
- Do NOT add extra words beyond the keyword
- Example: keyword "Bureau Veritas ISO 27001" → slug: `bureau-veritas-iso-27001`
- Example: keyword "mejores consultoras NIS2" → slug: `mejores-consultoras-nis2`

### Headings (H2, H3)
- H2s should include secondary keywords naturally
- **H2s that contain listicles MUST include the quantity** (e.g., "5 errores comunes", "9 fases del proceso")
- Each item inside a listicle H2 MUST be an H3
- H2s should work as a standalone table of contents
- H3s for detailed subsections
- Never skip heading levels (H1 → H3)

### Body Content
- **FULL primary keyword in first 100 words** — never broken up or rephrased
- FULL primary keyword must appear in at least 2 H2s
- Secondary keywords distributed naturally (don't force)
- Min 1.200 words for pillar/guide content
- Min 800 words for standard blog posts
- **All paragraphs: 1-3 lines max** — No paragraph may exceed 3 lines. Split if longer.
- Use bold for key terms on first mention
- **Internal links: EXACTLY 3** per post (from `links ESP.md` / `links ENG.md` ONLY)
- **External links: EXACTLY 3** per post (from `links ESP.md` / `links ENG.md` ONLY)
- Total per post: exactly 6 links (3 internal + 3 external), no more, no less
- ONLY use URLs from the links files — do not invent or add any external link
- Links inserted naturally using anchor text from the links files
- If no natural match for anchor text exists, write a subtle 1-2 sentence paragraph that blends in

### Images
- Alt text describing the image with keyword when natural
- File name descriptive (e.g., `proceso-certificacion-iso-27001.png`)
- Compress for web performance

## Content Structure for SEO

### PRIMARY: Listicle / "Best of" Queries (Default Format)
```
H1: Los X mejores [topic] en [year] (MAX 63 chars)
[Numbered index: 1. PrivaLex, 2. Competitor...]
[Introduction: 2-3 paragraphs with bold emphasis]
H2: Estos son los X mejores [topic]
  H3: 1. PrivaLex Partners (extended)
  H3: 2. [Competitor] (standard + Lo mejor/Lo peor)
  H3: 3. [Competitor] (standard + Lo mejor/Lo peor)
  ...
H2: [Contextual value section]
H2: [Decision criteria section]
H2: [X items — quantity in H2 — implementation]  ← MANDATORY, H3 for each item
H2: [X items — quantity in H2 — mistakes/timeline]  ← MANDATORY, H3 for each item
H2: Cómo puede ayudarte PrivaLex con [keyword]  ← ALWAYS penultimate
H2: Preguntas Frecuentes (FAQs)  ← ALWAYS this exact title (H2)
  H3: [Question 1]?  ← MUST be H3
  H3: [Question 2]?  ← MUST be H3
  H3: [Question 3]?  ← MUST be H3
  ... (5-6 questions minimum, ALL as H3, targeting primary keyword)
H2: [Final CTA]
```

### For "How to" Queries
```
H1: Cómo [action] [keyword] (MAX 63 chars)
H2: Paso 1: [First step]
H2: Paso 2: [Second step]
...
H2: Errores comunes
H2: Cómo puede ayudarte PrivaLex
H2: Preguntas Frecuentes (FAQs)  ← ALWAYS include
```

### For "What is" Queries
```
H1: ¿Qué es [keyword] y [why]? (MAX 63 chars)
H2: Definición y contexto
H2: Quién debe cumplir / A quién afecta
H2: Requisitos principales
H2: Cómo prepararse
H2: Preguntas Frecuentes (FAQs)  ← ALWAYS include
```

### For Comparison Queries
```
H1: [A] vs [B]: [Decision question] (MAX 63 chars)
H2: ¿Qué es [A]?
H2: ¿Qué es [B]?
H2: Principales diferencias (with table)
H2: ¿Cuál necesitas?
H2: Preguntas Frecuentes (FAQs)  ← ALWAYS include
```

### FAQ Section Rules (ALL formats — CRITICAL)
- Section title MUST be H2: `## **Preguntas Frecuentes (FAQs)**`
- English version: `## **Frequently Asked Questions (FAQs)**`
- **Each question MUST be H3**: `### **[Question]?**` — never H2, always H3
- Minimum 5-6 questions, ALL formatted as H3
- Questions MUST include/target the primary keyword
- Answers: 2-4 sentences, direct, actionable
- Optimized for Google FAQ rich snippet schema
- Questions should match real search queries
- Format example:
  ```markdown
  ## **Preguntas Frecuentes (FAQs)**

  ### **¿Qué es [primary keyword]?**
  
  [Answer]

  ### **¿Cuánto cuesta [related to keyword]?**
  
  [Answer]
  ```

## Internal & External Linking Strategy

### MANDATORY: 3 Internal + 3 External Links Per Post

Every post MUST contain exactly **3 internal links** and **3 external links** (6 total per language version).

### Link Source Files
- Spanish: `C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\links ESP.md`
- English: `C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\links ENG.md`

### Selection Rules
1. Read the corresponding links file
2. Choose the 3 internal + 3 external links that **best match the post's content**
3. Use the **exact anchor text** specified in the links file

### Insertion Rules
1. Find natural text in the post that matches or approximates the anchor text
2. Convert that text into a hyperlink
3. **If no natural match**: write a subtle 1-2 sentence paragraph that blends seamlessly with the surrounding content, incorporating the link with its anchor
4. Distribute links throughout (don't cluster)
5. NEVER place a link inside a heading (H1, H2, H3)

### Anchor Text Rules
- Use the anchor text specified in the links file
- If the exact anchor doesn't appear naturally, find the closest match or create a subtle insertion
- Never use "click here" or generic anchors

## Multilingual SEO

### Spanish Posts
- Primary target: Spain (es-ES)
- Secondary: LATAM (where applicable for regulatory content)
- Use Spain-specific terms (RGPD not GDPR, LOPDGDD, AEPD, FUNDAE)

### English Posts
- Target: EU-wide English speakers
- Use "organisation" (UK) for EU audiences
- Include both "GDPR" and framework-specific terms

### Hreflang Tags (when both versions exist)
- `es` version: primary for Spanish keywords
- `en` version: primary for English keywords
- Always link between translated versions

## Metadata Template

Use this EXACT format. NO quotes after colons. NO YAML frontmatter.

```
Title: [MAX 63 chars with FULL keyword]
Metadescripción: [MAX 135 chars, persuasive, with FULL keyword]
Slug: [keyword-only-slug, no extras]
Keyword: [exact primary keyword, secondary1, secondary2, secondary3]
```

**Rules:**
- NO quotes after the colons
- Title: max 63 characters
- Metadescripción: max 135 characters, MUST be persuasive (sell the click)
- Slug: ONLY the keyword as slug (e.g., "Bureau Veritas ISO 27001" → `bureau-veritas-iso-27001`)
- Keyword: primary keyword first, then secondaries comma-separated, no quotes, no bullet points

## Bilingual Content Strategy

Every blog post MUST be produced in both Spanish and English:

### Spanish Version (Primary)
- Created first
- Targets Spain-specific terms (RGPD, LOPDGDD, AEPD, FUNDAE, ENS)
- Index: only PrivaLex with link to `https://privalex.es/`
- Links from `links ESP.md`
- Saved as: `Aitor-private/Privalex/posts/[slug].md`

### English Version (Translation)
- Created after Spanish version is approved
- Targets EU-wide English audience
- Uses GDPR (not RGPD), adapts cultural references
- Index: only PrivaLex with link to `https://privalex.es/en/`
- Links from `links ENG.md`
- Competitor list may be adjusted for international relevance
- FUNDAE mentioned with context explanation
- Saved as: `Aitor-private/Privalex/posts/[slug-en].md`

### NO Promotional Content
Do NOT generate LinkedIn posts, newsletter snippets, or any promotional material. Only the blog posts.
