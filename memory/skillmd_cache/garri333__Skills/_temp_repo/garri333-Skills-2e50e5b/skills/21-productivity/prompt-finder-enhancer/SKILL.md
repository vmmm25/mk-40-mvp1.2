---
name: prompt-finder-enhancer
version: 1.0.0
description: >
  Community prompt library access and intelligent optimization. Search 140,000+ community
  prompts, enhance prompts with context injection, optimize structure for specific frameworks
  (React, Vue, Angular, Python, Node.js), detect task types automatically, and compose
  complex prompts from templates. Features two-level context injection (project metadata +
  file-specific), adaptive intelligence, and caching for reduced latency.
tags:
  - prompt-engineering
  - prompt-library
  - context-injection
  - optimization
  - templates
  - framework-specific
  - adaptive
  - caching
  - composition
  - productivity
author: garri333
license: MIT
source: Inspired by MCP Market Prompt Lookup (140,000+ community prompts) and prompt engineering best practices
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# prompt-finder-enhancer

Community prompt library access and intelligent optimization. Search 140,000+ prompts, enhance them with context injection, optimize for specific frameworks, detect task types automatically, and compose complex prompts from reusable templates.

---

## When to Activate

Activate this skill when the user:

- Wants to **find a prompt** for a specific task or framework
- Needs to **enhance or optimize** an existing prompt
- Asks for **prompt engineering** advice or best practices
- Wants to **inject project context** into a prompt automatically
- Needs **framework-specific prompt** optimization (React, Vue, Python, etc.)
- Asks about **prompt templates** or reusable prompt components
- Wants to **compose complex prompts** from smaller building blocks
- Needs **prompt caching** to reduce latency on repeated queries
- Asks about **community prompts** or prompt libraries
- Wants to **analyze a task** and auto-generate the optimal prompt
- Uses keywords: `find prompt`, `enhance prompt`, `optimize prompt`, `prompt template`, `prompt library`, `context injection`, `prompt engineering`

---

## Step-by-Step Instructions

### 1. Prompt Enhancement Architecture

```
PROMPT FINDER & ENHANCER PIPELINE
══════════════════════════════════════════════════════════════

  ┌──────────────────┐     ┌──────────────────┐
  │   USER INPUT     │     │   COMMUNITY      │
  │                  │     │   LIBRARY        │
  │ • Raw prompt     │     │ • 140,000+       │
  │ • Task desc      │     │   prompts        │
  │ • Framework      │     │ • Categorized    │
  └────────┬─────────┘     └────────┬─────────┘
           │                        │
           ▼                        ▼
  ┌──────────────────────────────────────────────┐
  │            TASK ANALYZER                      │
  │                                               │
  │  Detect: creation | debugging | refactoring   │
  │          | testing | documentation | review   │
  └──────────────────┬────────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │         CONTEXT INJECTION ENGINE              │
  │                                               │
  │  Level 1: Project metadata                    │
  │  ├─ Tech stack, framework, language           │
  │  ├─ Project structure, conventions            │
  │  └─ Dependencies, configuration               │
  │                                               │
  │  Level 2: File-specific context               │
  │  ├─ Current file content and imports          │
  │  ├─ Related files and dependencies            │
  │  └─ Recent changes and git context            │
  └──────────────────┬────────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │        PROMPT OPTIMIZER                       │
  │                                               │
  │  • Structure optimization                     │
  │  • Framework-specific enhancements            │
  │  • Token efficiency                           │
  │  • Output format specification                │
  │  • Constraint injection                       │
  └──────────────────┬────────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │        CACHE & OUTPUT                         │
  │                                               │
  │  • Cache enhanced prompts for reuse           │
  │  • Deliver optimized prompt                   │
  │  • Track effectiveness metrics                │
  └──────────────────────────────────────────────┘
```

---

### 2. Community Prompt Library Search

Search and retrieve prompts from community libraries:

```yaml
# Prompt Library Search
search:
  sources:
    - name: "MCP Market Prompt Lookup"
      prompts: 140000+
      categories:
        - coding
        - writing
        - analysis
        - design
        - debugging
        - testing
        - devops
        - data-science
        - security
        - documentation

  query_syntax:
    keyword: "react component testing"
    filters:
      category: "coding"
      framework: "react"
      language: "typescript"
      rating: ">= 4.0"
      updated_after: "2025-01-01"
    sort: "relevance"  # or "rating", "date", "usage_count"
    limit: 10
```

```
SEARCH RESULTS
══════════════════════════════════════════════════════════════

Query: "react component testing"
Results: 47 prompts found (showing top 5)

#  │ Title                              │ Rating │ Uses   │ Cat
───┼────────────────────────────────────┼────────┼────────┼──────
1  │ React Testing Library Expert       │ 4.8    │ 12,340 │ test
2  │ Component Unit Test Generator      │ 4.7    │ 9,870  │ test
3  │ React Integration Test Builder     │ 4.5    │ 7,210  │ test
4  │ Jest + RTL Best Practices          │ 4.5    │ 6,890  │ test
5  │ Accessibility Test for Components  │ 4.3    │ 4,120  │ test

Select a prompt to view, enhance, or use directly.
══════════════════════════════════════════════════════════════
```

---

### 3. Prompt Enhancement Process

Transform a basic prompt into an optimized, context-rich prompt:

#### Step 3.1: Analyze the Task

```yaml
# Task Analysis
task_analysis:
  input: "Help me create a login form"

  detected:
    task_type: "creation"
    domain: "frontend"
    framework: "react"           # inferred from project
    language: "typescript"       # inferred from tsconfig.json
    complexity: "medium"
    related_concepts:
      - "form handling"
      - "validation"
      - "authentication"
      - "accessibility"
      - "state management"
```

#### Step 3.2: Inject Context (Two-Level System)

```yaml
# Level 1: Project Metadata Context
project_context:
  framework: "React 19"
  language: "TypeScript 5.7"
  styling: "Tailwind CSS 4.0"
  state_management: "Zustand"
  testing: "Vitest + React Testing Library"
  api_pattern: "REST with fetch"
  linting: "ESLint + Prettier"
  conventions:
    components: "Functional components with hooks"
    naming: "PascalCase for components, camelCase for functions"
    file_structure: "Feature-based folders"
    imports: "Absolute imports with @/ alias"

# Level 2: File-Specific Context
file_context:
  current_file: "src/features/auth/LoginForm.tsx"
  imports_available:
    - "@/components/ui/Button"
    - "@/components/ui/Input"
    - "@/hooks/useAuth"
    - "@/lib/validators"
  related_files:
    - "src/features/auth/useAuth.ts"
    - "src/features/auth/authTypes.ts"
    - "src/api/authApi.ts"
  recent_patterns:
    - "Other forms use react-hook-form with zod validation"
    - "Error messages displayed with toast notifications"
```

#### Step 3.3: Optimize Structure

```
PROMPT OPTIMIZATION TRANSFORMS
══════════════════════════════════════════════════════════════

BEFORE (raw user input):
  "Help me create a login form"

AFTER (enhanced prompt):
──────────────────────────────────────────────────────────────
Create a login form React component with the following specifications:

**Tech Stack**: React 19, TypeScript 5.7, Tailwind CSS 4.0
**Location**: src/features/auth/LoginForm.tsx

**Requirements**:
1. Use react-hook-form with zod validation schema
2. Fields: email (validated), password (min 8 chars)
3. Submit handler calls useAuth().login(credentials)
4. Loading state during API call with disabled submit button
5. Error handling with toast notifications (match existing pattern)
6. Accessible: proper labels, aria attributes, keyboard navigation

**Available imports** (use these, don't create new):
- @/components/ui/Button (existing styled button)
- @/components/ui/Input (existing styled input)
- @/hooks/useAuth (provides login function)
- @/lib/validators (existing zod schemas)

**Conventions**:
- Functional component with hooks
- PascalCase component name
- Feature-based folder structure
- Absolute imports with @/ alias

**Output**: Complete TypeScript component file with types.
──────────────────────────────────────────────────────────────

Enhancement score: +340% context richness
Token overhead: +180 tokens (worthwhile for accuracy)
══════════════════════════════════════════════════════════════
```

---

### 4. Framework-Specific Enhancements

Apply framework-aware optimizations automatically:

```yaml
# Framework Enhancement Rules
framework_enhancements:
  react:
    inject:
      - "Use functional components with hooks"
      - "Follow React 19 patterns (use() hook, server components awareness)"
      - "Memoize expensive computations with useMemo"
      - "Use React.memo for pure display components"
    conventions:
      - "Props interface defined above component"
      - "Custom hooks for reusable logic"
      - "Error boundaries for fault tolerance"
    testing:
      - "Use React Testing Library (not Enzyme)"
      - "Test user behavior, not implementation"
      - "Use screen.getByRole over getByTestId"

  vue:
    inject:
      - "Use Composition API with <script setup>"
      - "Follow Vue 3.5+ patterns"
      - "Use defineProps/defineEmits macros"
    conventions:
      - "Single File Components (.vue)"
      - "Use composables for shared logic"
      - "PascalCase component names in templates"
    testing:
      - "Use @vue/test-utils"
      - "Mount with createTestingPinia for store testing"

  angular:
    inject:
      - "Use standalone components (Angular 17+)"
      - "Signal-based reactivity preferred"
      - "Use inject() function over constructor injection"
    conventions:
      - "Follow Angular style guide for naming"
      - "Use OnPush change detection"
      - "Lazy load route modules"
    testing:
      - "Use TestBed for component testing"
      - "Use HttpClientTestingModule for API tests"

  python:
    inject:
      - "Follow PEP 8 style guide"
      - "Use type hints for all function signatures"
      - "Use dataclasses or Pydantic models for data"
    conventions:
      - "snake_case for functions and variables"
      - "UPPER_CASE for constants"
      - "Docstrings for all public functions"
    testing:
      - "Use pytest over unittest"
      - "Fixtures for test setup"
      - "Parametrize for multiple test cases"

  nodejs:
    inject:
      - "Use ESM imports (import/export)"
      - "Async/await for all async operations"
      - "Error handling with custom error classes"
    conventions:
      - "camelCase for functions and variables"
      - "Express middleware pattern"
      - "Environment variables via dotenv"
    testing:
      - "Use Vitest or Jest"
      - "Supertest for API testing"
      - "Mock external services"
```

---

### 5. Adaptive Task Type Detection

Automatically detect the task type and apply appropriate prompt patterns:

```
TASK TYPE DETECTION
══════════════════════════════════════════════════════════════

User Input               │ Detected Type  │ Prompt Pattern
─────────────────────────┼────────────────┼──────────────────
"Create a new component"  │ CREATION       │ Spec + constraints
"Fix this bug"            │ DEBUGGING      │ Error + context
"Refactor this function"  │ REFACTORING    │ Current + target
"Write tests for..."      │ TESTING        │ Code + test cases
"Document this API"       │ DOCUMENTATION  │ Code + format
"Review this PR"          │ REVIEW         │ Diff + criteria
"Optimize performance"    │ OPTIMIZATION   │ Profile + targets
"Explain this code"       │ EXPLANATION    │ Code + audience
══════════════════════════════════════════════════════════════
```

```yaml
# Task-specific prompt patterns
task_patterns:
  creation:
    structure:
      - "Define the deliverable clearly"
      - "Specify tech stack and constraints"
      - "List available imports and existing patterns"
      - "Define acceptance criteria"
      - "Request complete, runnable output"

  debugging:
    structure:
      - "Describe the error (exact message, stack trace)"
      - "Provide the relevant code"
      - "Describe expected vs actual behavior"
      - "List what has already been tried"
      - "Request root cause + fix"

  refactoring:
    structure:
      - "Show current implementation"
      - "Describe desired improvement (readability, performance, etc.)"
      - "Specify constraints (no breaking changes, keep API)"
      - "Request refactored code + explanation of changes"

  testing:
    structure:
      - "Provide the code to test"
      - "Specify testing framework"
      - "List scenarios: happy path, edge cases, errors"
      - "Request test file with assertions"

  documentation:
    structure:
      - "Provide the code to document"
      - "Specify format (JSDoc, docstrings, README, API docs)"
      - "Define audience (developers, end users)"
      - "Request structured output"

  review:
    structure:
      - "Provide the code diff or PR"
      - "Specify review focus (security, performance, style)"
      - "Request itemized feedback with severity"
```

---

### 6. Caching Strategy

Reduce latency on repeated or similar queries:

```yaml
# Prompt Cache Configuration
cache:
  strategy: "tiered"

  tiers:
    L1_memory:
      type: "in-memory LRU"
      max_entries: 100
      ttl: "1 hour"
      hit_rate_target: "> 60%"
      stores: "exact prompt matches"

    L2_project:
      type: "file-based (.prompt-cache/)"
      max_entries: 1000
      ttl: "7 days"
      stores: "project-specific enhanced prompts"
      invalidation:
        - "On project dependency change"
        - "On framework version update"
        - "On file structure change"

    L3_community:
      type: "remote cache"
      ttl: "30 days"
      stores: "community prompt search results"
      refresh: "background async"

  cache_key_generation:
    components:
      - task_type
      - framework
      - language
      - prompt_hash
    normalization:
      - "lowercase"
      - "remove extra whitespace"
      - "sort constraints alphabetically"

  metrics:
    track:
      - cache_hit_rate
      - avg_latency_cached_ms
      - avg_latency_uncached_ms
      - cache_size_bytes
      - eviction_count
```

---

### 7. Template Variables and Composition

Build complex prompts from reusable components:

```yaml
# Template System
templates:
  variables:
    {{FRAMEWORK}}: "Resolved from project config (e.g., React 19)"
    {{LANGUAGE}}: "Resolved from file extension or config"
    {{STYLING}}: "Resolved from project dependencies"
    {{FILEPATH}}: "Current file being edited"
    {{IMPORTS}}: "Available imports from project"
    {{CONVENTIONS}}: "Project coding conventions"
    {{TESTING_FRAMEWORK}}: "Resolved from devDependencies"
    {{RECENT_PATTERNS}}: "Patterns from recent similar files"

  composable_blocks:
    tech_stack: |
      **Tech Stack**: {{FRAMEWORK}}, {{LANGUAGE}}, {{STYLING}}
      **Testing**: {{TESTING_FRAMEWORK}}

    constraints: |
      **Conventions**:
      {{CONVENTIONS}}

      **Available Imports** (prefer these over creating new):
      {{IMPORTS}}

    output_format: |
      **Output Requirements**:
      - Complete, runnable {{LANGUAGE}} file
      - No placeholder comments (implement fully)
      - Include error handling
      - Follow existing project patterns

    quality_gates: |
      **Quality Checklist**:
      - [ ] TypeScript strict mode compatible
      - [ ] No any types
      - [ ] Accessible (WCAG 2.1 AA)
      - [ ] Responsive design
      - [ ] Error states handled
```

#### Prompt Composition Example

```yaml
# Compose a prompt from blocks
composed_prompt:
  template: "component_creation"
  blocks:
    - tech_stack
    - constraints
    - output_format
    - quality_gates

  custom_sections:
    - name: "Component Specification"
      content: |
        Create a {{COMPONENT_NAME}} component that:
        1. {{REQUIREMENT_1}}
        2. {{REQUIREMENT_2}}
        3. {{REQUIREMENT_3}}

  variables:
    COMPONENT_NAME: "UserProfileCard"
    REQUIREMENT_1: "Displays user avatar, name, and role"
    REQUIREMENT_2: "Shows online status indicator"
    REQUIREMENT_3: "Supports edit mode with inline form"

  output: |
    Create a UserProfileCard component that:
    1. Displays user avatar, name, and role
    2. Shows online status indicator
    3. Supports edit mode with inline form

    **Tech Stack**: React 19, TypeScript 5.7, Tailwind CSS 4.0
    **Testing**: Vitest + React Testing Library

    **Conventions**:
    - Functional components with hooks
    - PascalCase for components
    - Feature-based folder structure

    **Available Imports** (prefer these over creating new):
    - @/components/ui/Avatar
    - @/components/ui/Badge
    - @/components/ui/Button

    **Output Requirements**:
    - Complete, runnable TypeScript file
    - No placeholder comments
    - Include error handling
    - Follow existing project patterns

    **Quality Checklist**:
    - [ ] TypeScript strict mode compatible
    - [ ] No any types
    - [ ] Accessible (WCAG 2.1 AA)
    - [ ] Responsive design
    - [ ] Error states handled
```

---

## Best Practices

1. **Context is king**: The #1 prompt improvement is adding relevant context — always inject project metadata
2. **Be specific about output**: Define exact format, language, and constraints for deterministic results
3. **Use community prompts as starting points**: Don't reinvent; search first, then enhance
4. **Match task type to pattern**: Use the appropriate prompt structure for creation vs. debugging vs. review
5. **Cache aggressively**: Project context changes slowly; cache enhanced prompts to reduce latency
6. **Validate before sending**: Check that enhanced prompts don't exceed token limits
7. **Track effectiveness**: Measure if enhanced prompts produce better results than raw ones
8. **Compose, don't copy**: Use template blocks to build prompts consistently across a team
9. **Keep templates updated**: As project dependencies change, invalidate cached context
10. **Framework awareness matters**: A React prompt is very different from a Vue prompt — always specialize

---

## Examples

### Example 1: Find and Enhance a Prompt

**User**: "Find me a good prompt for writing React component tests."

**Agent**:
1. Searches community library for "react component testing" prompts
2. Selects top-rated prompt (Rating: 4.8, 12,340 uses)
3. Enhances with project context:

```
ORIGINAL COMMUNITY PROMPT:
"Write unit tests for the given React component using React Testing Library."

ENHANCED PROMPT (with project context):
──────────────────────────────────────────────────────────────
Write comprehensive unit tests for the following React component.

**Testing Stack**: Vitest 2.1 + React Testing Library 16 + @testing-library/user-event
**Component**: src/features/dashboard/MetricsCard.tsx

**Test Requirements**:
1. Test rendering with default props
2. Test rendering with all optional props
3. Test user interactions (click handlers, hover states)
4. Test loading state
5. Test error state
6. Test accessibility (role attributes, keyboard navigation)
7. Test responsive behavior (if applicable)

**Conventions** (match existing test files):
- File naming: MetricsCard.test.tsx
- Use describe/it blocks (not test())
- Use screen.getByRole over getByTestId
- Use userEvent over fireEvent
- Mock API calls with vi.mock()

**Available test utilities**:
- @/test/utils (custom render with providers)
- @/test/fixtures (common test data)

[Component code will be provided below]
──────────────────────────────────────────────────────────────
Enhancement: +280% context | Estimated accuracy improvement: +45%
```

---

### Example 2: Auto-Detect Task and Generate Prompt

**User**: "This function is running slow, can you help?"

**Agent detects**: Task type = OPTIMIZATION

```
DETECTED TASK: Performance Optimization
AUTO-GENERATED PROMPT:
──────────────────────────────────────────────────────────────
Analyze and optimize the performance of the following function.

**Context**:
- File: src/services/dataProcessor.ts
- Function: processLargeDataset()
- Current execution time: ~3.2 seconds (measured via console.time)
- Dataset size: ~50,000 records
- Called: On every dashboard page load

**Optimization Targets**:
1. Reduce execution time to < 500ms
2. Minimize memory allocations
3. Maintain identical output (no behavioral changes)

**Approach**:
- Profile the function to identify bottleneck
- Consider: memoization, lazy evaluation, Web Workers, pagination
- Check for unnecessary iterations or copies
- Consider algorithm complexity (current: likely O(n²), target: O(n log n) or better)

**Output**:
1. Root cause analysis (what's slow and why)
2. Optimized implementation
3. Before/after performance comparison
4. Any trade-offs introduced

[Function code will be provided below]
──────────────────────────────────────────────────────────────
```

---

### Example 3: Compose a Multi-Part Prompt from Templates

**User**: "I need a prompt for creating a new API endpoint with tests and documentation."

**Agent composes from templates**:

```
COMPOSED PROMPT (3 blocks):
──────────────────────────────────────────────────────────────

## Part 1: API Endpoint Creation
Create a REST API endpoint with these specifications:
- Route: POST /api/v1/invoices
- Framework: Express.js + TypeScript
- Validation: zod schema
- Auth: JWT middleware (existing @/middleware/auth)
- Database: Prisma ORM (existing models)
- Error handling: Custom AppError class

## Part 2: Test Suite
Write tests using Vitest + Supertest:
- Success case (201 response with created invoice)
- Validation error (400 with specific field errors)
- Authentication failure (401 unauthorized)
- Authorization failure (403 forbidden for wrong role)
- Duplicate prevention (409 conflict)
- Server error handling (500 with generic message)

## Part 3: API Documentation
Generate OpenAPI 3.0 spec entry:
- Endpoint description
- Request body schema (with examples)
- Response schemas (200, 400, 401, 403, 409, 500)
- Authentication requirements
- Rate limiting notes

**Output**: Three files:
1. src/api/routes/invoices.ts (endpoint)
2. src/api/routes/invoices.test.ts (tests)
3. docs/api/invoices.yaml (OpenAPI spec)
──────────────────────────────────────────────────────────────
Composed from: endpoint_creation + test_suite + api_docs templates
Variables resolved: 12 | Blocks used: 3 | Estimated tokens: 420
```
