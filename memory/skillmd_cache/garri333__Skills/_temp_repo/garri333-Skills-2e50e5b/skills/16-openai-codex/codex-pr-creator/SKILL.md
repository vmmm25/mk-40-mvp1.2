---
name: codex-pr-creator
version: 1.0.0
description: Automated Pull Request creation with CI validation, intelligent type/scope detection from git changes, Conventional Commits format, automated PR title generation compatible with check-pr-title CI rules, and Linear/GitHub Issues ticket linking. Inspired by n8n PR Creator (170,914 stars on MCP Market).
tags: [openai, codex, pull-request, ci, conventional-commits, git, automation, pr-title, changelog, linear, github-issues]
author: garri333
license: MIT
source: openai/skills
---

# Codex PR Creator Skill

## Overview

Use this skill whenever the user needs to create Pull Requests with proper conventional commit formatting, automated type/scope detection, CI-compatible titles, and issue tracker linking. This skill automates the entire PR lifecycle — from analyzing git changes to generating titles that pass `check-pr-title` CI rules.

Inspired by the **n8n PR Creator** (170,914 stars on MCP Market), this skill brings intelligent PR automation to the Codex ecosystem.

---

## When to Activate

- User asks to create a Pull Request or merge request.
- User needs to generate a PR title from git changes.
- User mentions conventional commits or commit message formatting.
- User wants to link a PR to a Linear or GitHub Issue.
- User asks about `check-pr-title` CI validation.
- User needs to handle breaking changes in a PR.
- User wants to exclude changes from the changelog.
- User asks about PR automation or CI compatibility.

---

## Conventional Commits Format

### PR Title Structure

```
<type>(<scope>): <description>
```

### Supported Types

| Type | Description | Changelog Section |
|------|-------------|-------------------|
| `feat` | New feature | ✨ Features |
| `fix` | Bug fix | 🐛 Bug Fixes |
| `docs` | Documentation only | 📚 Documentation |
| `style` | Formatting, semicolons, etc. | 💄 Styles |
| `refactor` | Code change (no feature/fix) | ♻️ Code Refactoring |
| `perf` | Performance improvement | ⚡ Performance |
| `test` | Adding/correcting tests | ✅ Tests |
| `build` | Build system or dependencies | 🔧 Build System |
| `ci` | CI configuration changes | 👷 CI |
| `chore` | Maintenance tasks | 🔨 Chores |
| `revert` | Reverting a previous commit | ⏪ Reverts |

### Scope Examples

| Scope | When to Use |
|-------|-------------|
| `core` | Core library changes |
| `api` | API endpoint changes |
| `ui` | Frontend/UI changes |
| `auth` | Authentication/authorization |
| `db` | Database schema/queries |
| `deps` | Dependency updates |
| `config` | Configuration changes |
| `editor` | Editor/IDE integration |

---

## Step-by-Step Procedures

### 1. Automatic PR Creation from Git Changes

```bash
# Analyze current git changes and create a PR automatically
codex pr create

# Flow:
# 1. Codex analyzes `git diff` and `git log` against the base branch
# 2. Detects the type (feat, fix, refactor, etc.)
# 3. Identifies the scope from changed files/directories
# 4. Generates a conventional commits title
# 5. Creates a PR description with summary, changes, and testing notes
# 6. Validates against check-pr-title rules
# 7. Opens the PR on GitHub/GitLab

# Example output:
# Analyzing changes: 5 files changed, 142 insertions, 23 deletions
# Detected type: feat (new functionality in src/api/payments.ts)
# Detected scope: api (changes in src/api/)
# Generated title: feat(api): add Stripe payment processing endpoint
# ✓ Title passes check-pr-title validation
# Creating PR... ✓ PR #247 created: https://github.com/org/repo/pull/247
```

### 2. Intelligent Type and Scope Detection

```bash
# Codex analyzes git changes to determine type and scope:

# Type detection rules:
# - New files added → feat
# - Test files added/modified → test
# - Bug-related keywords in diff → fix
# - Documentation files changed → docs
# - CI config files changed → ci
# - Only formatting changes → style
# - Performance-related changes → perf
# - package.json/lockfile changes → build or deps

# Scope detection rules:
# - Changes in src/api/ → scope: api
# - Changes in src/components/ → scope: ui
# - Changes in src/auth/ → scope: auth
# - Changes across multiple directories → scope: omitted or "core"
# - Changes in tests/ only → scope: derived from test file names

# Override detected type/scope
codex pr create --type fix --scope auth

# Preview detection without creating PR
codex pr create --dry-run

# Output:
# Analysis:
#   Changed files: src/api/routes.ts, src/api/middleware.ts, tests/api.test.ts
#   Detected type: refactor
#   Detected scope: api
#   Suggested title: refactor(api): restructure route handlers with middleware pattern
#   Breaking changes: No
#   Linked issues: None detected
#
# Run without --dry-run to create the PR.
```

### 3. PR Title Generation and CI Validation

```bash
# Generate a title that passes check-pr-title CI rules
codex pr title

# Output: feat(api): add payment processing with Stripe webhook support

# Validate an existing title against CI rules
codex pr validate-title "feat(api): add payments"
# ✓ Valid conventional commit format
# ✓ Type 'feat' is allowed
# ✓ Scope 'api' is recognized
# ✓ Description is descriptive (not too short/generic)
# ✓ Compatible with check-pr-title v3.x rules

# Fix an invalid title
codex pr validate-title "updated stuff"
# ✗ Missing type prefix
# ✗ No scope defined
# ✗ Description too vague
# Suggested fix: feat(core): update configuration handling for new deployment targets

# check-pr-title CI compatibility rules:
# 1. Must start with a valid type (feat, fix, docs, etc.)
# 2. Scope is optional but recommended
# 3. Colon + space after type/scope
# 4. Description must be lowercase (no capital first letter)
# 5. No period at the end
# 6. Max 72 characters total
# 7. Breaking changes indicated with ! before colon
```

**check-pr-title CI configuration (.github/pr-title.yml):**

```yaml
# Recognized by Codex PR Creator for validation
types:
  - feat
  - fix
  - docs
  - style
  - refactor
  - perf
  - test
  - build
  - ci
  - chore
  - revert
scopes:
  required: false
  allowed:
    - core
    - api
    - ui
    - auth
    - db
    - deps
    - config
    - editor
rules:
  max_length: 72
  lowercase_description: true
  no_trailing_period: true
  require_scope_for_types:
    - feat
    - fix
```

### 4. Issue Linking — Linear and GitHub Issues

```bash
# Auto-detect linked issues from branch name
# Branch name format: feature/PROJ-123-add-payments
codex pr create
# → Automatically detects PROJ-123 and links to Linear

# Explicit issue linking
codex pr create --issue PROJ-123
codex pr create --issue "#456"           # GitHub Issue
codex pr create --issue "PROJ-123,PROJ-124"  # Multiple issues

# Linear integration
codex pr create --linear PROJ-123

# GitHub Issues integration
codex pr create --closes 456
codex pr create --fixes 456
codex pr create --relates-to 456

# Generated PR description with issue links:
# ## Related Issues
# - Closes PROJ-123 (Linear)
# - Fixes #456 (GitHub)
# - Related to #789
```

**Branch name patterns for auto-detection:**

| Pattern | Detected Issue |
|---------|---------------|
| `feature/PROJ-123-description` | Linear: PROJ-123 |
| `fix/GH-456-bug-description` | GitHub: #456 |
| `123-short-description` | GitHub: #123 |
| `feat/TEAM-99-add-feature` | Linear: TEAM-99 |

### 5. Breaking Changes

```bash
# Mark a PR as containing breaking changes
codex pr create --breaking

# Generated title with breaking change indicator:
# feat(api)!: redesign authentication flow with OAuth2

# Breaking change footer in PR description:
# ## ⚠️ Breaking Changes
# - `POST /auth/login` now requires `client_id` parameter
# - Removed deprecated `GET /auth/session` endpoint
# - Token format changed from JWT HS256 to RS256
#
# ### Migration Guide
# 1. Update all API clients to include `client_id` in login requests
# 2. Replace `/auth/session` calls with `/auth/me`
# 3. Update token validation to use RS256 public key

# Auto-detect breaking changes from git diff
codex pr create --detect-breaking
# Codex scans for:
# - Removed public API functions/endpoints
# - Changed function signatures
# - Renamed exports
# - Schema migrations with destructive changes
# - Major dependency version bumps
```

### 6. Changelog Integration

```bash
# Create PR with automatic changelog entry
codex pr create --changelog

# Exclude from changelog (for internal/infra changes)
codex pr create --no-changelog

# Changelog exclusion tags in PR description:
# <!-- changelog:exclude -->
# or
# [skip changelog]

# Generate a changelog entry without creating PR
codex pr changelog-entry

# Output:
# ### ✨ Features
# - **api**: Add Stripe payment processing endpoint ([#247](url))
#
# Add to CHANGELOG.md? [Y/n]
```

### 7. PR Description Generation

```bash
# Generate a comprehensive PR description
codex pr create --description detailed

# Generated description template:
```

**Generated PR description example:**

```markdown
## Summary

Add Stripe payment processing endpoint with webhook support for handling
subscription lifecycle events.

## Type of Change

- [x] ✨ New feature (non-breaking change adding functionality)
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] 💥 Breaking change (fix or feature causing existing functionality to break)
- [ ] 📚 Documentation update

## Changes

- Added `POST /api/payments/checkout` endpoint for creating Stripe sessions
- Added `POST /api/payments/webhook` for processing Stripe events
- Added `PaymentService` class with subscription management logic
- Added database migration for `payments` and `subscriptions` tables
- Added unit tests for payment processing flows

## Testing

- [x] Unit tests pass (`yarn test`)
- [x] Integration tests pass (`yarn test:integration`)
- [x] Manual testing completed
- [x] No regressions in existing functionality

## Related Issues

- Closes PROJ-123
- Fixes #456

## Screenshots / Evidence

_N/A — Backend-only changes_

## Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Documentation updated
- [x] Tests added for new functionality
- [x] No new warnings introduced
```

### 8. Compatibility Markers

```bash
# Add compatibility information to PR
codex pr create --compat

# Compatibility markers in PR description:
# ## Compatibility
# - **Node.js**: ≥18.0.0 ✓
# - **Database**: PostgreSQL 15+ ✓ (migration included)
# - **API**: Backward compatible ✓
# - **SDK**: v2.x compatible ✓
# - **Browser**: N/A (backend only)

# Specify compatibility requirements explicitly
codex pr create --requires "node>=18" --requires "postgres>=15"

# Mark as requiring specific review
codex pr create --requires-review security
codex pr create --requires-review database
```

---

## Best Practices

1. **Always use `--dry-run` first** — review the detected type, scope, and title before creating the PR.
2. **Let Codex detect the type** — manual override should be rare; the auto-detection is trained on conventional commits.
3. **Name branches with issue IDs** — `feature/PROJ-123-description` enables automatic issue linking.
4. **Use breaking change markers** — always flag breaking changes with `!` to prevent surprise failures for consumers.
5. **Keep PR titles under 72 characters** — required by most `check-pr-title` CI configurations.
6. **Include changelog tags** — use `--no-changelog` for infra changes to keep the changelog meaningful.
7. **Link issues explicitly** — even if branch-name detection works, explicit `--issue` is more reliable.
8. **Validate before push** — run `codex pr validate-title` locally to catch CI failures before they happen.
9. **Use detailed descriptions** — `--description detailed` creates thorough descriptions that speed up code reviews.
10. **Configure `.github/pr-title.yml`** — standardize your team's title rules so Codex can validate against them.

---

## Examples

### Example 1: Simple Feature PR

```bash
# On branch: feature/PROJ-42-user-avatars
codex pr create

# Output:
# ✓ Detected type: feat
# ✓ Detected scope: ui
# ✓ Linked issue: PROJ-42 (Linear)
# ✓ Title: feat(ui): add user avatar upload and display
# ✓ PR #301 created
```

### Example 2: Breaking Change with Migration Guide

```bash
codex pr create --breaking --description detailed --changelog

# Generated title: feat(api)!: migrate authentication to OAuth2 PKCE flow
# Generated PR with:
#   - Breaking change section
#   - Migration guide
#   - Changelog entry
#   - Compatibility markers
```

### Example 3: Dependency Update PR

```bash
# After running npm update or renovate
codex pr create --type build --scope deps

# Title: build(deps): update dependencies including react 19.1 and next 15.2
# Description includes:
#   - List of updated packages with version changes
#   - Breaking change analysis for major updates
#   - Auto-detected compatibility notes
```

### Example 4: CI Pipeline Integration

```yaml
# .github/workflows/pr-title-check.yml
name: PR Title Check
on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  check-title:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @openai/codex
      - name: Validate PR Title
        run: |
          codex pr validate-title "${{ github.event.pull_request.title }}"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Example 5: Batch PR Creation (Monorepo)

```bash
# Create separate PRs for each package in a monorepo
codex pr create --monorepo --split-by-package

# Output:
# Package: @myorg/api — feat(api): add rate limiting middleware → PR #302
# Package: @myorg/ui — fix(ui): correct date picker timezone handling → PR #303
# Package: @myorg/shared — refactor(shared): extract validation utils → PR #304
```
