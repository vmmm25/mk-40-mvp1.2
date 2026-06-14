---
name: goose-code-review
version: 1.0.0
description: >
  Automated code review skill following enterprise standards. Performs pull request analysis
  including architecture review, security scanning, performance profiling, test coverage
  verification, dependency audit, and accessibility checks with conventional comments format.
tags:
  - code-review
  - pull-request
  - security
  - performance
  - testing
  - accessibility
  - architecture
  - best-practices
  - enterprise
  - goose
author: garri333
license: MIT
source: block/agent-skills
marketplace: https://block.github.io/goose/skills
compatible:
  - goose
  - claude-desktop
  - skill-md-standard
---

# goose-code-review

Automated code review skill following enterprise standards. Analyzes pull requests across multiple dimensions: architecture, security, performance, testing, dependencies, and accessibility. Uses conventional comments format with blocking vs. non-blocking feedback differentiation.

---

## When to Activate

Activate this skill when the user:

- Asks for a **code review** of a file, diff, or pull request
- Wants **architecture feedback** on a code change
- Requests a **security review** of code changes
- Needs **performance analysis** of new or modified code
- Asks to verify **test coverage** for a change
- Wants a **dependency audit** for new or updated packages
- Requests an **accessibility check** on frontend code
- Wants to generate **review comments** in conventional format
- Mentions review keywords: `review`, `PR`, `pull request`, `code quality`, `feedback`

---

## Step-by-Step Instructions

### 1. Identify the PR Type

Determine the review template based on PR type:

| PR Type | Focus Areas | Depth |
|---|---|---|
| **Feature** | Architecture, security, tests, docs, accessibility | Full review |
| **Bugfix** | Root cause, regression tests, side effects | Targeted review |
| **Refactor** | Behavior preservation, readability, performance | Structural review |
| **Dependency Update** | CVE check, breaking changes, license compliance | Audit review |
| **Hotfix** | Minimal change, correctness, rollback plan | Fast review |
| **Documentation** | Accuracy, completeness, formatting | Content review |

### 2. Perform Multi-Dimensional Analysis

#### 2.1 Architecture Review

```
ARCHITECTURE CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━
□ Follows established project patterns and conventions
□ Proper separation of concerns (layers, modules)
□ No circular dependencies introduced
□ API contracts are backward compatible (or versioned)
□ Error handling is consistent and comprehensive
□ Logging is appropriate (not excessive, not missing)
□ Configuration is externalized (no hardcoded values)
□ Database schema changes are migration-safe
□ New abstractions are justified and well-documented
□ SOLID principles respected
□ DRY — no unnecessary duplication
□ Single Responsibility — each function/class has one job
```

#### 2.2 Security Scanning

```
SECURITY CHECKLIST:
━━━━━━━━━━━━━━━━━━
□ No secrets, API keys, or credentials in code
□ Input validation on all user-supplied data
□ Output encoding/escaping (XSS prevention)
□ Parameterized queries (SQL injection prevention)
□ Authentication checks on protected endpoints
□ Authorization checks (role/permission verification)
□ CORS configuration is restrictive and correct
□ Rate limiting on public-facing endpoints
□ Sensitive data not logged or exposed in errors
□ File uploads validated (type, size, content)
□ Dependencies checked for known CVEs
□ No use of eval(), innerHTML assignment, or unsafe patterns
```

#### 2.3 Performance Profiling

```
PERFORMANCE CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━
□ No N+1 query patterns
□ Database queries are indexed appropriately
□ Pagination implemented for list endpoints
□ Large data sets are streamed, not loaded entirely to memory
□ Caching strategy is appropriate
□ No blocking operations on the main thread / event loop
□ Lazy loading for heavy resources
□ Image/asset optimization
□ API payload size is reasonable
□ No unnecessary re-renders (React/Vue/Svelte)
□ Memoization used where appropriate
□ Time complexity of algorithms is acceptable for data size
```

#### 2.4 Test Coverage Verification

```
TESTING CHECKLIST:
━━━━━━━━━━━━━━━━━━
□ New code has corresponding unit tests
□ Edge cases and error paths are tested
□ Integration tests for API endpoints
□ Test names clearly describe behavior
□ Tests are independent (no shared mutable state)
□ Mocks/stubs are appropriate (not over-mocking)
□ Regression test for bugfixes
□ Coverage delta is positive or stable
□ Snapshot tests are intentional (not catch-all)
□ E2E tests for critical user flows (if applicable)
□ Test data is representative and well-structured
□ Flaky test patterns avoided
```

#### 2.5 Dependency Audit

```
DEPENDENCY CHECKLIST:
━━━━━━━━━━━━━━━━━━━━
□ New dependency is necessary (no existing alternative)
□ Package is actively maintained (recent commits, releases)
□ License is compatible (MIT, Apache-2.0, BSD preferred)
□ No known CVEs in the specified version
□ Bundle size impact is acceptable
□ Transitive dependencies reviewed
□ Lock file updated correctly
□ Peer dependency conflicts resolved
□ Package is widely adopted (downloads, stars, community)
□ Breaking changes from major version bumps addressed
```

#### 2.6 Accessibility Check

```
ACCESSIBILITY CHECKLIST (a11y):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Semantic HTML elements used (nav, main, article, etc.)
□ ARIA attributes correct and necessary
□ Keyboard navigation works (tab order, focus management)
□ Color contrast meets WCAG AA (4.5:1 text, 3:1 large)
□ Alt text for images and media
□ Form labels properly associated with inputs
□ Error messages are accessible and descriptive
□ Focus indicators visible
□ Screen reader tested (or VoiceOver/NVDA verified)
□ No reliance on color alone for information
□ Touch targets minimum 44x44 px (mobile)
□ Animations respect prefers-reduced-motion
```

### 3. Apply Conventional Comments Format

Use the [Conventional Comments](https://conventionalcomments.org/) format for all feedback:

```
<label> [decorations]: <subject>

[discussion]
```

#### Labels

| Label | Meaning | Blocking? |
|---|---|---|
| **blocker:** | Must be resolved before merge | ✅ Yes |
| **critical:** | Security or data integrity issue | ✅ Yes |
| **suggestion:** | Improvement recommendation | ❌ No |
| **nitpick:** | Minor style or preference | ❌ No |
| **question:** | Seeking clarification | ❌ No |
| **thought:** | Idea for future consideration | ❌ No |
| **praise:** | Positive feedback | ❌ No |
| **note:** | Informational observation | ❌ No |

#### Decorations

- `(non-blocking)` — Explicitly mark as non-blocking
- `(blocking)` — Explicitly mark as blocking
- `(if-minor)` — Only address if the change is small
- `(security)` — Security-related concern
- `(performance)` — Performance-related concern
- `(a11y)` — Accessibility-related concern

### 4. Differentiate Blocking vs. Non-Blocking

```
REVIEW VERDICT CRITERIA:
━━━━━━━━━━━━━━━━━━━━━━━

BLOCKING (Request Changes):
  → Security vulnerabilities
  → Data loss or corruption risk
  → Breaking API contracts without versioning
  → Missing tests for critical paths
  → Incorrect business logic
  → Production configuration exposed

NON-BLOCKING (Approve with Comments):
  → Style preferences
  → Minor naming improvements
  → Documentation additions
  → Optional performance optimizations
  → Future improvement suggestions
  → Alternative approaches worth considering
```

### 5. Generate Review Summary

```
PULL REQUEST REVIEW SUMMARY
════════════════════════════

PR: #1234 — Add user notification preferences
Author: @developer
Type: Feature
Files Changed: 12 | Additions: +340 | Deletions: -45

VERDICT: ⚠️ REQUEST CHANGES (2 blocking items)

Blocking:
  🔴 [security] Missing input validation on notification
     endpoint — user-supplied data passed directly to template
  🔴 [testing] No tests for notification preference update
     failure scenarios

Non-Blocking:
  🟡 [suggestion] Consider extracting notification template
     logic into a separate service
  🟡 [performance] N+1 query in getUserPreferences() — consider
     eager loading preferences relation
  🟢 [nitpick] Inconsistent naming: notifPref vs notificationPref
  🟢 [praise] Excellent error handling in the retry logic!

REVIEW SCORES:
  Architecture: ██████████ 8/10
  Security:     ████████░░ 6/10 (blocking issue)
  Performance:  █████████░ 7/10
  Testing:      ███████░░░ 5/10 (blocking issue)
  Accessibility: ██████████ N/A
  Code Quality: █████████░ 8/10
```

---

## Best Practices

1. **Be specific** — Reference exact lines and provide concrete suggestions, not vague feedback
2. **Explain the "why"** — Don't just say "this is wrong"; explain the problem and its consequences
3. **Offer alternatives** — When suggesting changes, provide example code
4. **Prioritize feedback** — Clearly distinguish blocking from non-blocking comments
5. **Acknowledge good work** — Include praise for well-written code
6. **Stay objective** — Focus on code quality, not personal style preferences
7. **Consider context** — A hotfix has different standards than a feature branch
8. **Review the tests** — Tests are code too; review them with the same rigor
9. **Check the PR description** — Ensure it explains the change and links to issues
10. **One review pass** — Batch all comments in a single review to avoid notification fatigue

---

## Examples

### Example 1: Feature PR Review

**User prompt:**
> "Review this PR that adds a new user settings API endpoint"

**Expected behavior:**

```
PULL REQUEST REVIEW: User Settings API
═══════════════════════════════════════

PR Type: Feature
Reviewing: src/api/settings.js, src/models/settings.js,
           tests/settings.test.js

──────────────────────────────────────

📄 src/api/settings.js

  blocker (security): Missing authentication middleware
  Line 15: router.post('/settings', updateSettings)
  
  This endpoint modifies user data but has no auth middleware.
  Any unauthenticated request can modify settings.
  
  Suggested fix:
    router.post('/settings', requireAuth, validateInput(settingsSchema), updateSettings)

  ───

  suggestion (performance): Consider caching user settings
  Line 42: const settings = await db.query('SELECT * FROM settings WHERE user_id = ?', [userId])
  
  User settings are read frequently but updated rarely.
  Consider adding a cache layer (Redis, 60s TTL) to reduce
  database load.

──────────────────────────────────────

📄 src/models/settings.js

  nitpick (non-blocking): Inconsistent naming convention
  Line 8: const get_user_settings = ...
  Line 22: const updateUserSettings = ...
  
  Mix of snake_case and camelCase. Project convention is
  camelCase — consider renaming get_user_settings → getUserSettings.

  ───

  praise: Excellent validation schema
  Lines 30-55: The Joi validation schema is thorough and
  well-documented. Great use of custom error messages.

──────────────────────────────────────

📄 tests/settings.test.js

  blocker (testing): Missing error path tests
  
  Tests only cover the happy path. Add tests for:
    - Unauthenticated request → 401
    - Invalid input → 400
    - Non-existent user → 404
    - Database error → 500

  ───

  suggestion: Add test for concurrent updates
  Settings updates from multiple sessions should be handled
  correctly (last-write-wins or conflict resolution).

──────────────────────────────────────

VERDICT: ⚠️ REQUEST CHANGES
  🔴 2 blocking issues must be resolved
  🟡 2 suggestions for improvement
  🟢 1 nitpick, 1 praise
```

### Example 2: Dependency Update Review

**User prompt:**
> "Review this PR that bumps React from 18 to 19"

**Expected behavior:**

```
DEPENDENCY UPDATE REVIEW: React 18 → 19
════════════════════════════════════════

DEPENDENCY AUDIT:
  Package: react (+ react-dom)
  Current: 18.2.0
  Target: 19.0.0
  Type: Major version bump ⚠️

  [✓] License: MIT (unchanged)
  [✓] No known CVEs in v19.0.0
  [✓] Actively maintained (Meta)
  [⚠️] Major version — breaking changes likely

BREAKING CHANGES TO ADDRESS:
  1. Legacy context API removed — search for contextType usage
  2. String refs removed — ensure all refs use createRef/useRef
  3. defaultProps on function components deprecated
  4. New JSX transform required

CHECKLIST:
  □ All breaking changes addressed in code
  □ react-dom/client migration complete
  □ Third-party component library compatibility verified
  □ Bundle size impact measured
  □ All existing tests passing
  □ Visual regression tests run
  □ Performance benchmarks compared

VERDICT: ⚠️ NEEDS VERIFICATION
  Ensure all breaking changes are addressed and full test
  suite passes before merging.
```

### Example 3: Bugfix PR Review

**User prompt:**
> "Review this one-line bugfix for the login timeout issue"

**Expected behavior:**

```
BUGFIX REVIEW: Login Timeout Fix
════════════════════════════════

PR Type: Bugfix
Change: 1 file, 1 line modified

📄 src/auth/session.js — Line 47

  - const SESSION_TIMEOUT = 30;        // 30 seconds
  + const SESSION_TIMEOUT = 30 * 60;   // 30 minutes

ANALYSIS:
  praise: Good catch — the timeout was set to 30 seconds
  instead of 30 minutes, causing premature session expiry.

  suggestion (non-blocking): Consider using a named constant
  or configuration value:
    const MINUTES = 60;
    const SESSION_TIMEOUT = 30 * MINUTES;
  
  Or better, move to config:
    const SESSION_TIMEOUT = config.session.timeoutSeconds;

  question: Is there a regression test to verify sessions
  persist for the expected duration? If not, consider adding:
    test('session should not expire within 29 minutes', ...)

VERDICT: ✅ APPROVE
  Fix is correct. Regression test recommended but non-blocking.
```
