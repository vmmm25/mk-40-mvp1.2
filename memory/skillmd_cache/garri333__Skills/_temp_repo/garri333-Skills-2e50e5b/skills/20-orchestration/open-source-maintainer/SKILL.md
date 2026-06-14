---
name: open-source-maintainer
version: 1.0.0
description: >
  End-to-end GitHub repository maintenance. Covers issue triage (labeling, assignment,
  prioritization), PR review and merge workflows, release management (semver, changelogs,
  package publishing), community communication, contributing guide maintenance, CI/CD pipeline
  maintenance, dependency updates (Dependabot/Renovate), and security advisory management.
tags:
  - open-source
  - github
  - issue-triage
  - pull-request
  - release-management
  - semver
  - changelog
  - community
  - ci-cd
  - dependabot
  - renovate
  - security-advisory
  - maintainer
author: garri333
license: MIT
source: n-skills
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# open-source-maintainer

End-to-end GitHub repository maintenance. Triage issues, review PRs, manage releases, communicate with contributors, maintain CI/CD, handle dependency updates, and respond to security advisories.

---

## When to Activate

Activate this skill when the user:

- Needs to **triage GitHub issues** (label, assign, prioritize)
- Wants to **review and merge pull requests** effectively
- Needs to **create a release** (version, changelog, publish)
- Asks about **community management** for an open-source project
- Wants to set up or maintain a **CONTRIBUTING.md** guide
- Needs to maintain **CI/CD pipelines** (GitHub Actions, GitLab CI)
- Wants to configure **Dependabot** or **Renovate** for dependency updates
- Has a **security advisory** or vulnerability to handle
- Wants to improve their **open-source maintenance workflow**
- Uses keywords: `issue triage`, `PR review`, `release`, `changelog`, `open source`, `maintainer`, `contributing`, `dependabot`

---

## Step-by-Step Instructions

### 1. Issue Triage

```
ISSUE TRIAGE WORKFLOW
══════════════════════════════════════════════════════════════

  New Issue Arrives
        │
  ┌─────▼──────┐    NO     ┌─────────────┐
  │ Has enough ├───────────► Request more │
  │ info?      │           │ info, add    │
  └─────┬──────┘           │ "needs-info" │
        │ YES              └─────────────┘
  ┌─────▼──────┐    YES    ┌─────────────┐
  │ Duplicate? ├───────────► Close, link  │
  │            │           │ to original  │
  └─────┬──────┘           └─────────────┘
        │ NO
  ┌─────▼──────┐
  │ Classify:  │
  │ • Type     │  bug / feature / question / docs
  │ • Priority │  P0-P3
  │ • Area     │  frontend / backend / infra / docs
  │ • Size     │  XS / S / M / L / XL
  └─────┬──────┘
        │
  ┌─────▼──────┐
  │ Assign:    │
  │ • Owner    │  maintainer / contributor / unassigned
  │ • Milestone│  v1.5.0 / backlog
  └────────────┘
```

**Label taxonomy:**

```yaml
# .github/labels.yml — standardized issue labels
labels:
  # Type
  - name: "bug"
    color: "#d73a4a"
    description: "Something isn't working"
  - name: "feature"
    color: "#a2eeef"
    description: "New feature or request"
  - name: "question"
    color: "#d876e3"
    description: "Further information is requested"
  - name: "documentation"
    color: "#0075ca"
    description: "Improvements or additions to documentation"

  # Priority
  - name: "P0-critical"
    color: "#b60205"
    description: "Critical: production down, security issue"
  - name: "P1-high"
    color: "#d93f0b"
    description: "High: major functionality broken"
  - name: "P2-medium"
    color: "#fbca04"
    description: "Medium: important but not urgent"
  - name: "P3-low"
    color: "#0e8a16"
    description: "Low: nice to have, minor improvement"

  # Area
  - name: "area/frontend"
    color: "#c5def5"
  - name: "area/backend"
    color: "#bfdadc"
  - name: "area/devops"
    color: "#fef2c0"

  # Size (effort estimation)
  - name: "size/XS"
    color: "#ededed"
    description: "< 1 hour"
  - name: "size/S"
    color: "#d4c5f9"
    description: "1-4 hours"
  - name: "size/M"
    color: "#bfd4f2"
    description: "4-8 hours"
  - name: "size/L"
    color: "#c2e0c6"
    description: "1-3 days"
  - name: "size/XL"
    color: "#f9d0c4"
    description: "3+ days — consider breaking down"

  # Status
  - name: "needs-info"
    color: "#e4e669"
    description: "Waiting for reporter to provide more details"
  - name: "good first issue"
    color: "#7057ff"
    description: "Good for newcomers"
  - name: "help wanted"
    color: "#008672"
    description: "Extra attention is needed"
  - name: "wontfix"
    color: "#ffffff"
    description: "This will not be worked on"
```

**Issue response templates:**

```markdown
<!-- Bug report response -->
Thanks for reporting this! I can reproduce the issue.

**Priority:** P2-medium
**Milestone:** v1.5.0
**Assigned to:** @maintainer

I'll look into this. In the meantime, here's a workaround:
[describe workaround]

---

<!-- Needs more info -->
Thanks for filing this. To help me investigate, could you provide:
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior
- [ ] Environment (OS, Node/Python version, browser)
- [ ] Error messages or logs (if any)

I'll add the `needs-info` label until we get these details.

---

<!-- Duplicate -->
This is a duplicate of #123. Closing this issue — please follow #123 for updates.
If your situation is different, please reopen and explain the difference.
```

---

### 2. PR Review & Merge Workflow

```
PR REVIEW WORKFLOW
══════════════════════════════════════════════════════════════

  PR Opened
      │
  ┌───▼────┐
  │ Auto   │  CI runs: lint, test, build, security scan
  │ Checks │  If any fail → author must fix before review
  └───┬────┘
      │ All pass
  ┌───▼──────────┐
  │ Review       │
  │ Checklist:   │
  │ □ Correct?   │  Does it do what it claims?
  │ □ Tests?     │  Are there tests for new/changed behavior?
  │ □ Clean?     │  Code quality, no dead code, good naming
  │ □ Docs?      │  Updated README/docs if needed
  │ □ Breaking?  │  Any breaking changes documented?
  │ □ Secure?    │  No secrets, no injection, no XSS
  └───┬──────────┘
      │
  ┌───▼────────┐   Changes needed    ┌──────────────┐
  │ Decision   ├─────────────────────► Request       │
  │            │                     │ Changes       │
  └───┬────────┘                     └──────────────┘
      │ Approved
  ┌───▼────────┐
  │ Merge      │  Squash & Merge (clean history)
  │ Strategy   │  Or Merge Commit (preserve history)
  └───┬────────┘
      │
  ┌───▼────────┐
  │ Post-merge │  Delete branch, close linked issues
  └────────────┘
```

**PR review comment templates:**

```markdown
<!-- Approval -->
LGTM! 🎉 Clean implementation with good test coverage.

Minor: Consider renaming `processData` → `transformUserInput` for clarity.
Not blocking — can be done in a follow-up.

---

<!-- Request changes -->
Thanks for this PR! A few things need addressing before merge:

**Must fix:**
1. Missing error handling in `api/users.py:45` — what happens if the DB is down?
2. Test `test_create_user` doesn't cover the duplicate email case

**Suggestions (optional):**
- Could simplify the loop in `utils.py:23` using a list comprehension
- Consider adding a type hint to the return value of `get_user()`

Let me know when you've pushed updates and I'll re-review. 👍
```

---

### 3. Release Management

```
RELEASE WORKFLOW
══════════════════════════════════════════════════════════════

1. DETERMINE VERSION (Semantic Versioning)
   Analyze commits since last release:
   - feat: → MINOR bump
   - fix: → PATCH bump
   - feat!: or BREAKING CHANGE → MAJOR bump

2. GENERATE CHANGELOG
   Group commits by type: Features, Bug Fixes, Breaking Changes
   Link to PRs and issues

3. CREATE RELEASE
   - Update version in package.json / pyproject.toml
   - Create git tag: v1.5.0
   - Push tag to trigger release workflow
   - Create GitHub Release with changelog

4. PUBLISH PACKAGES
   - npm publish (JavaScript)
   - pip publish (Python → PyPI)
   - docker push (container images)
   - GitHub Packages

5. ANNOUNCE
   - GitHub Release notes
   - Discord/Slack announcement
   - Twitter/social media (major releases)
   - Blog post (major releases)
```

**GitHub Release workflow:**

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'

      - run: npm ci
      - run: npm test
      - run: npm run build

      - name: Generate changelog
        id: changelog
        run: |
          # Get commits since last tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "")
          if [ -n "$PREV_TAG" ]; then
            CHANGELOG=$(git log $PREV_TAG..HEAD --pretty=format:"- %s (%h)" --no-merges)
          else
            CHANGELOG=$(git log --pretty=format:"- %s (%h)" --no-merges)
          fi
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          echo "$CHANGELOG" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.changelog.outputs.changelog }}
          generate_release_notes: true

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Changelog format (Keep a Changelog):**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [1.5.0] — 2026-02-22

### Added
- User notification preferences API (#234)
- Bulk export for inventory reports (#241)

### Fixed
- Session timeout on mobile devices (#236)
- Currency formatting for EUR locale (#238)

### Changed
- Upgraded React from 18.2 to 18.3

### Deprecated
- `GET /api/v1/users` — use `/api/v2/users` instead

### Security
- Updated lodash to fix prototype pollution (CVE-2021-23337)

## [1.4.2] — 2026-02-15
...
```

---

### 4. Community Communication

```
COMMUNICATION TEMPLATES
══════════════════════════════════════════════════════════════

WELCOMING NEW CONTRIBUTORS:
  "Welcome to the project! 🎉 Thanks for your first contribution.
   Your PR looks great — I've left a few minor suggestions.
   Don't hesitate to ask questions, we're happy to help."

DECLINING A PR GRACEFULLY:
  "Thanks for taking the time to submit this PR. Unfortunately,
   this doesn't align with the project's direction because [reason].
   I appreciate the effort, and I encourage you to look at the
   'help wanted' issues for areas where contributions are needed."

RESPONDING TO A HEATED ISSUE:
  "I understand this is frustrating. Let's focus on finding a
   solution. Could you share [specific info]? That will help
   us address this more effectively."

ANNOUNCING A BREAKING CHANGE:
  "⚠️ Heads up: v2.0.0 will include breaking changes to the
   authentication API. A migration guide is available at [link].
   Please test against the RC (v2.0.0-rc.1) and report issues."

COMMUNITY HEALTH METRICS:
  - Mean time to first response on issues: < 48h
  - Mean time to close issues: < 2 weeks
  - PR review turnaround: < 72h
  - Contributor retention (2nd PR rate): > 30%
```

---

### 5. Contributing Guide

```markdown
<!-- CONTRIBUTING.md template -->

# Contributing to [Project Name]

Thank you for wanting to contribute! This guide will help you
get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOU/PROJECT.git`
3. Install dependencies: `npm install` (or `pip install -e ".[dev]"`)
4. Create a branch: `git checkout -b feature/my-feature`
5. Make your changes
6. Run tests: `npm test`
7. Commit with a conventional message: `feat: add user search`
8. Push and open a PR

## Development Setup

```bash
# Prerequisites
node >= 20 (or python >= 3.11)

# Install
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint
```

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `test:` — Adding or fixing tests
- `refactor:` — Code change that neither fixes nor adds
- `chore:` — Build process or tooling
- `perf:` — Performance improvement

## Pull Request Process

1. Update documentation if you change behavior
2. Add tests for new features
3. Ensure CI passes (lint, test, build)
4. Request review from a maintainer
5. Squash commits before merge

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/).
Be respectful and constructive.

## Questions?

Open a [Discussion](../../discussions) or join our [Discord](link).
```

---

### 6. CI/CD Pipeline Maintenance

```yaml
# .github/workflows/ci.yml — Production-grade CI pipeline
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v4
        if: matrix.node == 20

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript
      - uses: github/codeql-action/analyze@v3
```

**CI maintenance checklist:**

```
CI/CD MAINTENANCE CHECKLIST (Monthly)
══════════════════════════════════════════════════════════════
□ Update action versions (actions/checkout@v4, etc.)
□ Update runtime versions (Node 20 → 22, Python 3.11 → 3.12)
□ Review and update cache strategies
□ Check for deprecated features in CI provider
□ Review build times — optimize if > 15 minutes
□ Audit CI secrets — rotate if needed
□ Verify branch protection rules are current
□ Test the release workflow with a dry run
□ Review Codecov/Coveralls thresholds
□ Check for flaky tests in CI history
```

---

### 7. Dependency Updates (Dependabot / Renovate)

**Dependabot configuration:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainer-username"
    labels:
      - "dependencies"
    commit-message:
      prefix: "chore(deps):"
    groups:
      dev-dependencies:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"
      production-minor:
        dependency-type: "production"
        update-types:
          - "minor"
          - "patch"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "ci"
    commit-message:
      prefix: "ci(deps):"
```

**Renovate configuration (alternative):**

```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    "group:allNonMajor",
    ":automergeMinor",
    ":automergeDigest"
  ],
  "labels": ["dependencies"],
  "schedule": ["before 8am on Monday"],
  "prConcurrentLimit": 5,
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "labels": ["dependencies", "breaking"]
    }
  ]
}
```

**Dependency update workflow:**

```
DEPENDENCY UPDATE TRIAGE
══════════════════════════════════════════════════════════════

PATCH updates (1.2.3 → 1.2.4):
  → Auto-merge if CI passes
  → Low risk: bug fixes only

MINOR updates (1.2.3 → 1.3.0):
  → Auto-merge for dev dependencies
  → Quick review for production dependencies
  → Check changelog for breaking behavior

MAJOR updates (1.2.3 → 2.0.0):
  → Manual review required
  → Read migration guide
  → Test thoroughly
  → Plan migration as a separate PR if complex

SECURITY updates (any version):
  → Priority: same day
  → Auto-merge patches if CI passes
  → Manual review + expedited merge for major
```

---

### 8. Security Advisory Management

```
SECURITY ADVISORY WORKFLOW
══════════════════════════════════════════════════════════════

1. RECEIVE REPORT
   Via: GitHub Security Advisories, email, private report
   DO NOT: Discuss publicly until fixed

2. ASSESS SEVERITY (CVSS)
   Critical (9.0-10.0): Remote code execution, data breach
   High (7.0-8.9):      Privilege escalation, data exposure
   Medium (4.0-6.9):    Information disclosure, DoS
   Low (0.1-3.9):       Minor information leak

3. DEVELOP FIX
   Work in a PRIVATE fork or security advisory draft
   Don't commit to public branches until ready

4. PREPARE DISCLOSURE
   - CVE ID (request from GitHub or MITRE)
   - Affected versions
   - Patched version
   - Workaround (if any)
   - Credit to reporter

5. RELEASE & DISCLOSE
   - Publish patched version
   - Create GitHub Security Advisory
   - Notify users (email list, social, release notes)
   - Update SECURITY.md

6. POST-MORTEM
   - How did this happen?
   - How can we prevent similar issues?
   - Are there similar patterns elsewhere in the code?
```

**SECURITY.md template:**

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | ✅ Yes             |
| 1.x     | ⚠️ Security only   |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report via one of these channels:
1. [GitHub Security Advisory](../../security/advisories/new) (preferred)
2. Email: security@project.example.com

You will receive an acknowledgment within 48 hours and a
detailed response within 5 business days.

## Disclosure Policy

We follow responsible disclosure:
- Reporter notifies us privately
- We develop and test a fix
- We release the fix and publish an advisory
- Reporter may publish details 30 days after the fix release
```

---

## Maintenance Schedule

```
OPEN SOURCE MAINTENANCE CADENCE
══════════════════════════════════════════════════════════════

DAILY (15 min):
  □ Triage new issues (label, prioritize)
  □ Respond to urgent bug reports
  □ Review and merge ready PRs

WEEKLY (1 hour):
  □ Review Dependabot/Renovate PRs
  □ Check CI pipeline health
  □ Respond to community discussions
  □ Update project board / milestones

MONTHLY (2-3 hours):
  □ Minor release (if changes accumulated)
  □ Review and update CI dependencies
  □ Check security advisories
  □ Recognize contributors
  □ Review metrics (issue response time, PR throughput)

QUARTERLY (half day):
  □ Major release planning
  □ Roadmap update
  □ CONTRIBUTING.md review
  □ Prune stale issues and PRs
  □ CI/CD pipeline optimization
  □ Documentation audit
```

---

## Best Practices

1. **Respond to issues within 48 hours** — even if just to acknowledge
2. **Label everything** — consistent labels make triage and reporting possible
3. **Be kind to contributors** — they're volunteering their time
4. **Automate what you can** — CI, labeling bots, dependency updates
5. **Use conventional commits** — enables automated changelog generation
6. **Keep the CONTRIBUTING.md current** — first thing new contributors read
7. **Don't merge without tests** — every PR should include relevant tests
8. **Handle security privately** — never discuss vulnerabilities in public issues
9. **Release regularly** — frequent small releases are safer than rare big ones
10. **Celebrate contributions** — mention contributors in release notes

---

## Related Skills

- `multi-agent-coordinator` — coordinate agents for repo maintenance tasks
- `task-decomposition` — break maintenance work into manageable tasks
- `agent-specialization` — assign maintenance tasks to specialized agents
