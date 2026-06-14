---
name: goose-release-manager
version: 1.0.0
description: >
  End-to-end release management skill. Handles semantic versioning, changelog generation from
  conventional commits, release notes drafting, package publishing (npm, PyPI, Docker Hub),
  Git tag creation, GitHub Release creation, pre-release validation, and rollback plan generation.
tags:
  - release
  - versioning
  - semver
  - changelog
  - publishing
  - npm
  - pypi
  - docker
  - git-tags
  - github-releases
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

# goose-release-manager

End-to-end release management. Orchestrates semantic versioning, changelog generation, release notes, package publishing, Git tagging, pre-release validation, and rollback planning.

---

## When to Activate

Activate this skill when the user:

- Wants to **create a new release** or **cut a release**
- Needs to determine the **next version number** (semantic versioning)
- Asks to **generate a changelog** from commit history
- Wants to **draft release notes** for stakeholders
- Needs to **publish a package** to npm, PyPI, or Docker Hub
- Asks to create a **Git tag** or **GitHub Release**
- Wants to run **pre-release validation** (tests, lint, security scan)
- Needs a **rollback plan** for a release
- Asks about **migration guides** for breaking changes
- Uses release keywords: `release`, `version`, `publish`, `changelog`, `tag`, `bump`, `deploy`, `semver`

---

## Step-by-Step Instructions

### 1. Determine the Version Bump

Apply [Semantic Versioning 2.0.0](https://semver.org/):

```
SEMANTIC VERSIONING: MAJOR.MINOR.PATCH
═══════════════════════════════════════

Current version: 2.3.1

PATCH (2.3.1 → 2.3.2):
  → Bug fixes that don't change the API
  → Security patches
  → Documentation corrections
  → Performance improvements (no API change)
  Commit prefixes: fix:, perf:, docs:

MINOR (2.3.1 → 2.4.0):
  → New features that are backward compatible
  → New API endpoints or methods
  → Deprecation notices (not removals)
  → New optional parameters
  Commit prefixes: feat:

MAJOR (2.3.1 → 3.0.0):
  → Breaking changes to the public API
  → Removed endpoints or methods
  → Changed request/response formats
  → Required parameter additions
  → Minimum version bumps for dependencies
  Commit prefixes: feat!:, fix!:, or BREAKING CHANGE in footer
```

### 2. Analyze Commits Since Last Release

```
COMMIT ANALYSIS: v2.3.1...HEAD
═══════════════════════════════

Conventional Commits Found: 24

Breaking Changes (MAJOR):
  (none found)

Features (MINOR):
  feat: add user notification preferences API (#234)
  feat: implement bulk export for inventory reports (#241)
  feat: add dark mode support to dashboard (#245)

Bug Fixes (PATCH):
  fix: resolve session timeout on mobile devices (#236)
  fix: correct currency formatting for EUR locale (#238)
  fix: prevent duplicate order submissions (#242)
  fix: handle null values in search results (#247)

Other:
  perf: optimize database queries for inventory list (#237)
  docs: update API documentation for v2 endpoints (#239)
  refactor: extract notification service (#240)
  chore: update CI pipeline configuration (#243)
  test: add integration tests for bulk export (#244)
  ci: add security scanning to PR checks (#246)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED VERSION: 2.4.0 (MINOR — new features, no breaking changes)
```

### 3. Generate Changelog

```markdown
# Changelog

## [2.4.0] — 2026-02-22

### ✨ Features
- **Notification preferences**: Users can now configure notification channels
  and frequency from the settings page (#234)
- **Bulk export**: Export inventory reports in CSV, Excel, and PDF formats
  with filtering options (#241)
- **Dark mode**: Dashboard now supports dark mode with automatic system
  preference detection (#245)

### 🐛 Bug Fixes
- **Session timeout**: Fixed premature session expiry on mobile devices
  caused by incorrect timeout calculation (#236)
- **Currency formatting**: Corrected EUR locale formatting to use comma
  as decimal separator (#238)
- **Duplicate orders**: Added idempotency key to prevent duplicate order
  submissions during network retries (#242)
- **Search null handling**: Search results no longer crash when fields
  contain null values (#247)

### ⚡ Performance
- Optimized inventory list queries reducing load time by 40% (#237)

### 📚 Documentation
- Updated API documentation for all v2 endpoints (#239)

### 🔧 Internal
- Extracted notification logic into a dedicated service (#240)
- Added integration tests for bulk export feature (#244)
- Added automated security scanning to PR pipeline (#246)
```

### 4. Draft Release Notes

```markdown
# Release Notes — v2.4.0

**Release Date:** February 22, 2026

## Highlights

### 🔔 Notification Preferences
Configure how and when you receive notifications. Choose from email,
in-app, and Slack channels. Set per-category frequency (immediate,
daily digest, weekly summary).

### 📊 Bulk Export
Export your inventory reports in multiple formats:
- **CSV** — For spreadsheet analysis
- **Excel** — With formatting and charts
- **PDF** — For printing and sharing

Apply date ranges, category filters, and custom columns before export.

### 🌙 Dark Mode
The dashboard now respects your system theme preference. Toggle between
light, dark, and auto modes from the settings panel.

## Bug Fixes
- Fixed session timeouts on mobile browsers
- Corrected currency display for European locales
- Prevented duplicate orders during slow network conditions
- Fixed crash when search results contain empty fields

## Upgrade Guide
This is a backward-compatible release. No action required for API consumers.

```bash
# npm
npm install @company/inventory-app@2.4.0

# Docker
docker pull company/inventory-app:2.4.0
```

## Full Changelog
See [CHANGELOG.md](./CHANGELOG.md) for the complete list of changes.
```

### 5. Pre-Release Validation

```
PRE-RELEASE VALIDATION CHECKLIST:
═════════════════════════════════

Code Quality:
  [✓] All CI checks passing on release branch
  [✓] Linting: 0 errors, 0 warnings
  [✓] Type checking: no type errors
  [✓] Code formatting: consistent

Testing:
  [✓] Unit tests: 847/847 passing (100%)
  [✓] Integration tests: 124/124 passing (100%)
  [✓] E2E tests: 38/38 passing (100%)
  [✓] Test coverage: 87.3% (threshold: 80%)
  [✓] No flaky tests detected

Security:
  [✓] Dependency audit: 0 known vulnerabilities
  [✓] Secret scanning: no secrets in code
  [✓] SAST scan: 0 critical or high findings
  [✓] License compliance: all dependencies MIT/Apache-2.0/BSD

Build:
  [✓] Production build successful
  [✓] Bundle size: 245KB gzipped (within budget)
  [✓] Docker image: 89MB (within limit)
  [✓] Build reproducible (deterministic output)

Documentation:
  [✓] CHANGELOG.md updated
  [✓] API docs updated
  [✓] Migration guide written (if breaking changes)
  [✓] README version references updated

━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALIDATION RESULT: ✅ PASS — Ready for release
```

### 6. Execute Release

#### Git Tag Creation

```bash
# Create annotated tag
git tag -a v2.4.0 -m "Release v2.4.0

Features:
- User notification preferences API
- Bulk export for inventory reports
- Dark mode support for dashboard

Bug Fixes:
- Session timeout on mobile devices
- Currency formatting for EUR locale
- Duplicate order submissions prevention
- Null value handling in search results"

# Push tag
git push origin v2.4.0
```

#### GitHub Release Creation

```
GITHUB RELEASE:
═══════════════

Tag: v2.4.0
Target: main (commit abc123f)
Title: v2.4.0 — Notification Preferences, Bulk Export, Dark Mode
Pre-release: No

Body: [Release notes from Step 4]

Assets:
  - inventory-app-2.4.0.tar.gz (source)
  - inventory-app-2.4.0-linux-amd64.tar.gz
  - inventory-app-2.4.0-darwin-arm64.tar.gz
  - inventory-app-2.4.0-windows-amd64.zip
  - checksums.sha256
```

#### Package Publishing

```
PACKAGE PUBLISHING:
═══════════════════

npm:
  [✓] npm login verified
  [✓] .npmrc configured for registry
  [✓] npm publish --tag latest
  [✓] Published: @company/inventory-app@2.4.0
  [✓] Verified: npm view @company/inventory-app version → 2.4.0

PyPI:
  [✓] twine check dist/*
  [✓] twine upload dist/*
  [✓] Published: inventory-app 2.4.0
  [✓] Verified: pip index versions inventory-app → 2.4.0

Docker Hub:
  [✓] docker build -t company/inventory-app:2.4.0 .
  [✓] docker tag company/inventory-app:2.4.0 company/inventory-app:latest
  [✓] docker push company/inventory-app:2.4.0
  [✓] docker push company/inventory-app:latest
  [✓] Verified: docker pull company/inventory-app:2.4.0 → OK

All packages published successfully ✅
```

### 7. Generate Rollback Plan

```
ROLLBACK PLAN: v2.4.0 → v2.3.1
═══════════════════════════════

Trigger Conditions:
  - Critical bug discovered in production
  - Error rate exceeds 5% threshold
  - P0/P1 incident caused by release

Rollback Steps:

  1. DECIDE to rollback
     → Incident Commander makes the call
     → Notify #releases channel

  2. REVERT application
     npm:
       npm dist-tag add @company/inventory-app@2.3.1 latest
     
     Docker:
       kubectl set image deployment/app app=company/inventory-app:2.3.1
     
     Git:
       git revert <merge-commit-hash>
       git push origin main

  3. VERIFY rollback
     → Health checks pass
     → Error rate returns to baseline
     → Smoke tests pass on production
     → Key user flows functional

  4. COMMUNICATE
     → Update status page
     → Notify stakeholders
     → Post in #releases channel

  5. INVESTIGATE
     → Create incident ticket
     → Determine root cause
     → Plan fix for v2.4.1

Estimated Rollback Time: < 10 minutes
Rollback Owner: On-call release engineer
```

### 8. Create Migration Guide (for Major Versions)

```markdown
# Migration Guide — v2.x → v3.0.0

## Breaking Changes

### 1. Authentication API Changes

**Before (v2.x):**
```json
POST /api/auth/login
{ "username": "user", "password": "pass" }
```

**After (v3.0):**
```json
POST /api/v3/auth/login
{ "email": "user@example.com", "password": "pass", "mfa_code": "123456" }
```

**Migration steps:**
1. Replace `username` field with `email`
2. Add MFA support to login flow
3. Update API base URL from `/api/` to `/api/v3/`

### 2. Response Format Changes

**Before (v2.x):**
```json
{ "data": [...], "total": 100 }
```

**After (v3.0):**
```json
{ "data": [...], "meta": { "total": 100, "page": 1, "per_page": 20 } }
```

**Migration steps:**
1. Update response parsing to access `meta.total` instead of `total`
2. Implement pagination using `meta.page` and `meta.per_page`

### 3. Deprecated Methods Removed

| Removed Method | Replacement |
|---|---|
| `getUser(id)` | `users.find(id)` |
| `listItems()` | `inventory.list({ paginate: true })` |
| `deleteItem(id)` | `inventory.remove(id)` |

## Automated Migration

Run the migration codemod:
```bash
npx @company/inventory-codemod@3.0.0
```

This will automatically:
- Update import paths
- Rename deprecated method calls
- Update response parsing patterns

## Timeline

- **v2.x maintenance**: Security patches until June 2026
- **v2.x end-of-life**: December 2026
- **v3.0 stable**: Available now
```

---

## Best Practices

1. **Follow semantic versioning strictly** — Users depend on version numbers to assess upgrade risk
2. **Use conventional commits** — They enable automated changelog generation and version bumping
3. **Validate before releasing** — Run the full test suite, security scan, and lint before tagging
4. **Never delete a published version** — If a version has a bug, publish a patch instead
5. **Tag releases in Git** — Use annotated tags with release context in the message
6. **Draft release notes for humans** — Changelogs are for developers; release notes are for everyone
7. **Publish to registries atomically** — All package registries should get the same version simultaneously
8. **Always have a rollback plan** — Document how to revert before you ship
9. **Use pre-release versions** — Test with alpha/beta/rc versions before stable release
10. **Automate everything possible** — CI/CD should handle building, testing, and publishing

---

## Examples

### Example 1: Cutting a Release

**User prompt:**
> "We're ready to release. Help me create the next version."

**Expected behavior:**

```
RELEASE PREPARATION: inventory-app
═══════════════════════════════════

Current version: 2.3.1
Analyzing commits since v2.3.1...

Commits found: 24
  Features: 3 (feat:)
  Bug fixes: 4 (fix:)
  Other: 17 (perf, docs, refactor, chore, test, ci)
  Breaking changes: 0

RECOMMENDED VERSION: 2.4.0 (MINOR)
  Reason: New features added, no breaking changes

RELEASE CHECKLIST:
  [✓] Version determined: 2.4.0
  [ ] Update version in package.json
  [ ] Generate changelog entry
  [ ] Draft release notes
  [ ] Run pre-release validation
  [ ] Create release branch (release/2.4.0)
  [ ] Create Git tag (v2.4.0)
  [ ] Create GitHub Release
  [ ] Publish to npm
  [ ] Publish Docker image
  [ ] Notify stakeholders
  [ ] Update documentation

Shall I proceed with the release? I'll start by updating
the version and generating the changelog.
```

### Example 2: Hotfix Release

**User prompt:**
> "We need to release a critical bugfix for the payment calculation error"

**Expected behavior:**

```
HOTFIX RELEASE: inventory-app
═════════════════════════════

Current version: 2.4.0
Hotfix type: PATCH (critical bugfix)
Target version: 2.4.1

HOTFIX PROCEDURE:
  1. Create hotfix branch from v2.4.0 tag
     git checkout -b hotfix/2.4.1 v2.4.0

  2. Cherry-pick the fix commit
     git cherry-pick <fix-commit-hash>

  3. Update version to 2.4.1
     npm version patch

  4. Fast-track validation:
     [✓] Fix verified in isolation
     [✓] Unit tests passing
     [✓] Integration tests passing
     [✓] No other changes included
     [✓] Security scan clean

  5. Tag and release
     git tag -a v2.4.1 -m "Hotfix: correct payment calculation"
     git push origin v2.4.1

  6. Publish
     npm publish
     docker push company/inventory-app:2.4.1

  7. Merge hotfix back to main
     git checkout main
     git merge hotfix/2.4.1

CHANGELOG ENTRY:
  ## [2.4.1] — 2026-02-22
  ### 🐛 Bug Fixes
  - **Payment calculation**: Fixed rounding error in tax
    calculation that could result in incorrect totals (#250)

⚠️ ROLLBACK PLAN:
  If v2.4.1 introduces issues, rollback to v2.4.0:
    npm dist-tag add @company/inventory-app@2.4.0 latest
    kubectl set image deployment/app app=company/inventory-app:2.4.0
```

### Example 3: Pre-release Version

**User prompt:**
> "Create a beta release of v3.0.0 for testing"

**Expected behavior:**

```
PRE-RELEASE: v3.0.0-beta.1
═══════════════════════════

Version: 3.0.0-beta.1
Channel: beta (pre-release)
Stability: NOT PRODUCTION READY

Pre-release validation:
  [✓] Unit tests: 892/892 passing
  [✓] Integration tests: 130/130 passing
  [⚠️] E2E tests: 36/38 passing (2 known issues tracked)
  [✓] Security scan: clean
  [✓] Breaking changes documented in migration guide

Publishing:
  npm publish --tag beta
  docker push company/inventory-app:3.0.0-beta.1

Install (for testers):
  npm install @company/inventory-app@beta
  docker pull company/inventory-app:3.0.0-beta.1

⚠️ This will NOT affect the 'latest' tag.
   Production users on v2.4.x are unaffected.

Beta feedback channel: #v3-beta-testing
Known issues: https://github.com/company/app/milestone/5
```
