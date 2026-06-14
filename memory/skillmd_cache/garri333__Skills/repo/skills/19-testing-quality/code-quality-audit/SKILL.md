---
name: code-quality-audit
version: 1.0.0
description: >
  Comprehensive codebase health assessment. Identifies and prioritizes technical debt, measures
  code complexity (cyclomatic, cognitive), checks dependency freshness, detects dead code and
  duplication, verifies architecture adherence, finds performance bottlenecks, evaluates linting
  coverage, type safety, and documentation coverage.
tags:
  - code-quality
  - technical-debt
  - complexity
  - audit
  - linting
  - dead-code
  - duplication
  - architecture
  - performance
  - type-safety
  - documentation
  - health-check
author: garri333
license: MIT
source: Inspired by Codebase Health Reporter from SkillsMP
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# code-quality-audit

Systematic codebase health assessment. Audit technical debt, complexity, dependencies, dead code, duplication, architecture compliance, performance, linting, type safety, and documentation coverage. Produce actionable reports with prioritized remediation plans.

---

## When to Activate

Activate this skill when the user:

- Asks for a **code quality assessment** or **codebase health check**
- Wants to identify and prioritize **technical debt**
- Needs to measure **code complexity** (cyclomatic, cognitive)
- Asks about **dependency freshness** or outdated packages
- Wants to find **dead code** or **unused exports**
- Needs to detect **code duplication** across the project
- Asks about **architecture compliance** or layering violations
- Wants to find **performance bottlenecks** in the codebase
- Needs to evaluate **linting rule coverage** or add new rules
- Wants to assess **type safety** (TypeScript strictness, Python type hints)
- Needs to check **documentation coverage** (JSDoc, docstrings, README)
- Uses keywords: `audit`, `tech debt`, `code quality`, `health check`, `complexity`, `dead code`, `duplication`

---

## Step-by-Step Instructions

### 1. Codebase Health Report

Generate a comprehensive report covering all quality dimensions:

```
CODEBASE HEALTH REPORT
══════════════════════════════════════════════════════════════
Project: <project-name>
Date: <YYYY-MM-DD>
Assessed by: AI Code Quality Audit

OVERALL HEALTH SCORE: 72/100 (Fair)

╔════════════════════════╤═══════╤═════════════════════════════╗
║ Dimension              │ Score │ Status                      ║
╠════════════════════════╪═══════╪═════════════════════════════╣
║ Code Complexity        │ 65    │ ⚠ Several high-complexity   ║
║ Dependency Health      │ 80    │ ✓ Mostly up-to-date         ║
║ Dead Code              │ 70    │ ⚠ Some unused exports       ║
║ Code Duplication       │ 60    │ ⚠ 8% duplication            ║
║ Architecture           │ 85    │ ✓ Good layer separation     ║
║ Performance            │ 70    │ ⚠ N+1 queries found         ║
║ Linting                │ 90    │ ✓ Comprehensive rules       ║
║ Type Safety            │ 55    │ ✗ 45% untyped functions     ║
║ Documentation          │ 60    │ ⚠ Missing API docs          ║
║ Test Coverage          │ 75    │ ✓ Good, missing edge cases  ║
╚════════════════════════╧═══════╧═════════════════════════════╝
```

---

### 2. Code Complexity Metrics

**Cyclomatic Complexity:** Number of independent paths through a function.

```
CYCLOMATIC COMPLEXITY THRESHOLDS
══════════════════════════════════════════════════════════════
1-10   ✓ Simple, low risk
11-20  ⚠ Moderate complexity, consider refactoring
21-50  ✗ High complexity, refactor recommended
50+    ✗✗ Untestable, refactor required
```

**Cognitive Complexity:** How hard the code is for a human to understand (weighted by nesting).

**Tools:**

```bash
# Python — radon
pip install radon
radon cc src/ -a -s              # Cyclomatic complexity
radon mi src/ -s                  # Maintainability index
radon hal src/                    # Halstead metrics

# JavaScript/TypeScript — eslint with complexity rule
# .eslintrc.json
{
  "rules": {
    "complexity": ["warn", { "max": 10 }],
    "max-depth": ["warn", { "max": 4 }],
    "max-lines-per-function": ["warn", { "max": 50 }]
  }
}

# Multi-language — SonarQube, CodeClimate
```

**Audit output example:**

```
HIGH COMPLEXITY FUNCTIONS (Cyclomatic > 15)
══════════════════════════════════════════════════════════════
File                        Function              CC   Lines
────────────────────────────────────────────────────────────
src/orders/processor.py     process_order()       28   145
src/auth/permissions.py     check_access()        22   98
src/reports/generator.py    build_report()        19   112
src/utils/validators.py     validate_input()      17   76

RECOMMENDATION: Extract sub-functions, use strategy pattern,
                replace nested conditionals with early returns.
```

---

### 3. Technical Debt Identification & Prioritization

```
TECHNICAL DEBT QUADRANT
══════════════════════════════════════════════════════════════

             Deliberate              Inadvertent
           ┌─────────────────┬─────────────────────┐
Reckless   │ "We don't have  │ "What's layering?"  │
           │  time for tests"│                     │
           │  → High risk    │  → Training needed  │
           ├─────────────────┼─────────────────────┤
Prudent    │ "Ship now,      │ "Now we know how    │
           │  refactor later"│  it should've been" │
           │  → Track in     │  → Refactor when    │
           │    backlog       │    touching area    │
           └─────────────────┴─────────────────────┘

DEBT PRIORITIZATION MATRIX:
Priority = Impact × Frequency × Fix Cost (inverse)

HIGH PRIORITY (fix now):
- Security vulnerabilities in dependencies
- No error handling in critical paths
- Missing input validation on public APIs
- Hardcoded credentials or secrets

MEDIUM PRIORITY (plan to fix):
- High-complexity functions (CC > 20)
- Code duplication > 5%
- Outdated major dependency versions
- Missing tests for critical business logic

LOW PRIORITY (fix opportunistically):
- Minor style inconsistencies
- TODO/FIXME comments
- Suboptimal but working algorithms
- Missing documentation on internal utilities
```

**Scanning for debt signals:**

```bash
# Count TODO/FIXME/HACK/WORKAROUND comments
grep -rn "TODO\|FIXME\|HACK\|WORKAROUND\|XXX\|TEMP" src/ | wc -l
grep -rn "TODO\|FIXME\|HACK" src/ --include="*.py" | sort

# Find functions longer than 100 lines (Python)
awk '/^def /{name=$0; line=NR} /^def /||/^class /{if(NR-line>100) print line": "name}' src/**/*.py

# Find large files (often a sign of needed refactoring)
find src/ -name "*.py" -exec wc -l {} + | sort -rn | head -20
```

---

### 4. Dependency Health

```bash
# Python
pip list --outdated
pip-audit                          # Security vulnerabilities
safety check                       # Known vulnerabilities

# Node.js
npm outdated
npm audit
npx depcheck                       # Find unused dependencies

# Multi-language
# Use Dependabot or Renovate for automated updates
```

**Audit output:**

```
DEPENDENCY HEALTH REPORT
══════════════════════════════════════════════════════════════
Total dependencies: 47
  Direct: 23
  Transitive: 24

OUTDATED PACKAGES:
  ✗ MAJOR updates (breaking): 3
    react 17.0.2 → 18.2.0
    typescript 4.9.5 → 5.3.3
    webpack 4.46.0 → 5.89.0

  ⚠ MINOR updates: 7
  ✓ PATCH updates: 12

SECURITY VULNERABILITIES:
  ✗ Critical: 0
  ✗ High: 1 (lodash prototype pollution — CVE-2021-23337)
  ⚠ Medium: 2
  ℹ Low: 3

UNUSED DEPENDENCIES: 4
  - moment (replaced by date-fns but not removed)
  - chalk (only used in removed script)
  - lodash.merge (can use native spread)
  - @types/express (no Express code found)
```

---

### 5. Dead Code Detection

```bash
# Python — vulture
pip install vulture
vulture src/ --min-confidence 80

# JavaScript/TypeScript — ts-prune (unused exports)
npx ts-prune

# ESLint — no-unused-vars, no-unreachable
npx eslint src/ --rule '{"no-unused-vars": "error"}'

# Generic — coverage-based detection
# Code with 0% coverage across all tests may be dead
pytest --cov=src --cov-report=html
# Look for files/functions with 0% coverage
```

**What to look for:**

```
DEAD CODE INDICATORS
══════════════════════════════════════════════════════════════
✗ Exported functions/classes never imported elsewhere
✗ Entire files never imported
✗ Feature flags that have been permanently on/off
✗ Commented-out code blocks
✗ Functions that are only called from other dead functions
✗ Unused CSS classes (PurgeCSS can detect these)
✗ Unreachable code after return/throw/break
✗ Unused database tables/columns
✗ Deprecated API endpoints still in code
```

---

### 6. Code Duplication Analysis

```bash
# Multi-language — jscpd
npx jscpd src/ --min-lines 5 --min-tokens 50 --reporters html

# Python — pylint duplicate detection
pylint --disable=all --enable=duplicate-code src/

# Output format
jscpd --reporters console --format "python" src/
```

**Duplication thresholds:**

```
DUPLICATION THRESHOLDS
══════════════════════════════════════════════════════════════
0-3%    ✓ Excellent — minimal duplication
3-5%    ✓ Good — acceptable for most projects
5-10%   ⚠ Fair — refactoring opportunities exist
10-20%  ✗ Poor — significant duplication, DRY violations
20%+    ✗✗ Critical — likely copy-paste programming
```

**Remediation strategies:**

```
DEDUPLICATION STRATEGIES
══════════════════════════════════════════════════════════════
1. Extract shared function     → Common logic to a utility
2. Extract base class          → Shared behavior in hierarchy
3. Use composition             → Assemble from reusable parts
4. Template method pattern     → Share algorithm, vary steps
5. Configuration over code     → Data-driven instead of branches
6. Generic/parameterized       → One function, multiple uses

WARNING: Not all duplication is bad.
- 2-3 lines of similar setup code: often fine
- Test code repetition: often clearer than DRY tests
- Forced by framework patterns: accept it
```

---

### 7. Architecture Adherence Verification

```
LAYERED ARCHITECTURE RULES
══════════════════════════════════════════════════════════════

  ┌──────────────┐
  │ Presentation │  → Can call: Application
  │ (API/UI)     │  → Cannot call: Domain, Infrastructure directly
  ├──────────────┤
  │ Application  │  → Can call: Domain, Infrastructure (via ports)
  │ (Services)   │  → Cannot call: Presentation
  ├──────────────┤
  │ Domain       │  → Can call: Nothing external
  │ (Entities)   │  → No framework imports here
  ├──────────────┤
  │ Infra        │  → Implements: Domain ports/interfaces
  │ (DB, API)    │  → Cannot call: Application, Presentation
  └──────────────┘

CHECK FOR VIOLATIONS:
- Does a controller import a repository directly?
- Does a domain entity import Flask/Express/Django?
- Does infrastructure call application services?
- Are there circular imports between layers?
```

```bash
# Python — import-linter
pip install import-linter
# importlinter.ini
[importlinter]
root_package = myapp

[importlinter:contract:layers]
name = Application layers
type = layers
layers =
    myapp.presentation
    myapp.application
    myapp.domain
    myapp.infrastructure

lint-imports
```

---

### 8. Performance Bottleneck Identification

```
STATIC PERFORMANCE CHECKS
══════════════════════════════════════════════════════════════

1. N+1 QUERIES
   Look for: ORM queries inside loops
   Example: for user in users: user.orders.all()  # N+1!
   Fix: Use select_related() / joinedload() / include()

2. MISSING INDEXES
   Look for: WHERE/ORDER BY on unindexed columns
   Check: EXPLAIN ANALYZE on critical queries

3. UNBOUNDED QUERIES
   Look for: SELECT * without LIMIT
   Fix: Always paginate list endpoints

4. SYNCHRONOUS I/O IN ASYNC CONTEXT
   Look for: Blocking calls in async functions
   Fix: Use async equivalents (aiohttp, asyncpg)

5. MEMORY-INTENSIVE PATTERNS
   Look for: Loading entire datasets into memory
   Fix: Stream/paginate large results

6. MISSING CACHING
   Look for: Repeated expensive computations
   Fix: Add caching with TTL for stable data

7. STRING CONCATENATION IN LOOPS
   Look for: result += string in a loop
   Fix: Use list join or StringBuilder
```

---

### 9. Linting Rule Coverage

```
LINTING AUDIT CHECKLIST
══════════════════════════════════════════════════════════════

Python:
  □ ruff or flake8 with comprehensive rule set
  □ mypy or pyright for type checking
  □ bandit for security linting
  □ isort for import ordering
  □ black/ruff format for formatting

JavaScript/TypeScript:
  □ ESLint with recommended + framework rules
  □ TypeScript strict mode enabled
  □ Prettier for formatting
  □ eslint-plugin-security
  □ eslint-plugin-import (import order, no unused)

CI Integration:
  □ Lint runs on every PR
  □ Zero tolerance for errors (warnings allowed temporarily)
  □ Pre-commit hooks for local enforcement
  □ Auto-fix where possible (--fix)
```

---

### 10. Type Safety Assessment

```
TYPE SAFETY LEVELS
══════════════════════════════════════════════════════════════

TypeScript:
  Level 1: strict: false, lots of 'any'         → Poor
  Level 2: strict: true, some @ts-ignore         → Fair
  Level 3: strict: true, no 'any', no @ts-ignore → Good
  Level 4: + exhaustive checks, branded types    → Excellent

Python:
  Level 1: No type hints                         → Poor
  Level 2: Some type hints, no type checker      → Fair
  Level 3: Type hints + mypy (basic mode)        → Good
  Level 4: mypy --strict, all code typed         → Excellent
```

```bash
# TypeScript — count 'any' usage
grep -rn ": any" src/ --include="*.ts" --include="*.tsx" | wc -l
grep -rn "@ts-ignore\|@ts-expect-error" src/ | wc -l

# Python — mypy coverage
mypy src/ --txt-report mypy_report
# Or use pyright for stricter checking
```

---

### 11. Documentation Coverage

```
DOCUMENTATION AUDIT
══════════════════════════════════════════════════════════════

PUBLIC API DOCUMENTATION:
  □ All public functions have docstrings/JSDoc
  □ Parameters are described with types and constraints
  □ Return values are documented
  □ Exceptions/errors are documented
  □ Examples are provided for complex functions

PROJECT DOCUMENTATION:
  □ README with setup instructions
  □ Architecture decision records (ADRs)
  □ API documentation (OpenAPI/Swagger)
  □ Contributing guide
  □ Changelog maintained
  □ Environment variables documented

INLINE DOCUMENTATION:
  □ Complex algorithms explained with comments
  □ Business rules referenced (ticket numbers)
  □ "Why" comments for non-obvious decisions
  □ No outdated/misleading comments
```

```bash
# Python — interrogate (docstring coverage)
pip install interrogate
interrogate src/ -v --fail-under 80

# JavaScript — jsdoc coverage
npx jsdoc-coverage src/
```

---

## Audit Report Template

```markdown
# Code Quality Audit Report

**Project:** <name>
**Date:** <YYYY-MM-DD>
**Scope:** <files/directories audited>

## Executive Summary
Overall health: X/100
Key finding: <one-sentence summary>

## Critical Issues (Fix Immediately)
1. [Issue] — [Impact] — [Recommended Fix]

## High Priority (Plan This Sprint)
1. [Issue] — [Impact] — [Recommended Fix]

## Medium Priority (Plan This Quarter)
1. [Issue] — [Impact] — [Recommended Fix]

## Low Priority (Fix Opportunistically)
1. [Issue] — [Impact] — [Recommended Fix]

## Metrics Summary
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Cyclomatic Complexity (avg) | X | <10 | ⚠/✓/✗ |
| Code Duplication | X% | <5% | ⚠/✓/✗ |
| Test Coverage | X% | >80% | ⚠/✓/✗ |
| Type Coverage | X% | >90% | ⚠/✓/✗ |
| Doc Coverage | X% | >80% | ⚠/✓/✗ |
| Outdated Deps | X | 0 critical | ⚠/✓/✗ |

## Recommended Actions (Prioritized)
1. ...
2. ...
3. ...
```

---

## Best Practices

1. **Audit regularly** — schedule quarterly health checks, not just when things break
2. **Automate what you can** — linting, type checking, dep audits belong in CI
3. **Track trends** — a single snapshot is less useful than seeing direction over time
4. **Prioritize by impact** — fix what causes the most bugs or slowdowns first
5. **Don't pursue perfection** — 80% quality across everything beats 100% in one area
6. **Make debt visible** — track tech debt items alongside feature work in your backlog
7. **Celebrate improvements** — share the metrics getting better with the team
8. **Set thresholds, not rules** — "complexity < 15" is better than "rewrite everything"
9. **Audit tests too** — test code quality matters as much as production code
10. **Include the team** — audits work best as collaborative reviews, not blame sessions

---

## Related Skills

- `testing-anti-patterns` — test quality assessment
- `systematic-debugging` — use audit findings to guide debugging
- `tdd-bdd-patterns` — improve test coverage identified in audits
