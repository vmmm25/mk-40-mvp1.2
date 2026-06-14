---
name: codebase-health-reporter
version: 1.0.0
description: >
  Automated codebase health auditing and reporting. Generates comprehensive health reports
  covering technical debt score, test coverage gaps, dependency freshness, code complexity
  hotspots, architecture drift, documentation staleness, and security vulnerabilities.
  Outputs structured Markdown reports with severity levels (critical, warning, info) and
  actionable recommendations.
tags:
  - code-quality
  - technical-debt
  - health-report
  - test-coverage
  - dependency-audit
  - complexity
  - architecture
  - documentation
  - security
  - productivity
author: garri333
license: MIT
source: Inspired by Codebase Health Reporter from MCP Market (emerging skill for Swift/general projects)
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# codebase-health-reporter

Automated codebase health auditing. Generate comprehensive reports covering technical debt, test coverage, dependency freshness, code complexity, architecture drift, documentation staleness, and security vulnerabilities with severity-based prioritization.

---

## When to Activate

Activate this skill when the user:

- Asks for a **codebase health check** or **project audit**
- Wants to assess **technical debt** levels and prioritize remediation
- Needs a **test coverage analysis** or wants to find untested code paths
- Asks about **dependency freshness** or outdated packages
- Wants to identify **code complexity hotspots** or refactoring candidates
- Needs to detect **architecture drift** from intended design patterns
- Asks about **documentation staleness** or missing docs
- Wants a **security vulnerability scan** of dependencies
- Needs a **metrics dashboard** for the project
- Is preparing for a **sprint planning** and needs to allocate tech debt work
- Uses keywords: `health report`, `code quality`, `tech debt`, `audit`, `coverage gaps`, `complexity`, `outdated dependencies`

---

## Step-by-Step Instructions

### 1. Health Report Architecture

```
CODEBASE HEALTH REPORTER PIPELINE
══════════════════════════════════════════════════════════════

  ┌──────────────────┐
  │   CODEBASE       │
  │   SCAN           │
  │                  │
  │ • File tree      │
  │ • Git history    │
  │ • Package files  │
  │ • Config files   │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │                   ANALYZERS                          │
  │                                                      │
  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
  │  │ Tech    │ │ Test    │ │ Deps    │ │ Complexity│  │
  │  │ Debt    │ │ Coverage│ │ Freshness│ │ Analysis │  │
  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │
  │  │ Arch    │ │ Doc     │ │ Security│               │
  │  │ Drift   │ │ Stale   │ │ Vulns   │               │
  │  └─────────┘ └─────────┘ └─────────┘               │
  └──────────────────────┬───────────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────┐
  │              REPORT GENERATOR                        │
  │                                                      │
  │  • Overall health score (0-100)                      │
  │  • Severity breakdown (critical/warning/info)        │
  │  • Actionable recommendations                        │
  │  • Trend comparison (vs. last report)                │
  └──────────────────────────────────────────────────────┘
```

---

### 2. Metrics Dashboard

Collect and present these core metrics:

```
METRICS DASHBOARD
══════════════════════════════════════════════════════════════

Metric                    │ Value      │ Status   │ Trend
──────────────────────────┼────────────┼──────────┼──────
Lines of Code (LoC)       │ 24,350     │ ℹ️ info  │ ↑ +12%
Cyclomatic Complexity Avg │ 8.3        │ ⚠️ warn  │ ↑ +0.7
Max Cyclomatic Complexity │ 42         │ 🔴 crit  │ ↑ +5
Test/Code Ratio           │ 0.34       │ ⚠️ warn  │ ↓ -0.02
Test Coverage %           │ 62%        │ ⚠️ warn  │ → stable
Dependency Count          │ 87         │ ℹ️ info  │ ↑ +3
Outdated Packages         │ 14         │ ⚠️ warn  │ ↑ +6
Security Vulnerabilities  │ 2 high     │ 🔴 crit  │ ↑ +1
Documentation Coverage    │ 45%        │ ⚠️ warn  │ ↓ -5%
TODO/FIXME/HACK Count     │ 23         │ ⚠️ warn  │ ↑ +4
Dead Code Estimate        │ ~1,200 LoC │ ⚠️ warn  │ → stable
──────────────────────────┼────────────┼──────────┼──────
OVERALL HEALTH SCORE      │ 58/100     │ ⚠️ WARN  │ ↓ -4
══════════════════════════════════════════════════════════════
```

---

### 3. Technical Debt Analysis

1. **Scan for debt markers**: Search for `TODO`, `FIXME`, `HACK`, `WORKAROUND`, `TEMPORARY`, `XXX` in source files
2. **Categorize debt**:
   - **Design debt**: Architecture shortcuts, missing abstractions
   - **Code debt**: Duplicated code, complex functions, missing types
   - **Test debt**: Low coverage, missing edge cases, flaky tests
   - **Documentation debt**: Missing READMEs, outdated API docs, no JSDoc/docstrings
   - **Dependency debt**: Outdated packages, deprecated APIs, version conflicts
3. **Calculate debt score**: Weighted sum of all debt categories (0-100, lower is better)
4. **Estimate remediation effort**: Hours to resolve each item

```yaml
# Technical Debt Report Structure
technical_debt:
  score: 37  # out of 100 (lower = less debt)
  categories:
    design_debt:
      score: 8
      items:
        - severity: warning
          file: "src/services/userService.ts"
          description: "God class with 15 methods — split into focused services"
          effort: "4h"
        - severity: critical
          file: "src/api/"
          description: "No error handling middleware — all errors return 500"
          effort: "2h"
    code_debt:
      score: 12
      items:
        - severity: warning
          file: "src/utils/helpers.ts"
          description: "3 duplicated validation functions across files"
          effort: "1h"
        - severity: info
          file: "src/components/"
          description: "12 components missing PropTypes/TypeScript interfaces"
          effort: "3h"
    test_debt:
      score: 9
      items:
        - severity: critical
          file: "src/services/paymentService.ts"
          description: "Payment processing has 0% test coverage"
          effort: "6h"
    dependency_debt:
      score: 8
      items:
        - severity: critical
          package: "lodash@4.17.15"
          description: "Known prototype pollution vulnerability (CVE-2021-23337)"
          fix: "npm update lodash@4.17.21"
          effort: "15m"
```

---

### 4. Test Coverage Gap Analysis

1. **Map source files to test files** using naming conventions (`*.test.ts`, `*.spec.ts`, `test_*.py`)
2. **Identify files with no tests**: List source files missing corresponding test files
3. **Analyze coverage by module**: Group coverage percentages by directory/module
4. **Find critical untested paths**: Identify business-critical code without tests
5. **Suggest priority test targets**: Rank by risk × change frequency

```
TEST COVERAGE GAP ANALYSIS
══════════════════════════════════════════════════════════════

Module                    │ Files │ Tested │ Coverage │ Risk
──────────────────────────┼───────┼────────┼──────────┼──────
src/services/             │ 8     │ 5      │ 58%      │ HIGH
src/api/routes/           │ 12    │ 9      │ 71%      │ HIGH
src/components/           │ 24    │ 18     │ 73%      │ MED
src/utils/                │ 6     │ 6      │ 92%      │ LOW
src/middleware/           │ 4     │ 1      │ 22%      │ CRIT
src/models/               │ 7     │ 7      │ 85%      │ LOW

CRITICAL UNTESTED FILES (business-critical, 0% coverage):
  🔴 src/services/paymentService.ts (changed 14 times in last 30 days)
  🔴 src/middleware/authMiddleware.ts (security-critical)
  🔴 src/services/billingService.ts (financial data processing)

PRIORITY TEST TARGETS (by risk × change frequency):
  1. paymentService.ts — risk: critical, changes: 14 → WRITE TESTS FIRST
  2. authMiddleware.ts — risk: critical, changes: 8 → WRITE TESTS SECOND
  3. userService.ts — risk: high, changes: 22 → WRITE TESTS THIRD
══════════════════════════════════════════════════════════════
```

---

### 5. Dependency Freshness Check

1. **Parse package files**: `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, etc.
2. **Check current vs. latest versions** for each dependency
3. **Categorize staleness**: Current, minor behind, major behind, deprecated, EOL
4. **Check for security advisories**: Cross-reference with CVE databases
5. **Calculate dependency health score**

```
DEPENDENCY FRESHNESS REPORT
══════════════════════════════════════════════════════════════

Package          │ Current  │ Latest   │ Status       │ Risk
─────────────────┼──────────┼──────────┼──────────────┼──────
react            │ 18.2.0   │ 19.1.0   │ MAJOR BEHIND │ MED
express          │ 4.18.2   │ 4.21.2   │ MINOR BEHIND │ LOW
lodash           │ 4.17.15  │ 4.17.21  │ SECURITY     │ CRIT
typescript       │ 5.3.2    │ 5.7.3    │ MINOR BEHIND │ LOW
next             │ 14.0.4   │ 15.2.0   │ MAJOR BEHIND │ MED
prisma           │ 5.7.0    │ 6.4.1    │ MAJOR BEHIND │ MED
jsonwebtoken     │ 8.5.1    │ 9.0.2    │ MAJOR BEHIND │ HIGH
axios            │ 0.27.2   │ 1.7.9    │ MAJOR BEHIND │ MED
─────────────────┼──────────┼──────────┼──────────────┼──────
FRESHNESS SCORE  │          │          │ 42/100       │ WARN

SECURITY ADVISORIES:
  🔴 lodash@4.17.15: Prototype Pollution (CVE-2021-23337) — UPDATE IMMEDIATELY
  🔴 jsonwebtoken@8.5.1: Insecure key handling (CVE-2022-23529) — UPDATE IMMEDIATELY
══════════════════════════════════════════════════════════════
```

---

### 6. Code Complexity Hotspots

1. **Calculate cyclomatic complexity** for all functions/methods
2. **Identify hotspots**: Functions with complexity > 10
3. **Map change frequency**: Cross-reference with git log for churn rate
4. **Prioritize refactoring**: High complexity + high change frequency = top priority

```
CODE COMPLEXITY HOTSPOTS
══════════════════════════════════════════════════════════════

File:Function                      │ CC  │ LoC │ Changes │ Priority
───────────────────────────────────┼─────┼─────┼─────────┼─────────
services/orderService:processOrder │ 42  │ 280 │ 14      │ 🔴 CRIT
api/routes/users:handleUserUpdate  │ 28  │ 195 │ 22      │ 🔴 CRIT
utils/parser:parseConfig           │ 25  │ 150 │ 3       │ ⚠️ WARN
services/billing:calculateInvoice  │ 22  │ 170 │ 11      │ 🔴 CRIT
components/Dashboard:render        │ 19  │ 240 │ 18      │ 🔴 CRIT
middleware/auth:validateToken      │ 15  │ 85  │ 5       │ ⚠️ WARN
───────────────────────────────────┼─────┼─────┼─────────┼─────────

REFACTORING RECOMMENDATIONS:
  1. processOrder (CC=42): Extract into OrderValidator, OrderProcessor,
     OrderNotifier sub-functions
  2. handleUserUpdate (CC=28): Use strategy pattern for different update
     types instead of nested if/else
  3. Dashboard.render (CC=19): Split into sub-components (DashboardHeader,
     DashboardMetrics, DashboardCharts)

CC = Cyclomatic Complexity | LoC = Lines of Code | Changes = last 90 days
══════════════════════════════════════════════════════════════
```

---

### 7. Architecture Drift Detection

1. **Define intended architecture**: Read from `ARCHITECTURE.md`, folder structure conventions, or user input
2. **Scan actual imports and dependencies**: Build a dependency graph
3. **Compare actual vs. intended**: Identify violations of layered architecture, circular dependencies, wrong-direction imports
4. **Report drift severity**: Critical (security boundary violation), warning (layer skip), info (style inconsistency)

```
ARCHITECTURE DRIFT REPORT
══════════════════════════════════════════════════════════════
Intended Architecture: Layered (Routes → Services → Repositories → Models)

VIOLATIONS FOUND: 7
──────────────────────────────────────────────────────────────

🔴 CRITICAL: Route directly accesses database
   File: src/api/routes/users.ts:45
   Import: import { prisma } from '../../db/client'
   Expected: Route should call UserService, not database directly
   Fix: Move DB query to UserRepository, call via UserService

⚠️ WARNING: Circular dependency detected
   Path: services/orderService → services/userService → services/orderService
   Fix: Extract shared logic into a common module

⚠️ WARNING: Service layer skipped
   File: src/api/routes/reports.ts:12
   Import: import { ReportRepository } from '../../repositories/reportRepo'
   Expected: Route → ReportService → ReportRepository
   Fix: Create ReportService as intermediary

ℹ️ INFO: Component imports from wrong directory
   File: src/components/Dashboard/Chart.tsx:3
   Import: import { formatDate } from '../../services/utils'
   Expected: Shared utils should be in src/utils/, not src/services/
   Fix: Move formatDate to src/utils/dateUtils.ts
══════════════════════════════════════════════════════════════
```

---

### 8. Documentation Staleness Check

1. **Inventory documentation files**: README.md, CONTRIBUTING.md, API docs, JSDoc/docstrings
2. **Compare doc timestamps with code changes**: If code changed but docs didn't, flag as stale
3. **Check for broken links and references**: Verify internal doc links are valid
4. **Measure documentation coverage**: % of exported functions/classes with docs

```
DOCUMENTATION STALENESS REPORT
══════════════════════════════════════════════════════════════

Document                    │ Last Updated │ Code Changed │ Status
────────────────────────────┼──────────────┼──────────────┼────────
README.md                   │ 2025-11-15   │ 2026-02-20   │ 🔴 STALE
API.md                      │ 2026-01-03   │ 2026-02-18   │ ⚠️ STALE
CONTRIBUTING.md             │ 2025-09-22   │ N/A          │ ⚠️ OLD
src/services/README.md      │ (missing)    │ 2026-02-21   │ 🔴 MISSING
CHANGELOG.md                │ (missing)    │ N/A          │ ℹ️ MISSING

DOCUMENTATION COVERAGE:
  Exported functions with JSDoc/docstrings: 34/89 (38%)
  Public API endpoints documented: 15/22 (68%)
  Configuration options documented: 8/14 (57%)

BROKEN LINKS:
  🔴 README.md:45 → docs/deployment.md (file not found)
  🔴 API.md:112 → #get-user-by-id (anchor not found, endpoint renamed)
══════════════════════════════════════════════════════════════
```

---

### 9. Generate Final Health Report

Compile all analyses into a single structured Markdown report:

```markdown
# Codebase Health Report
**Project**: my-project | **Date**: 2026-02-22 | **Overall Score**: 58/100 ⚠️

## Executive Summary
The codebase has moderate technical debt with critical issues in security
(2 vulnerable dependencies) and test coverage (payment processing untested).
Immediate action needed on dependency updates and auth middleware testing.

## Critical Issues (Action Required)
1. 🔴 lodash@4.17.15 — Prototype pollution vulnerability
2. 🔴 paymentService.ts — Zero test coverage on financial code
3. 🔴 Route bypasses service layer to access database directly

## Metrics Dashboard
[See Section 2 output]

## Detailed Reports
- [Technical Debt Analysis](#technical-debt)
- [Test Coverage Gaps](#test-coverage)
- [Dependency Freshness](#dependencies)
- [Complexity Hotspots](#complexity)
- [Architecture Drift](#architecture)
- [Documentation Staleness](#documentation)

## Recommended Action Plan
| Priority | Action                        | Effort | Impact |
|----------|-------------------------------|--------|--------|
| P0       | Update lodash + jsonwebtoken  | 30m    | High   |
| P0       | Write payment service tests   | 6h     | High   |
| P1       | Fix route→DB direct access    | 2h     | Medium |
| P1       | Reduce processOrder CC from 42| 4h     | Medium |
| P2       | Update README.md              | 1h     | Low    |
| P2       | Add service layer READMEs     | 2h     | Low    |
```

---

## Best Practices

1. **Run health checks regularly**: Schedule weekly or per-sprint audits to catch drift early
2. **Focus on trends, not absolutes**: A score of 60 improving by 5 each sprint is better than a static 75
3. **Prioritize by risk × impact**: Critical security + high-change-frequency items first
4. **Automate what you can**: Integrate dependency checks and complexity analysis into CI/CD
5. **Compare over time**: Always include trend indicators (↑↓→) so the team sees progress
6. **Be actionable**: Every finding must include a specific remediation step and effort estimate
7. **Don't overwhelm**: Limit recommendations to top 5-10 actionable items per report
8. **Adapt thresholds**: Adjust complexity and coverage thresholds to match team maturity
9. **Include positive signals**: Celebrate improvements and well-maintained modules
10. **Share with the team**: Reports should be committed to the repo for visibility

---

## Examples

### Example 1: Quick Health Check

**User**: "Give me a quick health check of this project."

**Agent**:
1. Scans file tree, package.json, test files, git log
2. Produces a condensed dashboard:

```
QUICK HEALTH CHECK — my-api-project
══════════════════════════════════════
Overall: 71/100 ✅ GOOD

✅ Test coverage: 78% (target: 75%)
✅ Dependencies: 2 minor updates available
⚠️ Complexity: 3 functions above threshold (CC > 15)
⚠️ Docs: README last updated 45 days ago
ℹ️ LoC: 12,400 | Files: 89 | Deps: 42

Top action: Refactor orderProcessor (CC=28)
══════════════════════════════════════
```

### Example 2: Full Audit Report for Sprint Planning

**User**: "Generate a full codebase health report. We're planning the next sprint and need to allocate time for tech debt."

**Agent**:
1. Runs all 7 analyzers (debt, coverage, deps, complexity, arch, docs, security)
2. Generates the comprehensive report from Section 9
3. Produces a prioritized backlog of tech debt items:

```
SPRINT TECH DEBT BACKLOG
══════════════════════════════════════════════════════════════

Total estimated effort: 24.5 hours

Ticket │ Description                         │ Effort │ Priority
───────┼─────────────────────────────────────┼────────┼─────────
TD-001 │ Fix lodash + jwt vulnerabilities    │ 0.5h   │ P0
TD-002 │ Write paymentService tests          │ 6h     │ P0
TD-003 │ Add auth middleware tests           │ 3h     │ P0
TD-004 │ Fix route→DB architectural violation│ 2h     │ P1
TD-005 │ Refactor processOrder (CC=42)       │ 4h     │ P1
TD-006 │ Break circular dependency cycle     │ 1.5h   │ P1
TD-007 │ Update README and API docs          │ 2h     │ P2
TD-008 │ Add missing component PropTypes     │ 3h     │ P2
TD-009 │ Remove dead code (~1,200 LoC)       │ 2.5h   │ P2

Recommendation: Allocate 12h this sprint for P0+P1 items.
Leave P2 for next sprint.
══════════════════════════════════════════════════════════════
```

### Example 3: Track Health Over Time

**User**: "Compare this report with last month's."

```
HEALTH TREND COMPARISON
══════════════════════════════════════════════════════════════
                        │ Jan 2026 │ Feb 2026 │ Change
────────────────────────┼──────────┼──────────┼────────
Overall Score           │ 62       │ 58       │ ↓ -4  ⚠️
Test Coverage           │ 64%      │ 62%      │ ↓ -2% ⚠️
Dependency Freshness    │ 55       │ 42       │ ↓ -13 🔴
Complexity (avg CC)     │ 7.6      │ 8.3      │ ↑ +0.7 ⚠️
Tech Debt Items         │ 18       │ 23       │ ↑ +5  ⚠️
Security Vulns          │ 1        │ 2        │ ↑ +1  🔴
Doc Coverage            │ 50%      │ 45%      │ ↓ -5% ⚠️

TREND: ⚠️ Health is declining. Dependency updates and security
patches have been deferred too long. Recommend dedicating a
full sprint to tech debt remediation.
══════════════════════════════════════════════════════════════
```
