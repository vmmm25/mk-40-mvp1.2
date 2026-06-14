---
name: codex-multi-agent
version: 1.0.0
description: Multi-agent architecture skill for the Codex Desktop App. Orchestrate specialized agents for parallel test writing, legacy refactoring, documentation generation, and more. Covers coordinator patterns, inter-agent communication, conflict resolution, and result consolidation.
tags: [openai, codex, multi-agent, orchestration, parallel, desktop-app, agents, refactoring, testing, documentation]
author: garri333
license: MIT
source: openai/skills
---

# Codex Multi-Agent Skill

## Overview

Use this skill whenever the user needs to orchestrate multiple specialized Codex agents working in parallel — assigning one agent to write tests, another to refactor legacy code, a third to generate documentation, and coordinating their outputs. Built on the Codex Desktop App architecture launched **February 2, 2026**.

The multi-agent system uses a **coordinator + specialized agents** pattern where a central coordinator agent manages task decomposition, agent assignment, parallel execution, inter-agent communication, and result consolidation.

---

## When to Activate

- User asks to run multiple coding tasks simultaneously.
- User wants to assign different agents to different aspects of a codebase.
- User mentions the Codex Desktop App multi-agent features.
- User needs to refactor, test, and document code in parallel.
- User asks about agent orchestration or coordination patterns.
- User wants to resolve conflicts between changes made by multiple agents.
- User needs to consolidate results from parallel agent executions.
- User asks about inter-agent communication or shared context.

---

## Architecture

### Coordinator + Specialized Agents Model

```
┌──────────────────────────────────────────────────────┐
│                 COORDINATOR AGENT                     │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────┐ │
│  │ Task         │ │ Dependency   │ │ Conflict      │ │
│  │ Decomposer   │ │ Resolver     │ │ Arbiter       │ │
│  └─────────────┘ └──────────────┘ └───────────────┘ │
│                        │                              │
│         ┌──────────────┼──────────────┐              │
│         ▼              ▼              ▼              │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────┐ │
│  │ Test Writer  │ │ Refactorer   │ │ Documenter    │ │
│  │ Agent        │ │ Agent        │ │ Agent         │ │
│  └─────────────┘ └──────────────┘ └───────────────┘ │
│         │              │              │              │
│         └──────────────┼──────────────┘              │
│                        ▼                              │
│              ┌─────────────────┐                     │
│              │ Result Merger   │                     │
│              │ & Validator     │                     │
│              └─────────────────┘                     │
└──────────────────────────────────────────────────────┘
```

**Components:**
- **Coordinator Agent**: Decomposes user requests, assigns tasks, manages execution order, resolves conflicts.
- **Specialized Agents**: Execute domain-specific tasks (testing, refactoring, documentation, security audit, etc.).
- **Result Merger**: Consolidates outputs, detects merge conflicts, validates combined result.

---

## Step-by-Step Procedures

### 1. Launching the Codex Desktop App

```bash
# Install Codex Desktop App (macOS)
brew install --cask openai-codex

# Install Codex Desktop App (Windows — winget)
winget install OpenAI.CodexDesktop

# Install Codex Desktop App (Linux — AppImage)
wget https://releases.openai.com/codex-desktop/latest/codex-desktop.AppImage
chmod +x codex-desktop.AppImage
./codex-desktop.AppImage

# Launch from CLI
codex-desktop

# Launch and open a project
codex-desktop --project /path/to/my-project
```

### 2. Configuring Multi-Agent Mode

```json
// ~/.codex-desktop/agents.json
{
  "coordinator": {
    "model": "gpt-5.2-thinking",
    "max_agents": 6,
    "conflict_strategy": "coordinator-decides",
    "timeout_per_agent": 300000
  },
  "agent_profiles": {
    "test-writer": {
      "model": "gpt-5.2-instant",
      "specialization": "unit and integration test generation",
      "file_patterns": ["**/*.test.*", "**/*.spec.*", "**/tests/**"],
      "tools": ["jest", "pytest", "vitest", "playwright"]
    },
    "refactorer": {
      "model": "gpt-5.2-thinking",
      "specialization": "legacy code modernization and refactoring",
      "file_patterns": ["src/**/*"],
      "tools": ["eslint", "prettier", "ruff", "black"]
    },
    "documenter": {
      "model": "gpt-5.2-instant",
      "specialization": "documentation, JSDoc, docstrings, README generation",
      "file_patterns": ["**/*.md", "docs/**"],
      "tools": ["typedoc", "sphinx", "mkdocs"]
    }
  }
}
```

### 3. Running a Multi-Agent Task

#### Via Desktop App UI

1. Open the Codex Desktop App and load your project.
2. Click **"Multi-Agent"** in the top toolbar.
3. Describe your overall goal in the prompt field.
4. The coordinator will propose a task decomposition — review and approve.
5. Agents execute in parallel — monitor progress in the agent panel.
6. Review consolidated results, resolve any flagged conflicts.
7. Apply changes or iterate.

#### Via CLI

```bash
# Launch multi-agent task from CLI
codex multi-agent "modernize this legacy Express.js app: \
  write comprehensive tests, refactor to TypeScript with modern patterns, \
  and generate API documentation"

# Specify agents explicitly
codex multi-agent \
  --agent test-writer:"write unit tests for all route handlers" \
  --agent refactorer:"convert from JavaScript to TypeScript, use async/await" \
  --agent documenter:"generate OpenAPI spec and README"

# Limit concurrency
codex multi-agent "improve code quality" --max-agents 3

# Dry run — see the plan without executing
codex multi-agent "refactor and test the auth module" --dry-run

# Use a specific coordination strategy
codex multi-agent "upgrade project" --strategy sequential
```

### 4. Task Orchestration

The coordinator agent handles task decomposition automatically:

```bash
# Example: User provides a high-level goal
codex multi-agent "prepare this codebase for production release"

# Coordinator decomposes into:
# ┌──────────────────────────────────────────────┐
# │ Task 1 (test-writer): Generate missing tests │ ← parallel
# │ Task 2 (refactorer): Fix linting issues       │ ← parallel
# │ Task 3 (documenter): Update README + CHANGELOG│ ← parallel
# │ Task 4 (security): Run security audit         │ ← after 1-3
# │ Task 5 (coordinator): Consolidate & validate  │ ← final
# └──────────────────────────────────────────────┘
```

**Dependency-aware scheduling:**

```json
{
  "tasks": [
    {
      "id": "t1",
      "agent": "refactorer",
      "description": "Refactor auth module to use bcrypt",
      "depends_on": []
    },
    {
      "id": "t2",
      "agent": "test-writer",
      "description": "Write tests for refactored auth module",
      "depends_on": ["t1"]
    },
    {
      "id": "t3",
      "agent": "documenter",
      "description": "Document the auth API endpoints",
      "depends_on": ["t1"]
    }
  ]
}
```

### 5. Parallel Agent Execution

```bash
# Monitor all running agents
codex multi-agent status

# Output:
# ┌────────────────┬──────────┬──────────┬─────────────────────────┐
# │ Agent          │ Status   │ Progress │ Current File            │
# ├────────────────┼──────────┼──────────┼─────────────────────────┤
# │ test-writer    │ Running  │ 67%      │ src/auth/login.test.ts  │
# │ refactorer     │ Running  │ 45%      │ src/api/routes.ts       │
# │ documenter     │ Complete │ 100%     │ —                       │
# └────────────────┴──────────┴──────────┴─────────────────────────┘

# Pause a specific agent
codex multi-agent pause test-writer

# Resume a paused agent
codex multi-agent resume test-writer

# Cancel all agents
codex multi-agent cancel --all

# View agent logs
codex multi-agent logs refactorer --tail 50
```

### 6. Inter-Agent Communication

Agents can share context and signals through the coordinator's message bus:

```json
// Example: Agent communication messages
{
  "from": "refactorer",
  "to": "test-writer",
  "type": "file_changed",
  "payload": {
    "file": "src/auth/service.ts",
    "changes": "Renamed AuthService.validate() to AuthService.verifyCredentials()",
    "impact": "Tests referencing validate() need updating"
  }
}
```

**Shared context mechanisms:**
- **File change notifications**: Agents are notified when another agent modifies a file they depend on.
- **Symbol rename propagation**: If one agent renames a function, others are informed automatically.
- **Dependency graph updates**: The coordinator maintains a live dependency graph across all agents.
- **Priority signals**: An agent can signal the coordinator to prioritize dependent tasks.

```bash
# Enable verbose inter-agent communication logging
codex multi-agent "upgrade project" --verbose-comms

# View the shared context state
codex multi-agent context --show
```

### 7. Result Consolidation

```bash
# After all agents complete, review consolidated results
codex multi-agent results

# View a unified diff of all changes
codex multi-agent results --diff

# View changes by agent
codex multi-agent results --by-agent

# Apply all changes
codex multi-agent results --apply

# Apply selectively (interactive)
codex multi-agent results --apply --interactive

# Export results for code review
codex multi-agent results --export pr-ready
```

### 8. Conflict Resolution

When multiple agents modify the same file or related code:

```bash
# View detected conflicts
codex multi-agent conflicts

# Output:
# ⚠ Conflict in src/auth/service.ts:
#   - refactorer: Renamed method validate() → verifyCredentials()
#   - test-writer: Added tests calling validate()
#   Resolution: coordinator-decides (auto-resolve)

# Resolution strategies:
# 1. coordinator-decides — Coordinator agent resolves automatically (default)
# 2. last-writer-wins — Last agent's changes take priority
# 3. manual — Prompt user to resolve
# 4. merge-all — Attempt three-way merge

# Set conflict strategy
codex multi-agent "upgrade project" --conflict-strategy manual

# Manually resolve a specific conflict
codex multi-agent resolve src/auth/service.ts --prefer refactorer
```

**Automatic conflict resolution logic:**
1. If changes are in different sections of the file → auto-merge.
2. If one agent renames and another references the old name → propagate rename.
3. If both agents modify the same lines → escalate to strategy (coordinator/manual).
4. If structural conflicts (e.g., different architectures) → always escalate to user.

---

## Agent Specializations

### Built-in Agent Types

| Agent | Purpose | Best For |
|-------|---------|----------|
| `test-writer` | Generate unit, integration, e2e tests | Coverage gaps, TDD |
| `refactorer` | Modernize, optimize, restructure code | Legacy codebases, tech debt |
| `documenter` | Generate docs, comments, READMEs | API documentation, onboarding |
| `security-auditor` | Find vulnerabilities, suggest fixes | Pre-release audits |
| `performance-optimizer` | Profile and optimize hot paths | Latency-sensitive services |
| `accessibility-checker` | Audit UI for a11y compliance | WCAG compliance |
| `migrator` | Framework/language migration | Version upgrades, rewrites |

### Custom Agent Definitions

```json
// .codex/custom-agents.json
{
  "i18n-agent": {
    "model": "gpt-5.2-instant",
    "specialization": "Internationalization and localization",
    "instructions": "Extract all hardcoded strings, create translation keys, generate locale files for en, es, ca, fr",
    "file_patterns": ["src/**/*.tsx", "src/**/*.ts"],
    "output_patterns": ["locales/**/*.json"]
  }
}
```

---

## Best Practices

1. **Start with a clear high-level goal** — the coordinator performs better with well-defined objectives than vague requests.
2. **Use Thinking tier for the coordinator** — the coordinator needs deep reasoning for task decomposition; specialized agents can use Instant.
3. **Limit concurrent agents to 3-4** — more agents increase conflict probability without proportional speed gains.
4. **Define dependencies explicitly** — when tasks have a natural order (refactor → test), declare it to avoid wasted work.
5. **Use dry-run first** — preview the task decomposition before committing to execution.
6. **Review conflicts manually for critical code** — automatic resolution may miss business logic nuances.
7. **Assign narrow scopes to agents** — "test the auth module" is better than "test everything" for quality results.
8. **Enable inter-agent communication** — ensures agents don't produce incompatible changes.
9. **Use the Desktop App for visual orchestration** — the agent panel provides real-time progress monitoring superior to CLI.
10. **Save agent configurations for recurring tasks** — reuse proven agent profiles across projects.

---

## Examples

### Example 1: Parallel Modernization Sprint

```bash
# Modernize a legacy Node.js project in parallel
codex multi-agent \
  --agent refactorer:"Convert all CommonJS requires to ESM imports, \
    update to Node 20 APIs, replace callbacks with async/await" \
  --agent test-writer:"Generate Jest tests for all modules in src/, \
    target 80% coverage, include edge cases" \
  --agent documenter:"Generate TSDoc comments for all exported functions, \
    create API reference in docs/api.md, update README with new setup instructions"
```

### Example 2: Pre-Release Quality Gate

```bash
# Run a comprehensive quality check with multiple specialized agents
codex multi-agent "prepare v2.0 release" \
  --agent security-auditor:"audit all dependencies, check for SQL injection, XSS, CSRF" \
  --agent test-writer:"achieve 90% test coverage, add missing edge case tests" \
  --agent performance-optimizer:"profile API endpoints, optimize queries over 100ms" \
  --agent documenter:"generate CHANGELOG from git history, update migration guide" \
  --conflict-strategy manual
```

### Example 3: Custom Orchestration Plan

```json
// .codex/multi-agent-plan.json
{
  "name": "typescript-migration",
  "description": "Migrate JavaScript project to TypeScript",
  "phases": [
    {
      "phase": 1,
      "parallel": true,
      "tasks": [
        { "agent": "refactorer", "task": "Add TypeScript config, rename .js to .ts" },
        { "agent": "documenter", "task": "Document current API interfaces" }
      ]
    },
    {
      "phase": 2,
      "parallel": true,
      "tasks": [
        { "agent": "refactorer", "task": "Add type annotations to all functions" },
        { "agent": "test-writer", "task": "Convert test files to TypeScript" }
      ]
    },
    {
      "phase": 3,
      "parallel": false,
      "tasks": [
        { "agent": "refactorer", "task": "Fix all TypeScript compilation errors" },
        { "agent": "test-writer", "task": "Verify all tests pass with tsc --noEmit" }
      ]
    }
  ]
}
```

```bash
# Execute the custom plan
codex multi-agent --plan .codex/multi-agent-plan.json
```

### Example 4: Interactive Multi-Agent Session (Desktop App)

```
User: "I need to add authentication to my Express API"

Coordinator: I'll decompose this into 3 parallel tasks:

  🔧 Agent 1 (refactorer): Implement JWT authentication middleware,
     login/register endpoints, and password hashing with bcrypt.

  🧪 Agent 2 (test-writer): Generate tests for auth endpoints,
     token validation, and edge cases (expired tokens, invalid credentials).

  📝 Agent 3 (documenter): Document auth endpoints in OpenAPI format,
     add auth section to README, create .env.example with required vars.

  Dependencies: Agent 2 and 3 will wait for Agent 1 to complete
  the core implementation before generating tests and docs.

  Proceed? [Y/n]
```
