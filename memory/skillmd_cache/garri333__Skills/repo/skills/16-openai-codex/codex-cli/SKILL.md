---
name: codex-cli
version: 1.0.0
description: OpenAI Codex CLI mastery skill for installation, authentication, terminal commands, code generation from natural language, file editing, project scaffolding, and IDE integrations. Covers GPT-5.2 Instant/Thinking tiers and shell/container execution modes.
tags: [openai, codex, cli, code-generation, gpt-5.2, terminal, scaffolding, ide, vscode, ai-coding]
author: garri333
license: MIT
source: openai/skills
---

# Codex CLI Skill

## Overview

Use this skill whenever the user needs to install, configure, or operate the OpenAI Codex CLI — the primary command-line interface for AI-assisted code generation, file editing, project scaffolding, and developer workflow automation powered by GPT-5.2.

> **Important migration notice (Feb 13, 2026):** GPT-4o has been officially retired. All Codex CLI users must migrate to GPT-5.2 model tiers. Legacy `--model gpt-4o` flags will return errors.

---

## When to Activate

- User asks to install or update the Codex CLI.
- User needs to authenticate with an OpenAI API key.
- User wants to generate code from a natural language prompt in the terminal.
- User asks about editing existing files using Codex.
- User wants to scaffold a new project (frontend, backend, full-stack).
- User asks about GPT-5.2 model tiers (Instant vs Thinking).
- User wants to integrate Codex CLI with VS Code or another IDE.
- User asks about execution modes (local shell vs hosted container).
- User needs to configure Codex CLI settings or preferences.

---

## Step-by-Step Procedures

### 1. Installation

```bash
# Install Codex CLI globally via npm
npm install -g @openai/codex

# Verify installation
codex --version

# Update to latest version
npm update -g @openai/codex

# Alternative: install via npx (no global install)
npx @openai/codex --help
```

**System requirements:**
- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 1.22+
- Git 2.30+ (for project scaffolding)
- OS: macOS, Linux, Windows (WSL2 recommended on Windows)

### 2. Authentication

```bash
# Set API key via environment variable (recommended)
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# On Windows PowerShell
$env:OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# On Windows CMD
set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Interactive login (stores key in ~/.codex/config.json)
codex auth login

# Verify authentication
codex auth whoami

# Use a specific organization
codex auth login --org org-xxxxxxxxxxxx

# Logout / clear stored credentials
codex auth logout
```

**Persistent configuration (~/.codex/config.json):**

```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "organization": "org-xxxxxxxxxxxx",
  "default_model": "gpt-5.2-instant",
  "default_mode": "local"
}
```

### 3. GPT-5.2 Model Tiers

Codex CLI operates on two GPT-5.2 tiers introduced after the GPT-4o retirement on Feb 13, 2026:

| Tier | Model ID | Use Case | Latency | Cost |
|------|----------|----------|---------|------|
| **Instant** | `gpt-5.2-instant` | Fast completions, high-volume tasks, simple edits | ~200ms | Lower |
| **Thinking** | `gpt-5.2-thinking` | Deep reasoning, complex architecture, multi-file refactoring | ~2-8s | Higher |

```bash
# Use Instant tier (default — fast, high-volume)
codex "add input validation to app.py" --model instant

# Use Thinking tier (deep reasoning for complex tasks)
codex "redesign the authentication module with OAuth2 and PKCE flow" --model thinking

# Set default tier
codex config set model thinking
```

**Tier selection guidance:**
- **Instant**: Single-file edits, boilerplate code, formatting, simple bug fixes, test generation.
- **Thinking**: Multi-file refactoring, architecture decisions, security audits, complex algorithms, debugging intricate issues.

### 4. Code Generation from Natural Language

```bash
# Generate a complete file
codex "create a FastAPI server with CRUD endpoints for a todo app"

# Generate and write directly to a file
codex "create a Python dataclass for User with validation" -o models/user.py

# Generate with specific language
codex "implement binary search" --lang rust

# Generate with context from existing files
codex "add unit tests for this module" --context src/utils.py

# Multi-file generation
codex "create a React component with tests and Storybook story for a DatePicker" --multi

# Pipe input for transformation
cat legacy_code.py | codex "refactor this to use modern Python 3.12 patterns"

# Generate with specific framework constraints
codex "create an Express.js middleware for rate limiting" --framework express
```

### 5. File Editing

```bash
# Edit an existing file with natural language instructions
codex edit src/app.py "add error handling to all database calls"

# Edit multiple files at once
codex edit src/**/*.ts "convert all var declarations to const/let"

# Preview changes before applying (dry run)
codex edit src/app.py "add logging" --dry-run

# Edit with diff output
codex edit src/app.py "optimize the search function" --diff

# Interactive edit mode (review each change)
codex edit src/app.py "refactor for readability" --interactive

# Undo last edit
codex edit --undo
```

### 6. Project Scaffolding

```bash
# Scaffold a new project interactively
codex init

# Scaffold with a specific template
codex init --template react-typescript

# Scaffold from a description
codex init "a full-stack Next.js app with Prisma ORM, PostgreSQL, and Tailwind CSS"

# Scaffold with specific options
codex init "REST API" --lang python --framework fastapi --db postgresql --auth jwt

# Scaffold and install dependencies automatically
codex init "Vue 3 dashboard" --install

# Available built-in templates
codex init --list-templates
```

### 7. Execution Modes

#### Local Shell Mode (default)

Commands execute directly in the user's local terminal environment:

```bash
# Explicit local mode
codex "list all TODO comments in the project" --mode local

# Local mode has full access to:
# - Local file system
# - Installed CLI tools (git, docker, npm, etc.)
# - Environment variables
# - Running services (databases, servers)
```

#### Hosted Container Mode

Commands execute in an isolated cloud container:

```bash
# Run in hosted container (sandboxed environment)
codex "run the full test suite and fix any failures" --mode container

# Container mode provides:
# - Isolated execution (safe for untrusted operations)
# - Pre-configured environments (Node, Python, Rust, Go, etc.)
# - No impact on local system
# - Reproducible results

# Specify container image
codex "build and test the project" --mode container --image node:20-alpine

# Container with GPU access (for ML tasks)
codex "train the model on sample data" --mode container --gpu
```

### 8. IDE Integrations

#### VS Code Extension

```bash
# Install the Codex VS Code extension
code --install-extension openai.codex-vscode

# Or search "OpenAI Codex" in VS Code Extensions marketplace
```

**VS Code keybindings:**
- `Ctrl+Shift+C` / `Cmd+Shift+C`: Open Codex command palette
- `Ctrl+K Ctrl+G` / `Cmd+K Cmd+G`: Generate code at cursor
- `Ctrl+K Ctrl+E` / `Cmd+K Cmd+E`: Edit selected code
- `Ctrl+K Ctrl+X` / `Cmd+K Cmd+X`: Explain selected code

**VS Code settings (settings.json):**

```json
{
  "codex.model": "gpt-5.2-instant",
  "codex.mode": "local",
  "codex.autoSuggest": true,
  "codex.inlineSuggestions": true,
  "codex.suggestDelay": 300,
  "codex.contextFiles": 5,
  "codex.telemetry": false
}
```

#### JetBrains Plugin

```bash
# Install via JetBrains Marketplace
# Settings → Plugins → Search "OpenAI Codex" → Install

# Or install from CLI
idea installPlugins openai.codex-jetbrains
```

#### Neovim Integration

```lua
-- In init.lua or after/plugin/codex.lua
require('codex').setup({
  api_key = vim.env.OPENAI_API_KEY,
  model = 'gpt-5.2-instant',
  keymaps = {
    generate = '<leader>cg',
    edit = '<leader>ce',
    explain = '<leader>cx',
  },
})
```

### 9. Advanced Usage

#### Batch Operations

```bash
# Process multiple files with the same instruction
codex batch "add JSDoc comments to all exported functions" --glob "src/**/*.ts"

# Batch with concurrency control
codex batch "add type annotations" --glob "src/**/*.py" --concurrency 4

# Batch with progress reporting
codex batch "migrate from CommonJS to ESM" --glob "src/**/*.js" --progress
```

#### Piping and Composition

```bash
# Chain with other CLI tools
git diff HEAD~1 | codex "summarize these changes for a commit message"

# Generate and pipe to clipboard
codex "regex for email validation" | pbcopy

# Use in scripts
TESTS=$(codex "generate pytest tests for $(cat src/utils.py)" --raw)
echo "$TESTS" > tests/test_utils.py
```

#### Configuration Profiles

```bash
# Create a named profile
codex config profile create work --model thinking --mode container

# Switch profiles
codex config profile use work

# List profiles
codex config profile list
```

---

## Best Practices

1. **Use Instant tier by default** — switch to Thinking only for complex, multi-step reasoning tasks to optimize cost and latency.
2. **Provide context** — use `--context` to include relevant files so Codex understands your codebase patterns.
3. **Use dry-run for edits** — always preview changes with `--dry-run` before applying to production code.
4. **Leverage container mode for risky operations** — sandbox untrusted code execution or destructive operations.
5. **Set up IDE integration** — inline suggestions dramatically improve developer velocity versus terminal-only usage.
6. **Use batch operations for large refactors** — process entire directories consistently rather than file-by-file.
7. **Secure your API key** — never commit keys to version control; use environment variables or `codex auth login`.
8. **Pin your model tier in CI/CD** — avoid unexpected behavior by explicitly setting `--model` in automation scripts.
9. **Keep CLI updated** — run `npm update -g @openai/codex` regularly for latest features and model improvements.
10. **Use profiles** — separate work/personal configurations to avoid mixing API keys and billing.

---

## Examples

### Example 1: Quick Bug Fix with Instant Tier

```bash
# User reports a bug in the payment module
codex edit src/payments/processor.py \
  "fix the race condition in process_payment where concurrent requests can double-charge" \
  --model instant --diff
```

### Example 2: Architecture Redesign with Thinking Tier

```bash
# Deep reasoning for complex refactoring
codex "analyze the current monolithic architecture in src/ and propose a microservices \
  decomposition plan with service boundaries, API contracts, and migration steps" \
  --model thinking -o architecture-plan.md
```

### Example 3: Full Project Scaffold

```bash
# Scaffold a production-ready project
codex init "SaaS dashboard with Next.js 15, tRPC, Prisma, PostgreSQL, \
  Stripe billing, NextAuth.js, Tailwind CSS, and Playwright tests" \
  --install --git-init
```

### Example 4: CI/CD Integration

```yaml
# .github/workflows/codex-review.yml
name: Codex Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @openai/codex
      - run: |
          git diff origin/main...HEAD | codex "review these changes for bugs, \
            security issues, and performance problems" --model thinking --raw \
          > review.md
      - uses: actions/upload-artifact@v4
        with:
          name: codex-review
          path: review.md
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Example 5: Migration from GPT-4o

```bash
# Check current configuration
codex config get model

# If still set to gpt-4o, update to gpt-5.2
codex config set model gpt-5.2-instant

# Update all project-level configs
find . -name ".codex.json" -exec sed -i 's/gpt-4o/gpt-5.2-instant/g' {} +

# Verify migration
codex "hello world test" --verbose
```
