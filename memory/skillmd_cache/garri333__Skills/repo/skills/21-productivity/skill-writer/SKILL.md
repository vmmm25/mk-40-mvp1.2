---
name: skill-writer
version: 1.0.0
description: >
  Meta-skill that creates other skills from conversations and workflows. Analyzes user interactions
  to extract reusable patterns, generates production-quality SKILL.md files with proper YAML
  frontmatter, validates skill structure and scope, and suggests new skills based on repeated
  usage patterns. Self-improving through feedback loops and community meta-skills trends.
tags:
  - meta-skill
  - skill-creation
  - pattern-extraction
  - yaml-frontmatter
  - validation
  - auto-improvement
  - workflow-analysis
  - productivity
  - reusable-patterns
author: garri333
license: MIT
source: OpenAI $skill-creator concept + community meta-skills trend
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# skill-writer

Meta-skill that creates other skills. Analyze conversations and workflows to extract reusable patterns, generate SKILL.md files with proper YAML frontmatter, validate skill structure, and auto-improve based on usage patterns.

---

## When to Activate

Activate this skill when the user:

- Wants to **create a new skill** from scratch or from an existing workflow
- Has a **repeated workflow** that should be extracted into a reusable skill
- Asks to **analyze a conversation** and generate a skill from it
- Needs to **validate an existing SKILL.md** for completeness and quality
- Wants to **refactor or improve** an existing skill definition
- Asks about **skill best practices**, structure, or formatting standards
- Wants to **auto-generate skills** from project patterns or common tasks
- Needs to **batch-create multiple skills** for a category
- Uses keywords: `create skill`, `new skill`, `extract skill`, `skill template`, `SKILL.md`, `meta-skill`

---

## Step-by-Step Instructions

### 1. Skill Creation Architecture

```
SKILL-WRITER PIPELINE
══════════════════════════════════════════════════════════════

  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
  │   INPUT SOURCE   │────▶│   PATTERN        │────▶│   SKILL          │
  │                  │     │   EXTRACTION     │     │   GENERATION     │
  │ • Conversation   │     │                  │     │                  │
  │ • Workflow log   │     │ • Identify steps │     │ • YAML header    │
  │ • Code patterns  │     │ • Extract I/O    │     │ • Instructions   │
  │ • User request   │     │ • Find triggers  │     │ • Examples       │
  └──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                             │
  ┌──────────────────┐     ┌──────────────────┐              │
  │   AUTO-IMPROVE   │◀────│   VALIDATION     │◀─────────────┘
  │                  │     │                  │
  │ • Usage tracking │     │ • Required fields│
  │ • Pattern learn  │     │ • Scope check    │
  │ • Suggest new    │     │ • Boundary test  │
  └──────────────────┘     └──────────────────┘

CORE PRINCIPLE: Each skill does ONE job well.
```

---

### 2. SKILL.md Structure Standard

Every generated SKILL.md MUST follow this structure:

```yaml
# YAML Frontmatter (REQUIRED)
---
name: skill-name-kebab-case        # Required: unique identifier
version: 1.0.0                     # Required: semantic versioning
description: >                     # Required: multi-line description
  Clear, concise description of what the skill does,
  its main capabilities, and primary use cases.
tags:                              # Required: 3-10 relevant tags
  - tag-one
  - tag-two
author: garri333                   # Required: author identifier
license: MIT                       # Required: license type
source: Origin or inspiration      # Optional: attribution
compatible:                        # Optional: compatible platforms
  - claude-code
  - claude-desktop
  - skill-md-standard
---
```

```markdown
# Markdown Body (REQUIRED SECTIONS)

# skill-name
One-paragraph summary.

## When to Activate
- Bullet list of activation triggers
- Include keywords that should activate this skill

## Step-by-Step Instructions
### Numbered subsections with detailed steps
- Imperative language ("Do X", "Generate Y")
- Explicit inputs and outputs for each step

## Best Practices
- Quality guidelines
- Do's and don'ts

## Examples
### Concrete usage examples with expected output
```

---

### 3. Pattern Extraction from Conversations

When analyzing a conversation to extract a skill:

1. **Identify the core task**: What is the user repeatedly asking the agent to do?
2. **Extract trigger phrases**: What words or phrases signal this task?
3. **Map the workflow steps**: What sequence of actions does the agent perform?
4. **Define inputs**: What information does the agent need from the user?
5. **Define outputs**: What deliverables does the agent produce?
6. **Find boundaries**: What is explicitly NOT part of this skill?

```yaml
# Pattern Extraction Template
extraction:
  conversation_id: "conv-2026-02-22-001"
  patterns_found:
    - pattern: "User asks to generate API documentation"
      frequency: 5
      steps:
        - "Read route files"
        - "Extract endpoint signatures"
        - "Generate OpenAPI spec"
        - "Create markdown docs"
      inputs:
        - "Source code directory"
        - "API framework (Express, FastAPI, etc.)"
      outputs:
        - "OpenAPI 3.0 YAML"
        - "Markdown documentation"
      suggested_skill_name: "api-doc-generator"
      confidence: 0.92
```

---

### 4. Quality Criteria for Generated Skills

Apply these quality checks to every generated skill:

```
QUALITY CRITERIA CHECKLIST
══════════════════════════════════════════════════════════════

✅ FOCUSED ON SINGLE JOB
   □ Skill does exactly one thing well
   □ Not a grab-bag of loosely related tasks
   □ Can be described in one sentence

✅ IMPERATIVE STEPS WITH EXPLICIT I/O
   □ Steps use imperative verbs ("Generate", "Validate", "Extract")
   □ Each step defines what goes in and what comes out
   □ No ambiguous or vague instructions

✅ PREFER INSTRUCTIONS OVER SCRIPTS
   □ Use natural language instructions by default
   □ Only include scripts when deterministic behavior is required
   □ Scripts are for automation; instructions are for flexibility

✅ CLEAR ACTIVATION TRIGGERS
   □ "When to Activate" section lists specific triggers
   □ Keywords are explicit and non-overlapping with other skills
   □ Edge cases are documented

✅ BOUNDARY DEFINITION
   □ What the skill does NOT do is clearly stated
   □ Related skills are referenced for handoff
   □ Scope creep is prevented

✅ EXAMPLES PRESENT
   □ At least 2 concrete usage examples
   □ Examples show both input and expected output
   □ Edge cases are covered in examples
```

---

### 5. Skill Validation

Before finalizing any SKILL.md, run this validation:

```yaml
# Validation Rules
validation:
  required_fields:
    frontmatter:
      - name          # Must be kebab-case, unique
      - version       # Must follow semver (X.Y.Z)
      - description   # Must be non-empty, > 20 characters
      - tags          # Must have 3-10 tags
      - author        # Must be non-empty
      - license       # Must be a recognized license
    body:
      - title         # H1 matching skill name
      - activation    # "When to Activate" section
      - instructions  # "Step-by-Step Instructions" section
      - examples      # At least one example section

  scope_validation:
    - single_responsibility: true
    - clear_boundaries: true
    - no_overlap_with_existing: true
    - activation_keywords_unique: true

  quality_gates:
    - description_length: ">= 50 chars"
    - tags_count: "3-10"
    - instruction_steps: ">= 3"
    - examples_count: ">= 2"
    - imperative_language: true
```

**Validation output format:**

```
SKILL VALIDATION REPORT
══════════════════════════════════════════════════════════════
Skill: api-doc-generator
Status: ✅ PASS (score: 94/100)

Frontmatter:
  ✅ name: valid kebab-case
  ✅ version: valid semver (1.0.0)
  ✅ description: 127 characters
  ✅ tags: 6 tags (within range)
  ✅ author: garri333
  ✅ license: MIT

Body:
  ✅ Title matches skill name
  ✅ When to Activate: 8 triggers defined
  ✅ Instructions: 5 steps with I/O
  ✅ Examples: 3 examples provided

Quality:
  ✅ Single responsibility
  ✅ Clear boundaries
  ⚠️ Minor: Consider adding "Best Practices" section (-3 pts)
  ⚠️ Minor: Tag "api" overlaps with api-testing skill (-3 pts)
══════════════════════════════════════════════════════════════
```

---

### 6. Auto-Improvement Engine

The skill-writer learns from usage patterns to suggest improvements:

```
AUTO-IMPROVEMENT LOOP
══════════════════════════════════════════════════════════════

  ┌────────────────┐
  │  USAGE DATA    │
  │                │
  │ • Which skills │──────┐
  │   activated    │      │
  │ • User edits   │      ▼
  │ • Complaints   │  ┌──────────────┐     ┌──────────────┐
  └────────────────┘  │  ANALYSIS    │────▶│  SUGGESTIONS │
                      │              │     │              │
                      │ • Frequency  │     │ • New skills │
                      │ • Gaps found │     │ • Merges     │
                      │ • Overlaps   │     │ • Splits     │
                      └──────────────┘     │ • Updates    │
                                           └──────────────┘

TRIGGERS FOR NEW SKILL SUGGESTION:
  • Same workflow repeated > 3 times without an existing skill
  • User manually adjusts agent output in the same way repeatedly
  • Two existing skills are always activated together
  • A skill is activated but user always asks for extra steps
```

```yaml
# Auto-improvement suggestions
auto_improve:
  suggest_new_skill:
    trigger: "workflow_repeated >= 3"
    action: "Extract pattern and propose new SKILL.md"
    requires_approval: true

  suggest_merge:
    trigger: "two_skills_co_activated >= 5"
    action: "Propose merging into single skill"
    requires_approval: true

  suggest_split:
    trigger: "skill_scope_exceeds_threshold"
    action: "Propose splitting into focused sub-skills"
    requires_approval: true

  suggest_update:
    trigger: "user_edits_output >= 3"
    action: "Update skill instructions to match user preference"
    requires_approval: true
```

---

## Best Practices

1. **One skill, one job**: Never combine unrelated functionality into a single skill
2. **Imperative language**: Write instructions as commands, not descriptions
3. **Explicit I/O**: Every step must declare its inputs and outputs
4. **Version responsibly**: Use semver — patch for fixes, minor for additions, major for breaking changes
5. **Tag thoughtfully**: Tags should enable discovery without creating noise
6. **Test with examples**: Every skill must have examples that can be mentally executed
7. **Avoid script dependencies**: Prefer instructions unless deterministic output is required
8. **Reference related skills**: Link to complementary skills for handoff scenarios
9. **Keep activation triggers specific**: Vague triggers cause false activations
10. **Document boundaries**: "What this skill does NOT do" prevents scope creep

---

## Examples

### Example 1: Create a Skill from a Repeated Workflow

**User**: "I keep asking you to review my PR, check for security issues, suggest tests, and format a summary. Can you make a skill for that?"

**Generated SKILL.md**:

```yaml
---
name: pr-security-review
version: 1.0.0
description: >
  Review pull requests for security vulnerabilities, suggest missing tests,
  and generate a formatted summary report with severity levels.
tags:
  - security
  - code-review
  - pull-request
  - testing
  - summary
author: garri333
license: MIT
---
```

```markdown
# pr-security-review

Review pull requests for security issues, suggest tests, and produce a summary.

## When to Activate
- User asks to review a PR for security
- User wants a security summary of code changes
- Keywords: `PR review`, `security check`, `vulnerability scan`

## Step-by-Step Instructions
### 1. Fetch PR diff
- Input: PR URL or branch name
- Output: Unified diff of all changed files

### 2. Security analysis
- Input: Diff content
- Output: List of potential vulnerabilities with severity (critical/high/medium/low)
- Check: SQL injection, XSS, auth bypass, secrets exposure, dependency vulnerabilities

### 3. Test gap analysis
- Input: Changed files + existing test files
- Output: List of untested code paths with suggested test cases

### 4. Generate summary report
- Input: Security findings + test gaps
- Output: Formatted Markdown report with:
  - Executive summary (1-2 sentences)
  - Security findings table (severity, file, line, description)
  - Test suggestions (file, function, test description)
  - Overall risk score (1-10)
```

---

### Example 2: Validate an Existing Skill

**User**: "Check if my database-migration skill is well-formed."

**Agent performs validation and responds**:

```
SKILL VALIDATION REPORT
══════════════════════════════════════════════════════════════
Skill: database-migration
Status: ⚠️ NEEDS IMPROVEMENT (score: 72/100)

Frontmatter:
  ✅ name: valid
  ✅ version: 1.0.0
  ⚠️ description: only 18 characters (minimum 50) → -10 pts
  ✅ tags: 4 tags
  ❌ author: missing → -8 pts
  ✅ license: MIT

Body:
  ✅ Title present
  ✅ When to Activate: 5 triggers
  ⚠️ Instructions: 2 steps (minimum 3) → -5 pts
  ❌ Examples: none found → -5 pts

Recommendations:
  1. Expand description to explain migration strategies supported
  2. Add author field
  3. Add at least one more instruction step (e.g., rollback procedure)
  4. Add 2+ examples showing migration scenarios
══════════════════════════════════════════════════════════════
```

---

### Example 3: Suggest New Skills from Usage Patterns

**Agent analysis output**:

```
SKILL SUGGESTION REPORT
══════════════════════════════════════════════════════════════
Analysis period: Last 30 days
Conversations analyzed: 47

Suggested New Skills:
──────────────────────────────────────────────────────────────
1. env-file-manager (confidence: 0.91)
   Reason: User managed .env files in 12 conversations
   Pattern: Create, validate, sync environment variables across services

2. changelog-generator (confidence: 0.87)
   Reason: User requested changelogs from git history 8 times
   Pattern: Parse commits → group by type → format CHANGELOG.md

3. api-mock-server (confidence: 0.83)
   Reason: User created mock APIs for frontend development 6 times
   Pattern: Read OpenAPI spec → generate mock server with realistic data

Suggested Merges:
──────────────────────────────────────────────────────────────
1. Merge: css-optimizer + tailwind-helper → frontend-styling
   Reason: Always activated together (9/9 co-activations)
══════════════════════════════════════════════════════════════
```
