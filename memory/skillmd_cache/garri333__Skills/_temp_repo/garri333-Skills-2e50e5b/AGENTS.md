# AGENTS.md — Cross-Platform Agent Instructions

> This file provides instructions for AI agents that read AGENTS.md (GitHub Copilot, Cursor, Windsurf, Cline, Aider, OpenCode, and others).

## About This Repository

This is a **skills library** with 245+ reusable skills for AI coding agents. Skills follow the [SKILL.md standard](https://github.com/anthropics/skills) by Anthropic (December 2025).

## How to Use These Skills

When working on a task, search this repository for relevant skills. Each skill is in its own directory under `skills/` with a `SKILL.md` file containing specialized knowledge.

### Skill Categories Available

| Category | Path | Focus |
|----------|------|-------|
| Writing & Content | `skills/01-writing-content/` | Copywriting, SEO, marketing |
| Frontend & Design | `skills/02-frontend-design/` | React, UI/UX, web design |
| Backend & APIs | `skills/03-backend-api/` | API design, Excel, PDF |
| AI Agents | `skills/04-ai-agents/` | Prompts, memory, self-improvement |
| DevOps & Git | `skills/05-devops-git/` | Git, CI/CD, MCP, Vercel |
| Data & Analysis | `skills/06-data-analysis/` | Visualization, crypto, analytics |
| Security | `skills/07-security-compliance/` | Auditing, monitoring |
| Automation | `skills/08-automation/` | Browser, email, calendar, search |
| Research | `skills/09-research/` | DeepWiki, knowledge base, web search |
| PrivaLex | `skills/10-privalex/` | PrivaLex Partners specific |
| Scientific | `skills/11-scientific/` | 117 scientific skills (K-Dense-AI) |
| Vercel Labs | `skills/12-vercel-labs/` | Official Vercel skills |
| Anthropic | `skills/13-anthropic/` | Official Anthropic skills |
| Social & Comms | `skills/14-social-comms/` | Twitter, Discord, LinkedIn, Reddit |
| Hugging Face | `skills/15-huggingface/` | ML/AI: CLI, datasets, training, evaluation |
| OpenAI Codex | `skills/16-openai-codex/` | Codex CLI, multi-agent, PR creation |
| Block/Goose | `skills/17-block-goose/` | Enterprise: workflows, incidents, releases |
| OpenClaw | `skills/18-openclaw/` | Memory, security, self-reflection |
| Testing | `skills/19-testing-quality/` | Playwright, debugging, TDD/BDD |
| Orchestration | `skills/20-orchestration/` | Multi-agent coordination |
| Productivity | `skills/21-productivity/` | Skill writer, health reports, n8n |

### Quick Skill Loading

For any task, load the relevant SKILL.md by reading the file at the appropriate path. Example:

- Building a React app → Read `skills/02-frontend-design/react-best-practices/SKILL.md`
- Training an ML model → Read `skills/15-huggingface/hf-trainer/SKILL.md`
- Setting up CI/CD → Read `skills/05-devops-git/github-cli/SKILL.md`
- Debugging a bug → Read `skills/19-testing-quality/systematic-debugging/SKILL.md`
- Multi-agent workflow → Read `skills/20-orchestration/multi-agent-coordinator/SKILL.md`

## Conventions

- Follow the SKILL.md standard for any new skills
- Use YAML frontmatter with: name, version, description, tags, author, license
- Keep skills focused on a single responsibility
- Use imperative instructions with explicit inputs and outputs
- Use Conventional Commits for git messages: `feat:`, `fix:`, `docs:`, `refactor:`
