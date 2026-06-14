---
name: codex-prompt-enhancer
version: 1.0.0
description: Prompt Finder & Enhancer skill with two-level context system (project metadata + file-specific content), adaptive context intelligence, context caching, automatic task type detection, framework recognition, and community prompt library access. 144,375 accesses on MCP Market.
tags: [openai, codex, prompt, enhancer, context, optimization, mcp, framework-detection, caching, community-prompts]
author: garri333
license: MIT
source: openai/skills
---

# Codex Prompt Enhancer Skill

## Overview

Use this skill whenever the user needs to optimize, enhance, or discover prompts for AI-assisted coding tasks. The Prompt Enhancer uses a two-level context system — project-level metadata and file-level content — combined with adaptive intelligence, context caching, automatic task detection, and framework recognition to transform simple prompts into highly effective instructions.

**MCP Market stats:** 144,375 accesses — a widely adopted prompt optimization tool in the ecosystem.

---

## When to Activate

- User asks to improve or optimize a coding prompt.
- User wants to find the best prompt for a specific task.
- User asks about prompt engineering for code generation.
- User mentions context management or context optimization.
- User wants to reduce prompt latency via caching.
- User needs framework-specific prompts (React, Vue, Angular, etc.).
- User asks about the community prompt library.
- User wants to understand how context affects AI code generation quality.
- User mentions task type detection or adaptive prompting.

---

## Two-Level Context System

```
┌─────────────────────────────────────────────────────────────┐
│                    LEVEL 1: PROJECT CONTEXT                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ package.json │  │ tsconfig     │  │ Framework        │  │
│  │ dependencies │  │ .eslintrc    │  │ Detection        │  │
│  │ scripts      │  │ .prettierrc  │  │ (React/Vue/etc.) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Project      │  │ Git History  │  │ CI/CD Config     │  │
│  │ Structure    │  │ & Patterns   │  │ & Conventions    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    LEVEL 2: FILE CONTEXT                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Current File │  │ Imports &    │  │ Symbols &        │  │
│  │ Content      │  │ Dependencies │  │ Type Definitions │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Related      │  │ Test Files   │  │ Recently Edited  │  │
│  │ Components   │  │ & Fixtures   │  │ Files            │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Level 1: Project Metadata

Gathered once per session and cached. Includes:

| Source | Context Extracted |
|--------|-------------------|
| `package.json` | Framework, dependencies, versions, scripts |
| `tsconfig.json` / `jsconfig.json` | TypeScript settings, path aliases |
| `.eslintrc` / `.prettierrc` | Code style conventions |
| Project structure | Directory patterns, architecture style |
| Git history | Common patterns, team conventions |
| CI config | Build tools, test runners, deploy targets |
| README / docs | Project purpose, API descriptions |

### Level 2: File-Specific Content

Gathered per request, scoped to the active file:

| Source | Context Extracted |
|--------|-------------------|
| Current file | Full content, cursor position, selection |
| Import graph | All imported modules and their exports |
| Type definitions | Interfaces, types, enums used in the file |
| Related components | Parent/child components in the tree |
| Test files | Existing tests for the current module |
| Recent edits | Last 5 files edited in the session |

---

## Step-by-Step Procedures

### 1. Basic Prompt Enhancement

```bash
# Enhance a simple prompt with context
codex enhance "add a search feature"

# Input:  "add a search feature"
# Output (enhanced):
# "Add a search feature to the ProductList component in src/components/ProductList.tsx.
#  Use the existing useDebounce hook from src/hooks/useDebounce.ts for input debouncing.
#  Filter products by name and description fields. Follow the project's Tailwind CSS
#  patterns for input styling (see src/components/FilterBar.tsx for reference).
#  The product data comes from the useProducts query hook via @tanstack/react-query v5.
#  Maintain TypeScript strict mode compliance and add the search term to URL params
#  using the existing useSearchParams wrapper."

# The enhancer added:
# ✓ Specific file location (from Level 2 context)
# ✓ Existing utility hook (from import graph)
# ✓ Data model fields (from TypeScript types)
# ✓ Styling conventions (from project patterns)
# ✓ Data fetching library (from Level 1 dependencies)
# ✓ TypeScript requirements (from tsconfig)
```

### 2. Automatic Task Type Detection

The enhancer automatically detects what type of task the user is performing:

```bash
# Task type detection examples:

# Detected: PAGE CREATION
codex enhance "create a settings page"
# → Adds routing context, layout patterns, auth guards, existing page examples

# Detected: DEBUGGING
codex enhance "fix the login error"
# → Adds error logs, stack trace context, related error handlers, test failures

# Detected: REFACTORING
codex enhance "clean up the user service"
# → Adds current dependencies, consumers of the service, test coverage info

# Detected: TESTING
codex enhance "add tests for the cart module"
# → Adds test framework config, existing test patterns, fixture locations, coverage gaps

# Detected: PERFORMANCE
codex enhance "optimize the dashboard loading time"
# → Adds bundle size info, current render counts, API response times, lazy-loading usage

# Detected: SECURITY
codex enhance "fix the XSS vulnerability"
# → Adds input sanitization patterns, CSP config, previous security fixes

# Detected: MIGRATION
codex enhance "upgrade to React 19"
# → Adds current React version, deprecated API usage, breaking change list
```

**Supported task types:**

| Task Type | Detection Signals | Context Added |
|-----------|-------------------|---------------|
| Page Creation | "create page", "new route", "add screen" | Routes, layouts, auth, existing pages |
| Debugging | "fix", "error", "bug", "not working" | Logs, stack traces, error handlers |
| Refactoring | "clean up", "refactor", "restructure" | Dependents, tests, imports |
| Testing | "test", "spec", "coverage" | Test config, fixtures, coverage gaps |
| Performance | "optimize", "slow", "performance" | Bundle, render stats, profiling |
| Security | "vulnerability", "XSS", "injection" | Sanitization, CSP, auth patterns |
| Migration | "upgrade", "migrate", "update version" | Current versions, breaking changes |
| Documentation | "document", "README", "JSDoc" | Existing docs, API surface, types |
| Styling | "style", "CSS", "design", "UI" | Design system, theme, component lib |

### 3. Framework Recognition

```bash
# The enhancer auto-detects your framework and adjusts prompts accordingly

# React project detected
codex enhance "create a form component"
# → Uses React hooks, functional components, React Hook Form / Formik patterns

# Vue project detected
codex enhance "create a form component"
# → Uses Composition API, defineProps, defineEmits, VeeValidate patterns

# Angular project detected
codex enhance "create a form component"
# → Uses Reactive Forms, FormBuilder, validators, Angular Material patterns

# Next.js project detected
codex enhance "create an API endpoint"
# → Uses App Router, Route Handlers, middleware, server actions patterns

# Svelte project detected
codex enhance "create a form component"
# → Uses reactive declarations, stores, bind: directives

# Detection sources:
# - package.json dependencies
# - Framework-specific config files (next.config.js, vue.config.js, angular.json)
# - File extensions (.vue, .svelte, .tsx)
# - Project structure patterns (app/, pages/, components/)
```

**Framework-specific enhancements:**

```bash
# React/Next.js
codex enhance "add authentication"
# Enhanced: "Implement authentication using NextAuth.js v5 (already in package.json).
#  Create a login page at app/(auth)/login/page.tsx following the App Router pattern.
#  Use the existing AuthProvider in src/providers/AuthProvider.tsx.
#  Add middleware.ts for route protection matching the /dashboard/* pattern.
#  Store session in the existing PostgreSQL database via Prisma adapter."

# Vue/Nuxt
codex enhance "add authentication"
# Enhanced: "Implement authentication using Nuxt Auth Utils (already configured).
#  Create a login page at pages/login.vue using Composition API.
#  Use the existing useAuth composable in composables/useAuth.ts.
#  Add server middleware in server/middleware/auth.ts.
#  Follow the project's Pinia store pattern for auth state."
```

### 4. Context Caching

```bash
# Context caching reduces latency for repeated prompts in the same session

# First prompt — full context gathering (~500ms)
codex enhance "add validation to the form"
# Cache: miss → Gathered Level 1 (120ms) + Level 2 (380ms) = 500ms

# Second prompt — cached project context (~150ms)
codex enhance "add error messages to the form"
# Cache: hit (Level 1) → Reused project context, gathered file context (150ms)

# Third prompt — same file, cached file context (~50ms)
codex enhance "add submit handler to the form"
# Cache: hit (Level 1 + Level 2) → Both cached (50ms)

# Cache management
codex enhance --cache-status

# Output:
# Context Cache Status:
#   Level 1 (Project): CACHED (age: 12m, size: 4.2KB)
#   Level 2 (File):    CACHED (age: 3m, size: 1.8KB, file: src/components/Form.tsx)
#   Cache hit rate:     78%
#   Avg latency saved:  340ms

# Force cache refresh
codex enhance --refresh-cache "add validation"

# Clear all caches
codex enhance --clear-cache

# Set cache TTL
codex config set enhance.cache_ttl 3600  # 1 hour
```

### 5. Adaptive Context Intelligence

The enhancer adjusts the amount and type of context based on task complexity:

```bash
# Simple task — minimal context (fast)
codex enhance "rename the variable"
# Context: Current file only, cursor position
# Enhancement: "Rename the variable 'x' to 'userCount' at line 42 in
#  src/utils/analytics.ts. Also update the 3 references in the same file."

# Medium task — moderate context
codex enhance "add error handling to the API call"
# Context: Current file + imported API client + error types
# Enhancement: "Add error handling to the fetchProducts API call in
#  src/hooks/useProducts.ts. Use the existing ApiError class from
#  src/api/errors.ts. Handle 401 (redirect to login), 404 (show empty state),
#  and 500 (show error toast using the useToast hook). Follow the pattern
#  established in src/hooks/useOrders.ts."

# Complex task — full context
codex enhance "redesign the state management architecture"
# Context: All stores, all consumers, component tree, test coverage, bundle analysis
# Enhancement: (comprehensive multi-paragraph prompt with architecture diagram,
#  migration plan, and specific file references)
```

### 6. Community Prompt Library

```bash
# Browse community prompts
codex enhance --library

# Search community prompts
codex enhance --library search "react form validation"

# Output:
# Community Prompts (react form validation):
#   1. ⭐ 2,340 — "React Hook Form + Zod Validation Pattern"
#      Author: react-community | Updated: 2026-02-15
#   2. ⭐ 1,890 — "Formik + Yup Complex Form Validation"
#      Author: form-experts | Updated: 2026-01-30
#   3. ⭐ 1,456 — "Native React Form with Custom Hooks"
#      Author: hooks-curator | Updated: 2026-02-01

# Use a community prompt
codex enhance --library use "react-hook-form-zod-validation"

# Save your enhanced prompt to the library
codex enhance "add real-time form validation" --save-to-library

# Rate a community prompt
codex enhance --library rate "react-hook-form-zod-validation" --stars 5

# Create a curated collection
codex enhance --library create-collection "our-team-prompts" \
  --prompts "react-hook-form-zod-validation,react-query-patterns,nextjs-api-routes"
```

### 7. Prompt Optimization Techniques

```bash
# Analyze prompt effectiveness
codex enhance --analyze "create a component that shows user data"

# Output:
# Prompt Analysis:
# ┌──────────────────────────────────────────────────────┐
# │ Specificity:    ★★☆☆☆ (too vague)                   │
# │ Context usage:  ★☆☆☆☆ (no file/component references)│
# │ Constraints:    ★☆☆☆☆ (no style/pattern guidance)   │
# │ Completeness:   ★★☆☆☆ (missing data source, types)  │
# │ Overall score:  32/100                               │
# ├──────────────────────────────────────────────────────┤
# │ Recommendations:                                     │
# │ 1. Specify which user data fields to display         │
# │ 2. Reference the data fetching hook or API endpoint  │
# │ 3. Mention the design system/CSS framework           │
# │ 4. Include error and loading state requirements      │
# │ 5. Specify the parent component or page              │
# ├──────────────────────────────────────────────────────┤
# │ Enhanced (score: 89/100):                            │
# │ "Create a UserProfile component in                   │
# │  src/components/UserProfile.tsx that displays the    │
# │  user's name, email, avatar, and role. Fetch data    │
# │  using the useUser hook from src/hooks/useUser.ts.   │
# │  Use Tailwind CSS with the card pattern from         │
# │  src/components/Card.tsx. Include loading skeleton,  │
# │  error state, and empty state. Add to the            │
# │  /settings page below the AccountSettings section."  │
# └──────────────────────────────────────────────────────┘

# Compare two prompts
codex enhance --compare \
  "create a login form" \
  "create a login form using React Hook Form with email/password fields, \
   Zod validation, error messages, and submit to POST /api/auth/login"

# Output:
# Prompt A: 32/100 (vague, no constraints, no patterns)
# Prompt B: 76/100 (specific library, fields, validation, endpoint)
# Recommendation: Use Prompt B, auto-enhance to 92/100 with project context
```

### 8. Integration with Codex CLI and IDE

```bash
# CLI — enhance before executing
codex --enhance "add caching to the API"
# Automatically enhances the prompt, shows the enhanced version, then executes

# IDE — auto-enhance on typing (VS Code settings)
```

```json
{
  "codex.promptEnhancer.enabled": true,
  "codex.promptEnhancer.autoEnhance": true,
  "codex.promptEnhancer.showPreview": true,
  "codex.promptEnhancer.contextLevel": "adaptive",
  "codex.promptEnhancer.cacheTTL": 3600,
  "codex.promptEnhancer.communityLibrary": true,
  "codex.promptEnhancer.frameworkDetection": true
}
```

```bash
# Desktop App — enhance panel
# 1. Type your prompt in the main input
# 2. Click "Enhance" (or press Ctrl+E)
# 3. Review the enhanced prompt with highlighted additions
# 4. Edit if needed, then execute
```

---

## Best Practices

1. **Let the enhancer add context** — write your intent simply and let the two-level system fill in project-specific details.
2. **Use adaptive mode** — don't manually set context depth; the enhancer selects the right level based on task complexity.
3. **Trust framework detection** — the enhancer recognizes your stack automatically; override only if detection is wrong.
4. **Leverage caching** — work in focused sessions to benefit from cached context and reduced latency.
5. **Browse the community library** — domain-specific prompts from experienced developers often outperform ad-hoc prompts.
6. **Run `--analyze` on failed prompts** — if AI output is poor, the prompt is usually the issue; use analyze to spot weaknesses.
7. **Be specific about what, let AI decide how** — "validate email format" is better than "use regex ^[a-z]... to validate".
8. **Include constraints, not implementations** — "use TypeScript strict mode" is better than "add `: string` to every variable".
9. **Save effective prompts** — `--save-to-library` builds your team's knowledge base for recurring tasks.
10. **Refresh cache after major changes** — when switching branches or pulling large changes, use `--refresh-cache`.

---

## Examples

### Example 1: Simple to Enhanced

```bash
# User's simple prompt
codex enhance "add a button"

# Enhanced output:
# "Add a 'Save Changes' button to the SettingsForm component in
#  src/components/SettingsForm.tsx. Use the existing Button component from
#  src/ui/Button.tsx with variant='primary' and size='md'. Place it at the
#  bottom of the form after the last input field. Wire it to the existing
#  handleSubmit function. Add a loading state using the isSubmitting variable
#  from the form hook. Disable the button when the form has no changes
#  (use the isDirty flag from React Hook Form)."
```

### Example 2: Debugging Enhancement

```bash
codex enhance "the page crashes"

# Enhanced output:
# "Debug the crash in src/pages/Dashboard.tsx. The error 'Cannot read property
#  map of undefined' occurs at line 45 where products.map() is called.
#  The useProducts hook in src/hooks/useProducts.ts returns undefined initially
#  before the API response arrives. Add null-safe handling: use optional chaining
#  (products?.map) and add a loading check using the isLoading flag from the
#  useQuery hook. Also add an ErrorBoundary wrapper following the pattern in
#  src/components/ErrorBoundary.tsx."
```

### Example 3: Framework-Aware Enhancement

```bash
# In a Next.js 15 project with App Router
codex enhance "create an API for users"

# Enhanced output:
# "Create a users API using Next.js 15 App Router Route Handlers.
#  Create app/api/users/route.ts with GET (list, paginated) and POST (create).
#  Create app/api/users/[id]/route.ts with GET (by id), PUT (update), DELETE.
#  Use the existing Prisma client from src/lib/prisma.ts with the User model.
#  Add Zod validation using the schemas in src/schemas/user.ts.
#  Return NextResponse.json() with proper status codes (200, 201, 400, 404).
#  Add authentication check using the auth() helper from src/lib/auth.ts.
#  Follow the error handling pattern in app/api/products/route.ts."
```

### Example 4: Community Prompt Usage

```bash
# Search and use a community prompt for a common task
codex enhance --library search "nextjs middleware auth"

# Select: "Next.js 15 Middleware Authentication Guard" (⭐ 3,210)

codex enhance --library use "nextjs-15-middleware-auth"

# The community prompt is automatically customized with your project context:
# - Your auth provider (NextAuth v5)
# - Your protected routes (/dashboard/*, /settings/*, /api/admin/*)
# - Your public routes (/login, /register, /api/public/*)
# - Your session configuration
# - Your redirect patterns
```

### Example 5: Context Cache Performance

```bash
# Session with 10 prompts — cache performance
codex enhance --cache-stats

# Session Statistics:
# ┌─────────────────────────────────────────────┐
# │ Prompts processed:     10                   │
# │ Cache hits (Level 1):  9/10 (90%)           │
# │ Cache hits (Level 2):  6/10 (60%)           │
# │ Avg latency (cached):  85ms                 │
# │ Avg latency (uncached): 420ms               │
# │ Total time saved:       2.68s               │
# │ Context tokens saved:   ~12,400             │
# └─────────────────────────────────────────────┘
```
