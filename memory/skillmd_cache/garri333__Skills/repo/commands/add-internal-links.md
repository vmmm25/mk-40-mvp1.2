# Add Internal Links to Post

You are tasked with adding internal links between PrivaLex blog posts using the existing content library as reference.

## Process

Follow these steps in order:

### 1. Analyze the Current Post

- Read the current blog post thoroughly
- Identify the main topics, frameworks, and keywords
- Summarize the post into **2-3 keywords or phrases** that capture its core themes
- Document these keywords clearly

### 2. Search for Related Posts

Search all markdown files in the PrivaLex content library:

```
Search in: C:\Users\aitor\blog-content\Aitor-private\Privalex\privalex context\
```

Search for the identified keywords and related terms. Look for posts that discuss:
- The same compliance framework (ISO 27001, NIS2, RGPD, etc.)
- Related topics (audits, training, documentation, risk assessment)
- The same target audience (startups, CTOs, DPOs)
- Complementary topics (e.g., if current post is about ISO 27001 certification, find posts about audits, controls, training)

Create a list of **5-10 most relevant posts** with their:
- File name
- Title
- Main topic
- Relevance to the current post

### 3. Add Links Strategically

Add links from the current post to related posts where they add value:

**Option A: Existing Anchor Text**
- Search for natural anchor text in the current post that matches the related post's topic
- Replace plain text with markdown links
- Example: `ISO 27001` → `[ISO 27001](link-to-iso27001-guide)`

**Option B: Minimal New Anchor Text**
- Only if there's a highly relevant connection and NO existing anchor text
- Add a brief, natural sentence or phrase that introduces the link
- Keep additions minimal and non-invasive (1 sentence maximum)
- Place in a contextually appropriate location

### 4. Add Incoming Links (Reverse Linking)

Also check: can any of the related posts link BACK to the current post?

For each relevant existing post, suggest a specific line where a link to the new post could be added, with the exact anchor text.

### 5. Guidelines and Constraints

- **Maximum 5-7 internal links** total in the post
- Do NOT force links where they don't naturally fit
- Prioritize quality over quantity
- Links should add genuine value to the reader
- Avoid linking to the same post multiple times
- Preserve the original voice and flow
- Do not modify headings, callout quotes, or section structure
- Focus on body paragraphs where links add context

### 6. Document Changes

After making changes, list all links added with:
- Location in the post (section/paragraph)
- Anchor text used
- Target post title
- Reason for adding the link

Also list suggested reverse links (from existing posts to the new post).

## Example Output

```
Summary of Changes:
- Keywords identified: ISO 27001, auditoría interna, controles
- Related posts found: 8
- Links added to current post: 4
- Reverse links suggested: 3

Links Added to Current Post:
1. Section "Paso 3": "[auditoría interna](link)" — Connects to internal audit checklist post
2. Section "Paso 5": "[formación del personal](link)" — Connects to training requirements post
3. Section "Controles": "[documentar los controles](link)" — Connects to controls documentation guide
4. Section "Conclusión": "[evaluación de riesgos](link)" — Connects to risk assessment guide

Reverse Links Suggested:
1. In "Checklist auditoría interna", section X: add link to current post about [topic]
2. In "Formación personal ISO 27001", section Y: add link to current post
3. In "Documentar controles", section Z: add link to current post
```

## User Input

$ARGUMENTS
