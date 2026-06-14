# Generate PrivaLex Blog Post

Generate a listicle-style, conversion-oriented, SEO-optimized blog post for PrivaLex Partners.

**Activation command:** `/generate-privalex-blog-post [keyword]`

## Instructions

You are generating blog content for PrivaLex Partners. Load these skills for guidance:

- `privalex-voice-and-tone` — Professional, trustworthy, anti-fluff guardrails
- `compliance-frameworks` — Technical accuracy on ISO 27001, NIS2, RGPD, DORA, ENS, etc.
- `content-formats` — Blog post structure templates
- `seo-guidelines` — Keyword strategy and on-page optimization
- `target-personas` — Audience profiles (CISO, CTO, DPO, Startup Founder)
- `privalex-product` — Services, differentiators, proof points
- `examples-hall-of-fame` — Reference examples for tone and quality
- `competitive-landscape` — Positioning vs competitors

---

## CRITICAL RULE: Paragraph Length

**Every paragraph in the post MUST be between 1 and 3 lines long.** No exceptions. If a paragraph exceeds 3 lines, split it into two. This applies to ALL sections: introduction, listicle items, value sections, FAQs, CTA — everything.

---

## CRITICAL RULE: Bold Emphasis

**Use bold formatting extensively throughout the post to improve readability and highlight key concepts.**

- **Minimum 2-3 bold phrases per paragraph** (can be more)
- Bold key terms, important concepts, numbers, and critical phrases
- Bold framework names (NIS2, ISO 27001, HIPAA, GDPR, etc.)
- Bold company names when first mentioned
- Bold critical deadlines, requirements, or obligations
- Bold proof points (client numbers, years of experience, countries)
- Use bold for emphasis in lists and bullet points
- **DO NOT over-bold** — not every word, but strategic emphasis

**Examples:**
- "La **Directiva NIS2** exige **notificación de incidentes en menos de 24 horas**"
- "PrivaLex ha trabajado con **más de 205 clientes en 14 países**"
- "Las **entidades esenciales** enfrentan sanciones de hasta **€10 millones o el 2% de la facturación global**"

---

## CRITICAL RULE: Keyword Integrity

The **primary keyword MUST appear complete and exact** throughout the post. If the keyword is "Bureau Veritas ISO 27001", that exact phrase must appear in:
- The title (H1)
- The introduction (first 100 words)
- At least 2 H2 headings
- The FAQ questions
- The meta description

NEVER substitute, rephrase, or break up the keyword. "Bureau Veritas ISO 27001" ≠ "certificación ISO 27001". The full keyword must be respected at all times.

---

## Post Format: Listicle (MANDATORY)

ALL blog posts MUST follow the listicle format. The style is "Los X mejores [software/herramientas/consultoras/soluciones]..." where PrivaLex is ALWAYS positioned as option #1 with significantly more detailed content than the rest.

---

## Step 1: Understand the Topic and Keyword Pattern

Ask the user (if not already provided):

1. **Primary keyword** — The SEO keyword to target (e.g., "Bureau Veritas ISO 27001", "Vanta HIPAA", "software NIS2")
2. **Detect keyword pattern and appropriate focus:**
   
   - If keyword = **"[Company/Brand] + [Framework/Regulation]"** (e.g., "Vanta HIPAA", "Bureau Veritas ISO 27001") → Enfoque: **"Alternativas a [Company]"**
   
   - If keyword = **"software + [Regulatory Framework]"** (e.g., "software NIS2", "software HIPAA", "software DORA") → Enfoque: **"Mejor software para facilitar el cumplimiento [Framework]"** (MUST use "software" to respect keyword, NOT "herramientas" — but clarify in content that compliance requires processes, not just tools)
   
   - If keyword = **"[Framework/Certification]"** only (e.g., "certificación ISO 27001", "cumplimiento HIPAA") → Enfoque: **"Mejores opciones para [action] con [Framework]"**

3. **Target audience** — Who is the primary reader? (CISO / CTO / DPO / Startup Founder / Compliance Officer)
4. **Number of items** — How many items in the listicle? (default: 8)
5. **CTA** — What should the reader do next? (Book consultation / Download guide / Contact)

**CRITICAL: Always respect the EXACT keyword in the title.**

**Examples:**
- "Vanta HIPAA" → "Mejores alternativas a Vanta HIPAA para healthtech"
- "software NIS2" → "Mejor software para facilitar el cumplimiento NIS2" (respects "software")
- "software HIPAA" → "Mejor software para facilitar el cumplimiento HIPAA" (respects "software")
- "software ENS" → "Mejor software para facilitar el cumplimiento ENS" (respects "software")
- "certificación ISO 27001" → "Mejores opciones para certificarte en ISO 27001"

---

## Step 2: Research from RAG Context (MANDATORY — DO THIS BEFORE ANYTHING ELSE)

**CRITICAL: You MUST research the RAG context BEFORE creating the outline or writing any content.**

Search the PrivaLex content library using `Grep` or `SemanticSearch`:

```
Search in: C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\
```

**REQUIRED SEARCHES (perform ALL of these):**

1. **Search for the primary keyword** (e.g., "HIPAA", "ISO 27001", "Vanta", "Bureau Veritas")
   - Use `Grep` for exact matches
   - Use `SemanticSearch` for conceptual understanding
2. **Search for competitors** mentioned in the keyword (if applicable)
   - Check `PrivaLex Competition (1).md` and `privalex vs [competitor].md` files
3. **Search for framework/regulation** details to ensure technical accuracy
4. **Search for "PrivaLex" + keyword** to find specific positioning and differentiators
5. **Extract proof points** — Client count, countries, years of experience, specific certifications delivered, FUNDAE capability

**What to extract and validate:**
- How PrivaLex compares to alternatives mentioned in the keyword
- Product capabilities for this specific framework/topic
- Client references and proof points
- Technical accuracy on the framework/regulation
- Specific differentiators vs. competitors

**DO NOT proceed to Step 3 (outline) until you have solid, specific context from the RAG.**

**Important:** Always ground content in the existing RAG context. Do NOT invent facts, statistics, or claims not supported by the source material or publicly verifiable information.

---

## Step 3: Research Competitors for the Listicle

For the other items in the listicle (positions 2-N), research real competitors or tools relevant to the topic. Sources:

- RAG context files: `PrivaLex Competition (1).md`, `privalex vs vanta.md`
- Known competitors: Vanta, OneTrust, Across Legal, Legal Army, ECIJA, Govertis, GlobalSuite
- Relevant software: Vanta, Drata, Secureframe, Sprinto, OneTrust, TrustArc, etc.
- Load `competitive-landscape` skill for positioning guidance

Each competitor entry must be factual and fair — no FUD, no invented claims.

---

## Step 4: Build the Post Outline

Present the outline to the user BEFORE writing:

```markdown
## Post Outline

**Title (H1):** [Max 63 characters, includes FULL primary keyword]
**Primary keyword:** [keyword — exact, complete]
**Secondary keywords:** [2-3 keywords]
**Target audience:** [Persona]
**Number of items:** [N]

### Structure:
1. Title (H1) — max 63 chars, MUST include full keyword
2. Numbered index (1-N list, only PrivaLex with link to home)
3. Introduction — same length as title area (~2-3 short paragraphs), MUST include full keyword
4. H2: "Estos son los X mejores [topic]"
   - H3: 1. PrivaLex Partners (EXTENDED — 6+ paragraphs + bullet list)
   - H3: 2. [Competitor] (standard — 3-4 paragraphs + Lo mejor/Lo peor)
   - H3: 3. [Competitor] (standard)
   - ... up to N
5. H2: [Contextual section — why this matters]
6. H2: [Decision criteria / how to choose]
7. H2: [Listicle section with quantity in H2 — e.g. "5 errores comunes al..."]
   - H3: Error 1 / Paso 1 / etc.
   - H3: Error 2 / Paso 2 / etc.
   - ...
8. H2: [Another listicle section with quantity in H2 — e.g. "9 fases del proceso..."]
   - H3: Fase 1 / Elemento 1 / etc.
   - H3: Fase 2 / Elemento 2 / etc.
   - ...
9. H2: "Cómo puede ayudarte PrivaLex con [keyword]" — ALWAYS penultimate
10. H2: "Preguntas Frecuentes (FAQs)" — 5-6 questions for rich snippets
11. Final CTA section
```

Wait for user approval or modifications before writing.

---

## Step 5: Write the Post (Spanish Version)

### MANDATORY STRUCTURE — Follow this exactly:

#### A. Metadata Block
Place at the very top of the file using this EXACT format (NO quotes after the colons):

```
Title: [Max 63 chars with full keyword]
Metadescripción: [Max 135 chars, persuasive, with full keyword]
Slug: [keyword-only, lowercase, hyphens, no accents]
Keyword: [primary keyword as-is, no quotes]
```

**METADATA RULES:**
- NO quotes after the colons
- Title: max 63 characters
- **Title MUST NOT contain colons (:)** — Never use "keyword: subtitle" structure
- **Title MUST sound natural and complete** — It should read like a natural sentence, not feel truncated or awkward
- **Title format depends on keyword pattern (ALWAYS respect the exact keyword):**
  - If keyword = "[Company] + [Framework]" → "Mejores alternativas a [Company] [Framework]"
  - If keyword = "software + [Regulatory Framework]" → "Mejor software para facilitar el cumplimiento [Framework]" (MUST use "software")
  - If keyword = "[Framework/Certification]" only → "Mejores opciones para [action verb] con/en [Framework]"
- Examples:
  - "Vanta HIPAA" → "Mejores alternativas a Vanta HIPAA para healthtech"
  - "software NIS2" → "Mejor software para facilitar el cumplimiento NIS2"
  - "software HIPAA" → "Mejor software para facilitar el cumplimiento HIPAA"
  - "software ENS" → "Mejor software para facilitar el cumplimiento ENS"
  - "certificación ISO 27001" → "Mejores opciones para certificarte en ISO 27001"
- Metadescripción: max 135 characters, MUST be persuasive (sell the click)
- Slug: ONLY the keyword converted to slug format (e.g., keyword "Bureau Veritas ISO 27001" → slug: bureau-veritas-iso-27001)
- Keyword: the exact primary keyword, no modifications
- Keywords list: comma-separated, no bullet points, no quotes

#### B. Title (H1)
- **Maximum 63 characters** including spaces
- MUST include the **full primary keyword exactly as given**
- **MUST NOT contain colons (:)** — Use natural phrasing without ":" separators
- **MUST sound natural and complete** — Like a real sentence, not truncated
- **Format based on keyword pattern (MUST respect exact keyword):**
  - "[Company] + [Framework]" → "Mejores alternativas a [full keyword]"
  - "software + [Regulatory Framework]" → "Mejor software para facilitar el cumplimiento [Framework]" (use "software")
  - "[Framework/Certification]" only → "Mejores opciones para [action] con/en [Framework]"
- Examples:
  - "Vanta HIPAA" → "Mejores alternativas a Vanta HIPAA para healthtech"
  - "software NIS2" → "Mejor software para facilitar el cumplimiento NIS2"
  - "software HIPAA" → "Mejor software para facilitar el cumplimiento HIPAA"
  - "software ENS" → "Mejor software para facilitar el cumplimiento ENS"
  - "certificación HIPAA" → "Mejores opciones para cumplir con HIPAA"
- Use sentence case
- Format: `# **[Title]**`

#### C. Numbered Index
Immediately after the title, include a numbered list. **ONLY PrivaLex gets a link** (to the home page). All other items are plain text, no links:

```markdown
Estas son las mejores opciones para [keyword]:

1. [PrivaLex Partners](https://privalex.es/)
2. Competitor 2
3. Competitor 3
...
N. Competitor N
```

#### D. Introduction
- **Same visual length as the title area** — approximately 2-3 short paragraphs
- Open with a question or pain point the reader is asking
- **MUST include the full primary keyword** in the first 100 words
- **Use bold extensively: MINIMUM 2-3 bold phrases per paragraph** — Bold frameworks, key terms, numbers, critical concepts
- Explain why this choice matters for the reader's business
- End with a transition sentence to the listicle
- Include a disclaimer: "(Ten en cuenta que las opciones mencionadas en esta lista no están ordenadas bajo ningún criterio específico, salvo indicación contraria)"

#### E. Main Listicle Section
**Format depends on keyword pattern (MUST include exact keyword):**
- If keyword = "[Company] + [Framework]" → `## **Estas son las X mejores alternativas a [Company] [Framework]**`
- If keyword = "software + [Regulatory Framework]" → `## **Este es el mejor software para facilitar el cumplimiento [Framework]**` (use "software")
- If keyword = "[Framework/Certification]" only → `## **Estas son las X mejores [consultoras/opciones] para [Framework]**`

Examples:
- "Vanta HIPAA" → `## **Estas son las 8 mejores alternativas a Vanta HIPAA**`
- "software NIS2" → `## **Este es el mejor software para facilitar el cumplimiento NIS2**`
- "software HIPAA" → `## **Este es el mejor software para facilitar el cumplimiento HIPAA**`
- "software ENS" → `## **Este es el mejor software para facilitar el cumplimiento ENS**`
- "certificación ISO 27001" → `## **Estas son las 10 mejores consultoras para certificarte en ISO 27001**`

##### Item #1: PrivaLex Partners (EXTENDED TREATMENT)
- **6+ paragraphs** of detailed description
- **Use bold extensively throughout: frameworks, proof points, key differentiators, numbers**
- Cover: what PrivaLex does, methodology, team, experience, differentiators
- Include specific proof points: **+205 clients, 14 countries, 7+ years**, client logos
- Mention **FUNDAE** capability if relevant
- Reference specific frameworks and certifications with **bold**
- **End with a bullet list** of key strengths (each bullet should have bold emphasis):

```markdown
Algunos puntos fuertes de PrivaLex Partners:

* [Strength 1 — specific and factual]
* [Strength 2 — specific and factual]
* [Strength 3 — specific and factual]
* [Strength 4 — specific and factual]
* [Strength 5 — specific and factual]
* [Strength 6 — specific and factual]
```

##### Items #2-N: Competitors (STANDARD TREATMENT)
Each competitor follows this structure:
- **3-4 paragraphs** describing who they are and what they offer
- **Use bold for key features, frameworks, and differentiators** (minimum 2-3 per paragraph)
- Include a real user quote or factual claim when available
- End with "**En resumen:**" block:

```markdown
**En resumen:**

**Lo mejor:** [comma-separated list of strengths]

**Lo peor:** [comma-separated list of weaknesses — factual and fair]
```

#### F. Contextual Value Section
- `## **[Why this topic matters — contextual H2]**`
- 3-5 paragraphs adding context, market trends, regulatory pressure
- **Use bold for key statistics, trends, deadlines, and critical concepts** (minimum 2-3 per paragraph)
- Connect to the reader's business reality

#### G. Decision Criteria Section
- `## **[How to choose / What to consider — H2]**`
- Practical guidance on evaluating options
- **Use bold for key criteria, decision factors, and important considerations** (minimum 2-3 per paragraph)
- Can include subsections (H3) for different criteria
- Use bullet lists for clarity

#### H. Listicle Value Section #1 (MANDATORY — H2 WITH QUANTITY + H3 ITEMS)
- **The H2 MUST include the quantity of items** in the listicle within it
- Example: `## **9 fases del proceso de certificación ISO 27001**`
- Example: `## **5 errores comunes al certificarse en ISO 27001**`
- **Each item within MUST be an H3 heading**
- **CRITICAL: Each H3 item MUST contain 2-3 paragraphs (1-3 lines each) — NEVER just one sentence**
- Content must be natural, coherent, and add real value
- Example:
```markdown
## **5 errores comunes al certificarse en ISO 27001**

### **1. Intentar certificarse sin partner de implementación**

[Paragraph 1: Explain the mistake — 1-3 lines]

[Paragraph 2: Why it's problematic — 1-3 lines]

[Paragraph 3 (optional): What to do instead — 1-3 lines]

### **2. Documentación excesiva o inadecuada**

[2-3 paragraphs with substantive content...]

### **3. No formar al equipo adecuadamente**

[2-3 paragraphs with substantive content...]
```

#### I. Listicle Value Section #2 (MANDATORY — H2 WITH QUANTITY + H3 ITEMS)
- Same rules as Section H: H2 with quantity, H3 for each item
- **CRITICAL: Each H3 item MUST contain 2-3 paragraphs (1-3 lines each) — NEVER just one sentence**
- Different topic from Section H
- Example: `## **Las 9 fases del proceso completo de certificación ISO 27001**`
- Example: `## **7 criterios para elegir el mejor certificador ISO 27001**`

#### J. PrivaLex Solution Section (MANDATORY — ALWAYS PENULTIMATE)
- `## **Cómo puede ayudarte PrivaLex con [keyword/topic]**`
- This section ALWAYS goes just before the FAQs (penultimate position)
- **MUST be persuasive and conversion-oriented** — This is a critical conversion point
- **4-5 paragraphs (1-3 lines each)**, directly addressing the reader's pain point from the post
- Start with empathy: acknowledge the challenge/frustration the reader faces
- Explain specifically how PrivaLex solves this problem differently than competitors
- Include specific proof points: client count, experience, methodology, success rate
- Add credibility: mention specific clients (if allowed) or verticals served
- **End with a clear, action-oriented CTA:**
  - Spanish: `**[Agenda una sesión estratégica con PrivaLex](https://privalex.es/contacto/)** y descubre cómo [specific benefit related to keyword].`
  - English: `**[Schedule a strategic session with PrivaLex](https://privalex.es/en/contact/)** and discover how [specific benefit related to keyword].`
- Tone: Confident but not pushy, helpful, results-focused

#### K. FAQ Section (MANDATORY — EXACT TITLE AND FORMAT)
```markdown
## **Preguntas Frecuentes (FAQs)**

### **[Question 1 targeting FULL primary keyword]?**

[Direct answer — 2-4 sentences]

### **[Question 2 targeting FULL primary keyword]?**

[Direct answer — 2-4 sentences]

### **[Question 3 targeting FULL primary keyword]?**

[Direct answer — 2-4 sentences]
```

**CRITICAL RULES:**
- Section title MUST be H2: `## **Preguntas Frecuentes (FAQs)**`
- Each question MUST be H3: `### **[Question]?**`
- Include **5-6 questions minimum**
- Questions must include the FULL primary keyword for Google rich snippets
- Each answer: 2-4 sentences, direct, actionable

#### L. Final CTA Section
- Short, motivating closing (2-3 sentences)
- Clear call-to-action linking to contact page:
  - Spanish: `**[agenda una sesión estratégica con PrivaLex](https://privalex.es/contacto/)**`
  - English: `**[schedule a strategic session with PrivaLex](https://privalex.es/en/contact/)**`
- Confident but not pushy tone

---

## Step 6: Internal & External Links (MANDATORY)

After writing the post, you MUST add links to each language version. The rules are strict:

### STRICT LINK COUNT: Exactly 3 internal + 3 external = 6 total per post

- **Spanish post:** exactly 3 internal + 3 external = 6 links total
- **English post:** exactly 3 internal + 3 external = 6 links total
- **NO MORE, NO LESS.** Count carefully before finalizing.

### Link Source Files (ONLY use links from these files)
- **Spanish links:** `C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\links ESP.md`
- **English links:** `C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\links ENG.md`

You MUST use ONLY the URLs provided in these files. Do NOT invent or add any link that isn't listed in the corresponding file.

### Link Selection Rules
1. Read the corresponding links file (ESP for Spanish post, ENG for English post)
2. Choose exactly **3 internal links** and exactly **3 external links** that best match the post's content
3. Use the **exact anchor text specified** in the links file for each link
4. Use the **exact URL** provided in the links file — do not modify URLs

### Link Insertion Rules
1. Search the post for natural occurrences of text that match or approximate the anchor text
2. Convert that text into a hyperlink using the URL from the links file
3. **If no natural match exists**: Write a very subtle, short paragraph (1-2 sentences) that fits naturally into the section's context, incorporating the anchor text with the link
4. The inserted text MUST blend seamlessly — it should not feel forced or out of place
5. Distribute links throughout the post (don't cluster them all in one section)
6. Never place a link inside a heading (H1, H2, H3)

---

## Step 7: Quality Check

Before presenting, verify ALL of these:

### Structure Compliance
- [ ] Title is MAX 63 characters and includes FULL primary keyword
- [ ] Title does NOT contain colons (:) and sounds natural/complete
- [ ] Metadata uses correct format (Title/Metadescripción/Slug/Keyword, no quotes)
- [ ] Metadescripción is MAX 135 characters and persuasive
- [ ] Slug is ONLY the keyword in slug format
- [ ] Numbered index at top (only PrivaLex with link to home)
- [ ] Introduction includes FULL primary keyword in first 100 words
- [ ] PrivaLex is item #1 with extended treatment (6+ paragraphs + bullet list)
- [ ] Other items have "En resumen" with "Lo mejor" / "Lo peor"
- [ ] Listicle sections (H, I) have quantity in H2 and H3 for each item
- [ ] FAQ section exists with EXACT title "Preguntas Frecuentes (FAQs)"
- [ ] FAQ questions include FULL primary keyword
- [ ] FAQ has 5-6 questions as H3
- [ ] "Cómo puede ayudarte PrivaLex con [keyword]" section exists as penultimate (before FAQs)
- [ ] Final CTA section exists
- [ ] ALL paragraphs are 1-3 lines max (no paragraph exceeds 3 lines)
- [ ] Bold text used for emphasis (2-3 per paragraph)
- [ ] Bullet lists present throughout
- [ ] EXACTLY 3 internal links + EXACTLY 3 external links inserted (6 total, no more, no less)
- [ ] All links come from the links ESP/ENG files (no invented links)
- [ ] All anchors match those specified in the links files

### Keyword Compliance
- [ ] Full primary keyword appears in H1
- [ ] Full primary keyword appears in first 100 words
- [ ] Full primary keyword appears in at least 2 H2s
- [ ] Full primary keyword appears in FAQ questions
- [ ] Full primary keyword appears in meta description
- [ ] Keyword is NEVER broken up, rephrased, or substituted

### Voice & Tone
- [ ] No banned words or phrases (from skill)
- [ ] Sounds like PrivaLex, not generic
- [ ] Professional but approachable
- [ ] Competitor descriptions are fair — no FUD

### Technical Accuracy
- [ ] All framework references correct
- [ ] No contradictions with RAG content
- [ ] Regulatory dates and deadlines current

### SEO
- [ ] Primary keyword in title, first paragraph, H2s
- [ ] Meta description under 135 chars and persuasive
- [ ] Slug is only the keyword
- [ ] FAQ questions target full primary keyword for rich snippets

### Conversion Orientation
- [ ] PrivaLex clearly positioned as best option
- [ ] Proof points included (clients, experience, certifications)
- [ ] CTA is clear and actionable
- [ ] FUNDAE mentioned if relevant

---

## Step 8: Translate to English

After the Spanish version is approved, create an English translation:

### Translation Rules
- Translate the FULL post maintaining the exact same structure
- Adapt for EU-wide English audience (not US-specific)
- Use "organisation" (UK spelling) for EU context
- Keep framework names as-is (ISO 27001, GDPR, NIS2 — use GDPR not RGPD)
- Translate "Preguntas Frecuentes (FAQs)" to "Frequently Asked Questions (FAQs)" — KEEP THE EXACT SAME STRUCTURE
- Adapt cultural references (FUNDAE is Spain-specific — mention it but explain context)
- Adapt competitor list if needed for international audience
- Generate separate English metadata

### English Metadata
Same format, no quotes after colons:
```
Title: [Max 63 chars — English, with full keyword]
Metadescripción: [Max 135 chars — English, persuasive]
Slug: [keyword-in-english-slug-format]
Keyword: [primary keyword in English]
```

### English Index
Only PrivaLex gets a link, using the English home URL:
```markdown
1. [PrivaLex Partners](https://privalex.es/en/)
2. Competitor 2
...
```

### English Links
Use `links ENG.md` file for the English version's 3 internal + 3 external links.

---

## Step 9: Save Files

Save both versions in the posts folder:

```
C:\Users\aitor\blog-content\Aitor-private\Privalex\posts\
├── [slug-es].md          ← Spanish version
└── [slug-en].md          ← English version
```

Slug = keyword only. Example:
- Spanish: `bureau-veritas-iso-27001.md`
- English: `bureau-veritas-iso-27001.md` (if same keyword) or English equivalent

**NO promotional file is generated.** Do NOT create LinkedIn posts, newsletter snippets, or any promotional content.

---

## Step 10: Present and Iterate

Present the full output in this order:

1. **Blog post — Spanish** (complete with metadata + links)
2. **Blog post — English** (complete with metadata + links)
3. **Links used** (list of 6 links per version with their locations in the post)

Ask for feedback and adjust as needed. Apply voice-and-tone guardrails to every revision.

---

## Reference: Post Structure Summary

```
Title: [max 63 chars, FULL keyword, NO colons, sounds natural]
Metadescripción: [max 135 chars, persuasive]
Slug: [keyword-only-slug]
Keyword: [exact keyword, no quotes]

# **Title (max 63 chars, FULL keyword, NO colons, natural)**← H1

Estas son las mejores [topic]:                             ← Numbered index
1. [PrivaLex Partners](https://privalex.es/)               ← Only link
2. Competitor
...

[Introduction — 2-3 paragraphs, bold, FULL keyword]        ← Hook + context

## **Estos son los X mejores [topic]**                     ← H2 Main section

### **1. PrivaLex Partners**                               ← H3 EXTENDED (6+ paragraphs)
[Detailed description]
[Bullet list of strengths]

### **2. [Competitor]**                                    ← H3 Standard (3-4 paragraphs)
[Description]
**En resumen:**
**Lo mejor:** ...
**Lo peor:** ...

### **3. [Competitor]**                                    ← H3 Standard
...

## **[Contextual section]**                                ← H2 Value

## **[How to choose]**                                     ← H2 Decision criteria

## **[X errores/pasos/fases — quantity in H2]**            ← H2 Listicle section 1
### **1. [Item]**                                          ← H3
### **2. [Item]**                                          ← H3
...

## **[X criterios/fases/claves — quantity in H2]**         ← H2 Listicle section 2
### **1. [Item]**                                          ← H3
### **2. [Item]**                                          ← H3
...

## **Cómo puede ayudarte PrivaLex con [keyword]**          ← H2 ALWAYS PENULTIMATE
[2-3 short paragraphs, specific to the post's topic]

## **Preguntas Frecuentes (FAQs)**                         ← H2 EXACT TITLE

### **[Question with FULL keyword]?**                      ← H3 FAQ
[Answer]

### **[Question with FULL keyword]?**                      ← H3 FAQ
[Answer]
...

## **[Final CTA section]**                                 ← H2 Closing
[Motivating close + CTA]

ALL paragraphs: 1-3 lines max. No exceptions.

LINKS: EXACTLY 3 internal + EXACTLY 3 external (from links files only)
```

---

## User Input

$ARGUMENTS
