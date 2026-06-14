# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-22

### Added — 7 New Categories (37 new skills)

- **15-huggingface/** — 5 official Hugging Face ML/AI skills
  - `hf-cli`: HuggingFace CLI interface (auth, repos, upload/download)
  - `hf-datasets`: Dataset creation and management
  - `hf-trainer`: Model training with Trainer API (LoRA/QLoRA, distributed)
  - `hf-evaluation`: Standardized model evaluation (GLUE, MMLU, etc.)
  - `hf-jobs`: Job orchestration (Inference Endpoints, AutoTrain, Spaces)

- **16-openai-codex/** — 6 OpenAI Codex ecosystem skills
  - `codex-cli`: Codex CLI mastery with GPT-5.2
  - `codex-multi-agent`: Multi-agent architecture (Desktop App Feb 2026)
  - `codex-skill-installer`: $skill-installer and $skill-creator tools
  - `codex-pr-creator`: Automated PR creation with CI validation
  - `codex-react-linter`: React Code Fix & Linter (242K stars MCP Market)
  - `codex-prompt-enhancer`: Prompt Finder & Enhancer (144K accesses)

- **17-block-goose/** — 5 enterprise skills from Block/Goose
  - `goose-workflows`: Repeatable deployment/migration workflows
  - `goose-incident-response`: P0-P4 incident response and RCA
  - `goose-code-review`: Enterprise multi-dimension code review
  - `goose-security-audit`: OWASP, CVE, SOC 2, ISO 27001 auditing
  - `goose-release-manager`: End-to-end release management

- **18-openclaw/** — 6 OpenClaw community skills
  - `openclaw-memory`: Triple memory system (LanceDB + Git-Notes + File)
  - `openclaw-security`: Agent security (injection, malware, audit)
  - `openclaw-self-reflect`: Self-improvement via conversation analysis
  - `openclaw-project-management`: Project management with task-observer
  - `openclaw-messaging`: Cross-platform messaging integration
  - `openclaw-reasoning`: Equilibrium-Native advanced reasoning

- **19-testing-quality/** — 5 testing and code quality skills
  - `webapp-testing-playwright`: E2E testing with Playwright
  - `systematic-debugging`: Structured debugging methodology
  - `testing-anti-patterns`: Common testing mistakes and fixes
  - `code-quality-audit`: Codebase health assessment
  - `tdd-bdd-patterns`: TDD and BDD development patterns

- **20-orchestration/** — 5 multi-agent orchestration skills
  - `multi-agent-coordinator`: Central multi-agent coordinator
  - `agent-specialization`: Configure domain-specialized agents
  - `task-decomposition`: Break complex tasks into subtasks
  - `parallel-execution`: Parallel agent task execution
  - `open-source-maintainer`: End-to-end GitHub repo maintenance

- **21-productivity/** — 5 productivity and tools skills
  - `skill-writer`: Meta-skill that creates other skills
  - `codebase-health-reporter`: Automated codebase health reports
  - `n8n-automation`: n8n workflow automation integration
  - `voxtral-transcription`: Voxtral Transcribe 2 (open-source, local)
  - `prompt-finder-enhancer`: 140K+ prompt library and optimization

### Added — Cross-Platform Support

- `AGENTS.md` for GitHub Copilot, Cursor, Windsurf, Cline, Aider compatibility
- OpenSkills installation support (`npm i -g openskills`)
- Claude Code plugin installation support
- Codex `$skill-installer` support
- `gemini-extension.json` placeholder for Gemini CLI

### Changed

- **README.md** completely rewritten with:
  - 2026 ecosystem updates (Claude Opus 4.6, GPT-5.2, Codex Desktop, Voxtral)
  - 6 installation methods (global, Claude plugin, OpenSkills, npx, per-project, Codex)
  - Platform compatibility matrix (9 agents)
  - Skills discovery guide (12 sources)
  - Expanded credits with 7 official + 7 community + 5 marketplace sources
  - Quality criteria based on industry best practices

### Statistics

- Skills: 198+ → **245+** (+47 skills, +24% growth)
- Categories: 14 → **21** (+7 categories)
- Sources: 5 → **17** sources
- Compatible agents: 6 → **9** agents

## [1.0.0] - 2026-02-18

### Added

- Initial release with 198+ skills in 14 categories
- K-Dense-AI scientific skills (117)
- Vercel Labs official skills (5)
- Anthropic official skills (16)
- Social & Communications skills (5)
- Custom skills (55) across 10 categories
