---
name: codex-skill-installer
version: 1.0.0
description: Skill management for the Codex ecosystem using $skill-installer and $skill-creator. Covers three tiers (System, Curated, Experimental), discovery, installation, updating, removal, and custom skill creation. Cross-platform across Codex CLI, IDE extension, and Desktop App.
tags: [openai, codex, skills, installer, skill-creator, plugin, management, curated, experimental, cross-platform]
author: garri333
license: MIT
source: openai/skills
---

# Codex Skill Installer Skill

## Overview

Use this skill whenever the user needs to discover, install, update, remove, or create skills for the Codex ecosystem. The `$skill-installer` tool manages a three-tier skill hierarchy (System, Curated, Experimental) and works identically across Codex CLI, the IDE extension, and the Desktop App. The companion `$skill-creator` tool enables interactive creation of new skills.

---

## When to Activate

- User asks about installing or managing Codex skills.
- User wants to discover available skills or browse the skill catalog.
- User mentions `$skill-installer` or `$skill-creator`.
- User needs to install a curated or experimental skill.
- User wants to create a custom skill for Codex.
- User asks about the `.system/`, `.curated/`, or `.experimental/` directories.
- User wants to update or remove an existing skill.
- User asks about cross-platform skill compatibility (CLI, IDE, Desktop).

---

## Skill Tier Architecture

```
~/.codex/skills/
├── .system/              ← Tier 1: Pre-installed, always available
│   ├── code-generation/
│   ├── file-editing/
│   ├── project-init/
│   └── shell-commands/
├── .curated/             ← Tier 2: Official catalog, $skill-installer <name>
│   ├── react-expert/
│   ├── python-debugger/
│   ├── sql-optimizer/
│   └── docker-helper/
└── .experimental/        ← Tier 3: Community/custom, $skill-installer install <skill> from <path>
    ├── my-custom-skill/
    ├── team-conventions/
    └── internal-api-helper/
```

### Tier Comparison

| Tier | Directory | Install Method | Source | Updates | Stability |
|------|-----------|---------------|--------|---------|-----------|
| **System** | `.system/` | Pre-installed | OpenAI core | Automatic with CLI updates | Stable |
| **Curated** | `.curated/` | `$skill-installer <name>` | Official catalog | `$skill-installer update` | Verified |
| **Experimental** | `.experimental/` | `$skill-installer install <skill> from <path>` | GitHub, local, URL | Manual | Varies |

---

## Step-by-Step Procedures

### 1. Discovery — Finding Available Skills

```bash
# List all installed skills (all tiers)
$skill-installer list

# Output:
# System Skills (always active):
#   ✓ code-generation      v2.1.0  Core code generation capabilities
#   ✓ file-editing          v2.1.0  File modification and creation
#   ✓ project-init          v2.1.0  Project scaffolding
#   ✓ shell-commands        v2.1.0  Terminal command execution
#
# Curated Skills:
#   ✓ react-expert          v1.3.0  React/Next.js development patterns
#   ✓ python-debugger       v1.1.0  Python debugging assistance
#
# Experimental Skills:
#   ✓ my-custom-skill       v0.5.0  Custom team conventions

# Search the curated catalog
$skill-installer search react

# Output:
# Curated Catalog Results:
#   react-expert        v1.3.0  React/Next.js development patterns
#   react-testing       v1.0.0  React Testing Library patterns
#   react-native-dev    v0.9.0  React Native mobile development
#   react-performance   v1.1.0  React performance optimization

# Browse all curated skills
$skill-installer catalog

# Get detailed info about a skill
$skill-installer info react-expert

# Output:
# Name:         react-expert
# Version:      1.3.0
# Tier:         Curated
# Author:       openai
# License:      MIT
# Description:  Expert-level React, Next.js, and React Server Components
#               development patterns and best practices
# Tags:         react, nextjs, frontend, components, hooks
# Size:         12 KB
# Dependencies: None
# Installed:    Yes (updated 3 days ago)

# Search with filters
$skill-installer search --tag backend --sort stars
$skill-installer search --tag python --author openai
```

### 2. Installation — Curated Skills

```bash
# Install a curated skill (Tier 2)
$skill-installer react-expert

# Output:
# ✓ Installing react-expert v1.3.0 to .curated/
# ✓ Skill activated — available in all Codex interfaces
# ✓ Use: "Help me build a React component" to trigger

# Install multiple curated skills at once
$skill-installer react-expert python-debugger sql-optimizer

# Install a specific version
$skill-installer react-expert@1.2.0

# Install with verbose output
$skill-installer react-expert --verbose

# Install without auto-activation
$skill-installer react-expert --no-activate
```

### 3. Installation — Experimental Skills

```bash
# Install from a GitHub repository (Tier 3)
$skill-installer install my-company-skill from github:myorg/codex-skills/company-conventions

# Install from a local directory
$skill-installer install team-rules from /path/to/skills/team-rules

# Install from a URL (tar.gz or zip)
$skill-installer install api-helper from https://example.com/skills/api-helper-v1.tar.gz

# Install from a Git branch
$skill-installer install feature-skill from github:user/repo/skill-name#feature-branch

# Install with a custom name
$skill-installer install my-linter from github:user/repo/linter --as custom-linter

# Install and trust (skip safety prompts)
$skill-installer install company-tool from github:myorg/tools --trust
```

### 4. Updating Skills

```bash
# Update all curated skills to latest versions
$skill-installer update

# Update a specific skill
$skill-installer update react-expert

# Check for available updates without installing
$skill-installer update --check

# Output:
# Updates available:
#   react-expert     1.3.0 → 1.4.0  (new: React 19 support)
#   python-debugger  1.1.0 → 1.2.0  (new: asyncio debugging)

# Force update (overwrite local modifications)
$skill-installer update react-expert --force

# Update experimental skill from its source
$skill-installer update my-custom-skill --from github:myorg/skills/custom
```

### 5. Removing Skills

```bash
# Remove a curated or experimental skill
$skill-installer remove react-expert

# Remove with confirmation prompt
$skill-installer remove react-expert --confirm

# Remove all experimental skills
$skill-installer remove --tier experimental --all

# Remove and purge cached data
$skill-installer remove react-expert --purge

# Note: System skills cannot be removed
$skill-installer remove code-generation
# ✗ Error: System skills cannot be removed. They are part of the core Codex installation.
```

### 6. Skill Activation and Deactivation

```bash
# Deactivate a skill (keep installed but don't use)
$skill-installer deactivate react-expert

# Reactivate a deactivated skill
$skill-installer activate react-expert

# List active vs inactive skills
$skill-installer list --status

# Activate a skill only for the current project
$skill-installer activate react-expert --project-only

# Set skill priorities (when skills overlap)
$skill-installer priority react-expert --level high
```

### 7. Creating Custom Skills with $skill-creator

```bash
# Launch interactive skill creation wizard
$skill-creator

# Wizard flow:
# 1. Skill name: my-api-patterns
# 2. Description: Internal API design patterns and conventions
# 3. Tags: api, rest, internal, patterns
# 4. Tier: experimental
# 5. Template: blank | from-existing | from-prompt
# 6. Generated at: ~/.codex/skills/.experimental/my-api-patterns/

# Create from a template
$skill-creator --template blank --name my-skill

# Create from an existing skill as base
$skill-creator --from react-expert --name react-custom

# Create from a natural language description
$skill-creator --from-prompt "a skill for writing FastAPI endpoints with \
  SQLAlchemy ORM, following our team's naming conventions and error handling patterns"

# Create with specific file structure
$skill-creator --name db-patterns --files "SKILL.md,examples/,templates/"
```

### Skill File Structure

```
my-custom-skill/
├── SKILL.md              ← Main skill definition (YAML frontmatter + instructions)
├── skill.json            ← Metadata and configuration
├── examples/             ← Usage examples
│   ├── basic.md
│   └── advanced.md
├── templates/            ← Code templates the skill can reference
│   ├── component.tsx
│   └── test.spec.ts
└── README.md             ← Human-readable documentation
```

**skill.json format:**

```json
{
  "name": "my-custom-skill",
  "version": "0.1.0",
  "description": "Custom skill for team conventions",
  "author": "your-username",
  "license": "MIT",
  "tags": ["custom", "conventions"],
  "activation": {
    "keywords": ["team pattern", "our convention", "internal API"],
    "file_patterns": ["src/api/**/*.ts"],
    "auto_detect": true
  },
  "compatibility": {
    "codex_cli": ">=1.0.0",
    "codex_desktop": ">=1.0.0",
    "codex_ide": ">=1.0.0"
  },
  "dependencies": {
    "skills": ["react-expert"],
    "tools": ["typescript"]
  }
}
```

### 8. Cross-Platform Usage

Skills work identically across all Codex interfaces:

#### Codex CLI

```bash
# Skills are auto-loaded when relevant to your prompt
codex "create a React component with hooks"
# → react-expert skill activates automatically

# Force a specific skill
codex "build a login form" --skill react-expert

# Disable a skill for one command
codex "build a login form" --no-skill react-expert
```

#### IDE Extension (VS Code)

```json
// settings.json — Codex skill preferences
{
  "codex.skills.autoActivate": true,
  "codex.skills.preferred": ["react-expert", "python-debugger"],
  "codex.skills.disabled": [],
  "codex.skills.experimentalDir": "${workspaceFolder}/.codex/skills"
}
```

#### Desktop App

1. Open **Settings → Skills** in the Codex Desktop App.
2. Browse installed skills across all three tiers.
3. Toggle activation per skill or per project.
4. Install new skills directly from the catalog UI.

### 9. Project-Level Skills

```bash
# Initialize skills for a specific project
$skill-installer init --project

# Creates .codex/skills/ in the project root
# .codex/
# └── skills/
#     ├── .project-config.json
#     └── my-project-skill/
#         └── SKILL.md

# Install a skill scoped to the current project only
$skill-installer install project-conventions from ./skills --project

# Share project skills via version control
# Add .codex/skills/ to your Git repository
git add .codex/skills/
git commit -m "Add project-specific Codex skills"
```

---

## Best Practices

1. **Start with curated skills** — they're verified, maintained, and stable; add experimental skills only when needed.
2. **Use project-level skills for team conventions** — commit them to Git so the whole team shares the same Codex behavior.
3. **Keep custom skills focused** — a skill that does one thing well is more reliable than a monolithic skill.
4. **Version your experimental skills** — use semantic versioning in skill.json for reproducible behavior.
5. **Test skills before sharing** — use `$skill-installer validate` to check for common issues.
6. **Set activation keywords carefully** — overly broad keywords cause unwanted skill activation.
7. **Update curated skills regularly** — run `$skill-installer update --check` weekly.
8. **Use `$skill-creator --from-prompt`** — let AI generate the initial skill structure, then refine manually.
9. **Don't duplicate system skills** — extend or customize them instead of recreating core functionality.
10. **Document your custom skills** — include examples and a README so teammates can use them effectively.

---

## Examples

### Example 1: Setting Up a Frontend Project with Skills

```bash
# Install frontend-relevant curated skills
$skill-installer react-expert react-testing css-modules tailwind-expert

# Verify installation
$skill-installer list --tier curated

# Now Codex automatically applies these skills:
codex "create a dashboard page with a data table, filters, and pagination"
# → react-expert + tailwind-expert skills activate
```

### Example 2: Creating a Team Conventions Skill

```bash
# Create a custom skill interactively
$skill-creator --from-prompt "Our team uses:
  - TypeScript strict mode
  - Zod for validation
  - tRPC for API layer
  - Drizzle ORM for database
  - Naming: camelCase for variables, PascalCase for types
  - Error handling: always use Result<T, E> pattern
  - Testing: Vitest with Testing Library"

# Output: Created ~/.codex/skills/.experimental/team-conventions/SKILL.md
# Review and edit the generated skill, then share:
cp -r ~/.codex/skills/.experimental/team-conventions .codex/skills/
git add .codex/skills/team-conventions
git commit -m "Add team conventions skill for Codex"
```

### Example 3: Installing from GitHub

```bash
# Install a community skill from GitHub
$skill-installer install fastapi-patterns from github:community/codex-skills/fastapi-patterns

# Verify it works
codex "create a CRUD endpoint for products" --skill fastapi-patterns

# If satisfied, pin the version
$skill-installer pin fastapi-patterns@0.3.0
```

### Example 4: Skill Validation and Publishing

```bash
# Validate a custom skill before sharing
$skill-installer validate ~/.codex/skills/.experimental/my-skill

# Output:
# ✓ SKILL.md found with valid YAML frontmatter
# ✓ skill.json is valid
# ✓ Activation keywords are specific enough
# ✓ No conflicts with system or curated skills
# ✓ Examples directory contains valid examples
# ⚠ Warning: No README.md found (recommended)
# Result: PASS (1 warning)

# Package for distribution
$skill-installer pack my-skill --output my-skill-v1.0.0.tar.gz

# Publish to the curated catalog (requires OpenAI developer account)
$skill-installer publish my-skill --catalog curated
```
