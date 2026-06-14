---
name: content-formats
description: Templates and patterns for each content format PrivaLex produces (blog, LinkedIn, newsletter, case study). Use when generating specific content types.
---

# Content Format Templates

Structure and patterns for each content type. Adapt to the message — don't fill in robotically.

---

## Blog Post Structure

### PRIMARY FORMAT: Listicle (Conversion-Oriented)

This is the **default and primary format** for all PrivaLex blog posts. All posts follow the "Los X mejores..." pattern, positioning PrivaLex as item #1.

**Key rules:**
- **CRITICAL: ALWAYS respect the exact keyword in the title** — If keyword is "software NIS2", use "software", NOT "herramientas"
- **Title format based on keyword pattern:**
  - If keyword = "[Company] + [Framework]" (e.g., "Vanta HIPAA") → "Mejores alternativas a [Company] [Framework]"
  - If keyword = "software + [Regulatory Framework]" (e.g., "software NIS2") → "Mejor software para facilitar el cumplimiento [Framework]"
  - If keyword = "[Framework]" only (e.g., "certificación ISO 27001") → "Mejores opciones para [action verb] con/en [Framework]"
- Title: MAX 63 characters, MUST include FULL primary keyword, MUST NOT contain colons (:), MUST sound natural and complete (like a real sentence)
- All paragraphs: 1-3 lines max, no exceptions
- **Bold emphasis: MINIMUM 2-3 bold phrases per paragraph** — Bold key terms, frameworks, numbers, critical concepts, proof points
- Meta description: MAX 135 characters, persuasive
- Slug: ONLY the keyword in slug format (no extras)
- Metadata format: `Title:` / `Metadescripción:` / `Slug:` / `Keyword:` — NO quotes after colons
- Keywords listed comma-separated, no bullet points, no quotes
- Introduction: proportional to title area (2-3 short paragraphs), MUST include FULL keyword
- PrivaLex always #1 with extended treatment (6+ paragraphs + bullet list)
- Index: ONLY PrivaLex gets a link (to home: ES=https://privalex.es/ EN=https://privalex.es/en/), rest plain text
- Competitors get standard treatment (3-4 paragraphs + "Lo mejor/Lo peor")
- **Main listicle H2 format (MUST respect exact keyword):**
  - If keyword = "[Company] + [Framework]" → `## **Estas son las X mejores alternativas a [Company] [Framework]**`
  - If keyword = "software + [Framework]" → `## **Este es el mejor software para facilitar el cumplimiento [Framework]**`
  - If keyword = "[Framework]" only → `## **Estas son las X mejores [consultoras/opciones] para [Framework]**`
- H2 sections that are listicles MUST include quantity in the H2, with H3 for each item inside
- MUST end with "Preguntas Frecuentes (FAQs)" section (exact title)
- MUST include numbered index at top
- Always create Spanish + English versions
- MUST include EXACTLY 3 internal links + EXACTLY 3 external links (from links ESP/ENG files only), inserted naturally
- NO promotional content generated (no LinkedIn, no newsletter snippets)
- FULL primary keyword must NEVER be broken up, rephrased, or substituted throughout the post

```markdown
Title: [Max 63 chars with FULL keyword]
Metadescripción: [Max 135 chars, persuasive, with FULL keyword]
Slug: [keyword-only-slug]
Keyword: [exact keyword, comma-separated secondaries]

# **[Title — max 63 chars with FULL primary keyword]**

Estas son las mejores [topic]:

1. [PrivaLex Partners](https://privalex.es/)
2. Competitor 2
3. Competitor 3
...
N. Competitor N

[Hook: Question or pain point — bold key phrases]

[Context: Why this matters for the reader's business — bold key phrases]

[Transition to listicle + disclaimer about ordering]

## **Estas son las X mejores [alternativas a Empresa Framework / opciones para Framework]**

### **1. PrivaLex Partners**

[6+ paragraphs: Detailed description, methodology, experience, differentiators]
[Include: +205 clients, 14 countries, 7+ years, client logos, FUNDAE]

Algunos puntos fuertes de PrivaLex Partners:

* [Strength 1 — specific]
* [Strength 2 — specific]
* [Strength 3 — specific]
* [Strength 4 — specific]
* [Strength 5 — specific]
* [Strength 6 — specific]

### **2. [Competitor Name]**

[3-4 paragraphs: Who they are, what they offer, real quote if available]

**En resumen:**

**Lo mejor:** [strengths list]

**Lo peor:** [weaknesses list — factual, fair]

### **3. [Competitor Name]**

[Same structure as #2]

...

## **[Contextual section — why this matters]**

[3-5 paragraphs adding market context, regulatory pressure]

## **[How to choose / Decision criteria]**

[Practical evaluation guidance with subsections]

## **[X items — quantity in H2 — practical implementation]**

### **1. [Item]**
[Paragraph 1: Explain the concept — 1-3 lines]
[Paragraph 2: Why it matters — 1-3 lines]
[Paragraph 3 (optional): How to apply it — 1-3 lines]

### **2. [Item]**
[2-3 paragraphs with substantive content — NEVER just one sentence]
...

## **[X items — quantity in H2 — common mistakes or timeline]**

### **1. [Item]**
[Paragraph 1: Describe the mistake/phase — 1-3 lines]
[Paragraph 2: Context or impact — 1-3 lines]
[Paragraph 3 (optional): Recommendation — 1-3 lines]

### **2. [Item]**
[2-3 paragraphs with substantive content — NEVER just one sentence]
...

## **Cómo puede ayudarte PrivaLex con [keyword]**

[Paragraph 1: Empathize with the reader's challenge — 1-3 lines]

[Paragraph 2: How PrivaLex solves this differently — 1-3 lines]

[Paragraph 3: Specific proof points (clients, experience, methodology) — 1-3 lines]

[Paragraph 4: Credibility (verticals, success stories) — 1-3 lines]

[Paragraph 5: Clear CTA — 1-3 lines]

**[Agenda una sesión estratégica con PrivaLex](https://privalex.es/contacto/)** y descubre cómo [specific benefit].

(English: **[Schedule a strategic session with PrivaLex](https://privalex.es/en/contact/)** and discover how [specific benefit].)

## **Preguntas Frecuentes (FAQs)**

### **[Question 1 targeting primary keyword]?**

[Answer — 2-4 sentences, direct]

### **[Question 2 targeting primary keyword]?**

[Answer — 2-4 sentences, direct]

### **[Question 3 targeting primary keyword]?**

[Answer — 2-4 sentences, direct]

[5-6 questions total minimum — ALL as H3 — optimized for Google rich snippets]
[Questions MUST include FULL primary keyword]

## **[Final CTA section]**

[Short motivating close + clear call-to-action]

LINKS: 3 internal + 3 external distributed throughout (from links ESP/ENG files)
```

### SECONDARY FORMAT: Compliance Guide / How-To

Use only when the user specifically requests a non-listicle format.

```markdown
# [Specific outcome or question] — [Framework reference if applicable]

[Hook: The real problem or question your audience is asking — 1-2 sentences]

[Why this matters: business impact, regulatory pressure, or market reality — 1 paragraph max]

## [Section 1: Core concept or first step — H2 with secondary keyword]

[Content: Explain with specifics. Reference clauses, controls, or requirements.]

[Quote or callout if applicable]

### [Subsection: Practical detail — H3 if needed]

[Bullets, examples, or checklist items]

## [Section 2: Next step or deeper dive]

[Content with practical guidance]

## [Section 3: Common mistakes or advanced considerations]

[Content addressing skepticism or misconceptions]

## Cómo puede ayudarte PrivaLex

[1-2 paragraphs: Specific to the topic. Not generic.]

[CTA: Clear, specific next step]

## **Preguntas Frecuentes (FAQs)**

[5-6 questions targeting primary keyword — ALWAYS include this section]
```

### SECONDARY FORMAT: Framework Comparison

```markdown
# [Framework A] vs [Framework B]: [Practical question — max 63 chars]

[Hook: Why this comparison matters — business context]

## Qué cubre [Framework A]

[Focused description with specific references]

## Qué cubre [Framework B]

[Focused description with specific references]

## Principales diferencias

| Característica | [Framework A] | [Framework B] |
|----------------|---------------|---------------|
| Enfoque | ... | ... |
| Ámbito | ... | ... |
| Certificación | ... | ... |
| Obligatoriedad | ... | ... |

## ¿Cuál necesita tu empresa?

[Decision framework based on sector, size, market, regulatory pressure]

## Conclusión

[Brief, actionable takeaway — not a repeat of the intro]

[CTA]

## **Preguntas Frecuentes (FAQs)**

[5-6 questions targeting primary keyword — ALWAYS include this section]
```

---

## LinkedIn Post Structure

### Thought Leadership / Insight

```
[Hook: Contrarian take, surprising stat, or provocative question]

[2-3 short paragraphs with line breaks between them]

[Practical insight or lesson from experience]

[Soft CTA: question to audience or link to resource]

#ISO27001 #Ciberseguridad #Compliance #RGPD #Startups
```

**Rules:**
- Max 1.300 characters for main body
- One idea per post
- Line breaks between every paragraph (readability on mobile)
- Max 5 hashtags
- No link in main body if possible (kills reach); put in first comment

### Client Win / Case Reference

```
[Opening: The challenge or context — anonymized if needed]

[What we did — specific, not vague]

[Result — with metric or tangible outcome if possible]

[Takeaway for the reader]

[Soft CTA]
```

### Regulatory Update / News

```
[What changed — in plain language]

[Who's affected]

[What to do about it — 2-3 actionable points]

[Link to full article in first comment]
```

---

## Newsletter / Email Structure

### Monthly Update

```
Subject: [Specific topic] — [Month] update de PrivaLex

[Nombre],

[One sentence: What's the theme or most important thing this month]

**Lo más destacado:**
• **[Topic 1]** — [One-line description with value]
• **[Topic 2]** — [One-line description]
• **[Topic 3]** — [One-line description]

**Del blog:**
• [Blog post title](link) — [One sentence summary]
• [Blog post title](link) — [One sentence summary]

**Próximos eventos / deadlines:**
• [Relevant regulatory deadline or event]

[Sign-off — personal, from a named person]
```

### Single-Topic Email

```
Subject: [Clear benefit or specific topic]

[Nombre],

[2-3 sentences: Why this matters RIGHT NOW]

[Key points — bullets or short paragraphs]

[Single clear CTA]

[Sign-off]
```

**Rules:**
- Subject line: specific and benefit-oriented, under 60 characters
- Body: under 200 words
- One CTA only
- Signed by a real person (not "El equipo de PrivaLex")

---

## Case Study Structure

```markdown
# [Client name or anonymous descriptor]: [Outcome achieved]

## El reto

[1-2 paragraphs: What the client needed and why]

- Sector: [Industry]
- Tamaño: [Employees / revenue range]
- Marco normativo: [ISO 27001, RGPD, etc.]
- Situación inicial: [Brief description of starting point]

## La solución

[What PrivaLex did — specific services, approach, timeline]

### Fase 1: [Assessment / Gap Analysis]
[Brief description]

### Fase 2: [Implementation]
[Brief description]

### Fase 3: [Audit / Certification]
[Brief description]

## Los resultados

| Métrica | Antes | Después |
|---------|-------|---------|
| [Metric 1] | [Value] | [Value] |
| [Metric 2] | [Value] | [Value] |

> "[Client quote if available]"
> — [Name, Title, Company]

## Conclusión

[1-2 sentences: What this proves about PrivaLex's approach]

[CTA]
```

---

## Whitepaper / Guide Structure

```markdown
# [Title: Specific, keyword-rich]

## Resumen ejecutivo

[3-5 sentences summarizing the entire guide]

## Índice

1. [Section 1]
2. [Section 2]
...

## [Section 1: Context and Problem]

[Deep content with data, references, regulatory context]

## [Section 2: Framework / Approach]

[Structured methodology or analysis]

## [Section 3: Practical Application]

[How-to, checklists, templates]

## [Section 4: PrivaLex Perspective]

[Expert opinion, differentiated approach]

## Conclusión y próximos pasos

[Actionable takeaways]

## Sobre PrivaLex Partners

[Standard boilerplate — 3 sentences max]
```

---

## Twitter/X Thread Structure (Optional)

```
1/ [Hook: Problem or insight] 🧵

2/ [Context: Why this matters now]

3/ [Key point 1 — practical]

4/ [Key point 2 — practical]

5/ [Key point 3 — practical]

6/ [Takeaway + CTA]
```

**Rules:**
- Max 7 tweets
- Each tweet must stand alone
- No excessive emojis (max 1 per tweet)
- Link to full resource in last tweet
