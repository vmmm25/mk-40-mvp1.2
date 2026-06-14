# 🧠 Skills — Librería de Skills para Agentes IA

[![Agent Skills Standard](https://img.shields.io/badge/Agent%20Skills-Standard-blue)](https://agentskills.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Skills: 245+](https://img.shields.io/badge/Skills-245%2B-orange)](skills/)
[![Categories: 21](https://img.shields.io/badge/Categories-21-purple)](skills/)
[![OpenSkills Compatible](https://img.shields.io/badge/OpenSkills-Compatible-brightgreen)](https://github.com/numman-ali/n-skills)
[![SKILL.md Standard](https://img.shields.io/badge/SKILL.md-Anthropic%20Standard-blueviolet)](https://github.com/anthropics/skills)
[![Last Updated](https://img.shields.io/badge/Updated-Feb%202026-red)]()

Repositorio de **245+ skills reutilizables para agentes IA** — la colección más completa en español para potenciar tus proyectos con GitHub Copilot, Claude Code, Cursor, Codex CLI/Desktop, Cline, Windsurf, Aider, Goose y cualquier herramienta que soporte el estándar SKILL.md.

> **Formato SKILL.md** — Estándar de Anthropic (diciembre 2025), adoptado por OpenAI, Hugging Face y la industria. Arquitectura de *divulgación progresiva*: el agente carga solo metadatos al inicio (~docenas de tokens por skill), con contenido completo cargado dinámicamente cuando es relevante.

---

## 🌟 Novedades Febrero 2026

| Fecha | Evento | Impacto |
|-------|--------|---------|
| 3 feb 2026 | **Claude Opus 4.6** | Menor tasa de rechazo, ventana de contexto para codebases medianos, mejor coherencia en refactorizaciones |
| 2 feb 2026 | **Codex Desktop App** | Arquitectura multi-agente: tests + refactoring + docs en paralelo |
| 5 feb 2026 | **Voxtral Transcribe 2** | Transcripción open-source local, <200ms, 13 idiomas |
| 13 feb 2026 | **Retiro GPT-4o** | Migración obligatoria a GPT-5.2 (Instant/Thinking/Prism) |
| Feb 2026 | **7 nuevas categorías** | +37 skills: HuggingFace, OpenAI, Block/Goose, OpenClaw, Testing, Orchestration, Productivity |

---

## 🎯 Para qué sirve este repositorio

Cuando empiezas un proyecto nuevo, el agente puede buscar en este repo y encontrar las skills que necesita:

| Tu proyecto | Skills recomendadas |
|------------|---------------------|
| **Web app** | `frontend-design`, `web-design-guidelines`, `seo-content`, `react-best-practices` |
| **Agente IA** | `prompt-engineering`, `memory-management`, `skill-creator`, `multi-agent-coordinator` |
| **API** | `api-design`, `git-conventional-commits`, `systematic-debugging`, `tdd-bdd-patterns` |
| **ML/AI** | `hf-trainer`, `hf-datasets`, `hf-evaluation`, `lora-finetuning` |
| **DevOps** | `goose-workflows`, `goose-release-manager`, `github-cli`, `vercel-platform` |
| **Seguridad** | `security-audit`, `goose-security-audit`, `openclaw-security`, `testing-anti-patterns` |
| **Multi-agente** | `multi-agent-coordinator`, `agent-specialization`, `parallel-execution` |
| **Contenido** | `copywriting-persuasive`, `humanizer`, `marketing-mode`, PrivaLex skills |

---

## 📦 Estructura del repositorio

```
skills/
├── 01-writing-content/          # Escritura, copywriting, contenido, marketing
├── 02-frontend-design/          # UI/UX, React, diseño web, generación de imágenes
├── 03-backend-api/              # APIs, servidores, bases de datos
├── 04-ai-agents/                # Prompts, agentes, skills IA
├── 05-devops-git/               # Git, CI/CD, despliegues, MCP
├── 06-data-analysis/            # Datos, visualización, crypto, estadística
├── 07-security-compliance/      # Ciberseguridad, normativas
├── 08-automation/               # Email, calendario, tareas, búsqueda web
├── 09-research/                 # Investigación, análisis, DeepWiki, búsqueda
├── 10-privalex/                 # Skills específicas de PrivaLex Partners
├── 11-scientific/               # 117 skills científicas (K-Dense-AI)
├── 12-vercel-labs/              # 5 skills oficiales de Vercel Labs
├── 13-anthropic/                # 16 skills oficiales de Anthropic
├── 14-social-comms/             # Twitter/X, Slack, Discord, LinkedIn, Reddit
├── 15-huggingface/          🆕  # 5 skills oficiales de Hugging Face (ML/AI)
├── 16-openai-codex/         🆕  # 6 skills del ecosistema OpenAI Codex
├── 17-block-goose/          🆕  # 5 skills enterprise de Block/Goose
├── 18-openclaw/             🆕  # 6 skills de la comunidad OpenClaw
├── 19-testing-quality/      🆕  # 5 skills de testing y calidad de código
├── 20-orchestration/        🆕  # 5 skills de orquestación multi-agente
├── 21-productivity/         🆕  # 5 skills de productividad y herramientas
├── _templates/                  # Plantillas para crear nuevas skills
├── AGENTS.md                    # Compatibilidad cross-platform (Copilot, Cursor, etc.)
└── commands/                    # Comandos slash para agentes
```

---

## 🚀 Cómo usar este repositorio

### Opción 1: Instalación global (recomendado)

Las skills están disponibles en todos tus proyectos:

```bash
# Para Cursor
cp -r skills/* ~/.cursor/skills/

# Para Claude Code
cp -r skills/* ~/.claude/skills/

# Para Codex
cp -r skills/* ~/.codex/skills/

# Para GitHub Copilot (lee AGENTS.md automáticamente)
cp AGENTS.md ~/tu-proyecto/.github/copilot-instructions.md
```

### Opción 2: Plugin de Claude Code

```bash
# Registrar marketplace
/plugin marketplace add garri333/Skills

# Instalar skills individuales
/plugin install prompt-engineering@garri333/Skills
/plugin install hf-trainer@garri333/Skills
```

### Opción 3: OpenSkills (universal — todos los agentes)

```bash
# Instalar OpenSkills CLI
npm i -g openskills

# Instalar skills desde este repo
openskills install garri333/Skills

# Sincronizar con todos tus agentes
openskills sync
```

### Opción 4: Usando npx (skills.sh ecosystem)

```bash
npx skills add garri333/Skills/prompt-engineering
npx skills add garri333/Skills/hf-trainer
npx skills add garri333/Skills/multi-agent-coordinator
```

### Opción 5: Instalación por proyecto

```bash
mkdir -p .cursor/skills
cp -r skills/04-ai-agents/prompt-engineering .cursor/skills/
cp -r skills/15-huggingface/hf-trainer .cursor/skills/
cp -r skills/20-orchestration/multi-agent-coordinator .cursor/skills/
```

### Opción 6: Codex $skill-installer

```bash
# Skills curados
$skill-installer prompt-engineering

# Skills experimentales
$skill-installer install hf-trainer from garri333/Skills/skills/15-huggingface
```

---

## 🔗 Compatibilidad de Plataformas

| Agente | Método de integración | Estado |
|--------|----------------------|--------|
| **Claude Code** | `/plugin install` o copia a `~/.claude/skills/` | ✅ Nativo |
| **GitHub Copilot** | Lee `AGENTS.md` automáticamente | ✅ Nativo |
| **Cursor** | Copia a `~/.cursor/skills/` | ✅ Nativo |
| **Codex CLI/Desktop** | `$skill-installer` o copia a `~/.codex/skills/` | ✅ Nativo |
| **Cline** | OpenSkills → `AGENTS.md` | ✅ Via OpenSkills |
| **Windsurf** | OpenSkills → `AGENTS.md` | ✅ Via OpenSkills |
| **Aider** | Lee `AGENTS.md` | ✅ Via AGENTS.md |
| **Goose (Block)** | Lee `SKILL.md` estándar | ✅ Nativo |
| **Gemini CLI** | `gemini-extension.json` (planificado) | 🔜 Próximo |

---

## 📋 Catálogo Completo de Skills

### 01. Escritura y Contenido (6 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `copywriting-persuasive` | Técnicas de copywriting persuasivo y conversión | Emails, ads, landing pages, sales copy |
| `humanizer` | Detecta y elimina marcadores de texto IA | Revisar textos antes de publicar |
| `marketing-mode` | 23 frameworks de marketing (AIDA, growth, CRO, SEO) | Estrategias de marketing y contenido |
| `prompt-log` | Extrae transcripts de sesiones de agentes | Documentar y revisar conversaciones IA |
| `resume-optimizer` | CV con scoring ATS y exportación PDF/DOCX | Crear o mejorar currículums |
| `seo-content` | Guía completa de SEO y estructura editorial | Crear blog posts, landing pages, contenido web |

### 02. Frontend y Diseño (8 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `frontend-design` | Guía de diseño UI/UX y accesibilidad | Revisar o crear interfaces web |
| `image-generation` | DALL-E 3, FLUX, Stable Diffusion — texto a imagen | Generar imágenes con IA |
| `react-best-practices` | Patrones React y Next.js de Vercel Engineering | Escribir o refactorizar código React |
| `react-composition-patterns` | Patrones de composición React escalables | Refactorizar componentes |
| `react-native-mobile` | React Native y Expo para apps móviles | Desarrollar apps móviles |
| `superdesign` | Expert guidelines para UIs modernas y hermosas | Crear interfaces premium |
| `uiux-pro` | Inteligencia de diseño UI/UX para interfaces pulidas | Proyectos con React, Vue, Svelte, Tailwind |
| `web-design-guidelines` | Guía de mejores prácticas para interfaces web | Auditar UI, accessibility, UX |

### 03. Backend y APIs (4 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `api-design` | Principios y patrones para diseñar APIs robustas | Diseñar o revisar APIs REST/GraphQL |
| `vercel-deploy` | Despliegue de aplicaciones en Vercel | Deployar apps web |
| `excel-data` | Leer, escribir y manipular archivos Excel | Trabajar con datos en Excel |
| `pdf-builder` | Generar PDFs profesionales desde Markdown | Crear documentos, reports, NDAs |

### 04. Agentes IA (6 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `prompt-engineering` | Técnicas avanzadas de ingeniería de prompts | Crear o mejorar prompts |
| `skill-creator` | Guía para crear nuevas skills | Crear una skill nueva |
| `memory-management` | Configurar memoria persistente para agentes | Añadir memoria a un agente |
| `self-improving-agent` | Captura aprendizajes para mejorar performance | Agentes que aprenden de sus errores |
| `deep-research-agent` | Investigación compleja multi-step | Tareas de investigación profunda |
| `coding-agent` | Control de agentes de coding (Claude Code, Codex) | Programar mediante subagentes |

### 05. DevOps y Git (4 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `git-conventional-commits` | Formato Conventional Commits para mensajes git | Hacer commits, changelogs, versionado |
| `github-cli` | Interfaz especializada con GitHub CLI (`gh`) | Issues, PRs, CI/CD, GitHub API |
| `mcp-porter` | Descubrir, instalar y llamar servidores MCP | Gestionar el ecosistema MCP |
| `vercel-platform` | Deploy y gestión de proyectos en Vercel | Deployar, dominios, variables de entorno |

### 06. Datos y Análisis (5 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `crypto-wallet` | Wallets multi-chain: Ethereum, Polygon, Solana | Leer balances y transacciones blockchain |
| `data-visualization` | Crear visualizaciones de datos efectivas | Charts, gráficos, dashboards |
| `financial-analysis` | Análisis financiero de stocks y mercados | Finanzas, inversiones, mercados |
| `ga4-analytics` | Query Google Analytics 4 via API | Analizar métricas web |
| `statistical-analysis` | Análisis estadístico y metodología | Análisis de datos, informes |

### 07. Seguridad y Compliance (2 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `security-audit` | Auditoría de seguridad completa | Revisar configuraciones de seguridad |
| `security-monitor` | Monitorización de seguridad en tiempo real | Detectar intrusiones y anomalías |

### 08. Automatización (12 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `browser-automation` | Automatización de navegador (headless) | Scraping, testing, workflows web |
| `caldav-calendar` | Eventos de calendario via CalDAV (Google, iCloud) | Crear/leer eventos de calendario |
| `email` | Enviar/leer email via IMAP/SMTP y Gmail API | Notificaciones, automatización de email |
| `faster-whisper` | Transcripción de voz local con Whisper | Transcribir audio/video sin API |
| `google-workspace` | CLI para Gmail, Calendar, Drive, Contacts | Automatizar Google Workspace |
| `notion` | API de Notion — bases de datos, páginas, bloques | Gestión de conocimiento con Notion |
| `realtime-web-search` | Búsqueda web en tiempo real (Tavily, Serper, Brave) | Información actual y en tiempo real |
| `remind-me` | Crear recordatorios con lenguaje natural | Programar tareas futuras |
| `todoist` | Gestión de tareas via Todoist REST API | Crear y organizar tareas desde código |
| `weather` | Datos meteorológicos sin API key con wttr.in | Información del tiempo actual |
| `whatsapp-messaging` | Enviar mensajes WhatsApp via CLI | Notificaciones, mensajes automáticos |
| `youtube-downloader` | Descargar videos con yt-dlp | Descargar contenido de YouTube y más |

### 09. Research e Investigación (7 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `deepwiki` | Q&A sobre cualquier repositorio GitHub via DeepWiki | Entender librerías y codebases |
| `knowledge-base` | Sistema de gestión de conocimiento (LanceDB, RAG) | Gestionar knowledge base del proyecto |
| `research-deep` | Investigación profunda con arXiv, Semantic Scholar | Research complejo y papers científicos |
| `summarize-content` | Resumen inteligente de URLs o archivos | Leer y resumir contenido rápidamente |
| `thinking-partner` | Colaborador de pensamiento para problemas complejos | Explorar problemas con preguntas |
| `web-search-brave` | Búsqueda web via Brave Search API | Buscar documentación, hechos, noticias |
| `web-search-exa` | Búsqueda semántica con Exa AI | Encontrar código, papers, info empresa |

### 10. PrivaLex Partners (8 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `privalex-product` | Positioning, servicios y proof points de PrivaLex | Cualquier contenido que describe PrivaLex |
| `privalex-voice-and-tone` | Voz, tono y guardarraíles anti-fluff | TODO el contenido de PrivaLex |
| `compliance-frameworks` | Base de conocimiento: ISO 27001, NIS2, GDPR, etc. | Contenido técnico de compliance |
| `seo-guidelines` | SEO específico para contenido PrivaLex | Blog posts y contenido web |
| `target-personas` | Perfiles de CISO, CTO, DPO, Founder | Personalizar contenido por audiencia |
| `content-formats` | Templates: blog, LinkedIn, newsletter, case study | Generar formatos específicos |
| `competitive-landscape` | Posicionamiento vs Vanta, ECIJA, etc. | Contenido comparativo |
| `examples-hall-of-fame` | Ejemplos aprobados de contenido PrivaLex | Referencia de calidad y tono |

### 11. Scientific — K-Dense-AI (117 skills)

> **Fuente:** [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)

| Dominio | Skills destacadas |
|---------|-------------------|
| Bioinformática | scanpy, biopython, deeptools, pysam, pydeseq2, anndata, cellxgene-census |
| Química | rdkit, chembl-database, pubchem-database, matchms, molfeat, deepchem |
| Drug Discovery | drugbank-database, opentargets-database, diffdock, pytdc, medchem |
| Genómica | ensembl-database, gene-database, gwas-database, clinvar-database, gget |
| Clínica | pyhealth, clinical-reports, clinical-decision-support, clinpgx-database |
| Física / Quantum | qiskit, pennylane, cirq, qutip, fluidsim, pymatgen |
| ML / Datos | pytorch-lightning, polars, dask, networkx, plotly, matplotlib, pymc |
| Lab Automation | opentrons-integration, pylabrobot, lamindb, latchbio-integration |
| Publicación | latex-posters, pptx-posters, scientific-slides, paper-2-web, markitdown |
| Investigación | literature-review, hypothesis-generation, peer-review, scientific-brainstorming |

[→ Ver todas las 117 skills científicas](skills/11-scientific/)

### 12. Vercel Labs — Oficial (5 skills)

> **Fuente:** [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)

| Skill | Descripción |
|-------|-------------|
| `composition-patterns` | Patrones avanzados de composición React |
| `react-best-practices` | Mejores prácticas React oficiales de Vercel |
| `react-native-skills` | Patrones oficiales de React Native |
| `vercel-deploy-claimable` | Deployments reclamables en Vercel |
| `web-design-guidelines` | Guías de diseño web oficiales de Vercel |

### 13. Anthropic — Oficial (16 skills)

> **Fuente:** [anthropics/skills](https://github.com/anthropics/skills) — 14,300+ ⭐ GitHub

| Skill | Descripción |
|-------|-------------|
| `algorithmic-art` | Arte generativo y creative coding |
| `brand-guidelines` | Creación y aplicación de brand guidelines |
| `canvas-design` | Patrones de diseño para canvas/artifacts |
| `doc-coauthoring` | Escritura colaborativa de documentos |
| `docx` | Generación de documentos Word |
| `frontend-design` | Patrones de frontend de Anthropic |
| `internal-comms` | Escritura de comunicaciones internas |
| `mcp-builder` | Construir servidores MCP desde cero |
| `pdf` | Generación y manipulación de PDFs |
| `pptx` | Creación de presentaciones PowerPoint |
| `skill-creator` | Crear nuevas skills para agentes |
| `slack-gif-creator` | Creación de GIFs animados para Slack |
| `theme-factory` | Generación de temas de UI |
| `web-artifacts-builder` | Creación de artifacts web |
| `webapp-testing` | Testing de aplicaciones web |
| `xlsx` | Generación de hojas de cálculo Excel |

### 14. Social & Comunicaciones (5 skills)

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `bird-twitter` | X/Twitter — posts, búsqueda, timeline, DMs | Publicar o monitorear en X/Twitter |
| `discord` | Discord bots, webhooks, slash commands | Integrar con servidores Discord |
| `linkedin-cli` | LinkedIn — scraping de perfiles y automatización | Investigación de candidatos/empresas |
| `reddit` | Reddit lectura via JSON endpoints y PRAW | Monitorear hilos y subreddits |
| `slack` | Slack SDK, webhooks, file uploads, eventos | Notificaciones y bots de Slack |

### 15. 🆕 Hugging Face — Oficial (5 skills)

> **Fuente:** [huggingface/skills](https://github.com/huggingface/skills) — Skills especializadas en ML/AI. Compatible con Claude Code, Codex, Gemini CLI, Cursor.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `hf-cli` | CLI de Hugging Face: auth, repos, upload/download | Gestionar modelos y datasets en HF Hub |
| `hf-datasets` | Crear y gestionar datasets en HF Hub | Preparar datos para entrenamiento ML |
| `hf-trainer` | Entrenamiento de modelos con Trainer API | Fine-tuning, LoRA/QLoRA, distributed training |
| `hf-evaluation` | Evaluación estandarizada de modelos | Benchmarks, métricas, comparación de modelos |
| `hf-jobs` | Orquestación de jobs en infraestructura HF | Inference Endpoints, AutoTrain, Spaces |

### 16. 🆕 OpenAI Codex (6 skills)

> **Fuente:** [openai/skills](https://github.com/openai/skills) — Skills del ecosistema Codex (CLI, IDE, Desktop App). Tres niveles: System, Curated, Experimental.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `codex-cli` | Dominio de Codex CLI con GPT-5.2 | Generación de código, scaffolding, edición |
| `codex-multi-agent` | Arquitectura multi-agente (Desktop App Feb 2026) | Tests + refactoring + docs en paralelo |
| `codex-skill-installer` | `$skill-installer` y `$skill-creator` | Instalar, gestionar y crear skills para Codex |
| `codex-pr-creator` | Creación automática de PRs con validación CI | PRs con conventional commits y ticket linking |
| `codex-react-linter` | React Code Fix & Linter (242K ⭐ MCP Market) | Formateo, linting, calidad React |
| `codex-prompt-enhancer` | Prompt Finder & Enhancer (144K accesos) | Optimizar prompts con contexto de proyecto |

### 17. 🆕 Block/Goose — Enterprise (5 skills)

> **Fuente:** [block/agent-skills](https://github.com/block/agent-skills) — Skills enterprise de Block (ex-Square). Compatible con Goose, Claude Desktop, estándar SKILL.md.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `goose-workflows` | Workflows repetibles: deploy, release, migración | Pipelines de despliegue y migración |
| `goose-incident-response` | Respuesta a incidentes (P0-P4), RCA, post-mortem | Gestión de incidentes en producción |
| `goose-code-review` | Code review enterprise multi-dimensión | Revisar PRs con criterios de calidad |
| `goose-security-audit` | Auditoría OWASP, CVE, SOC 2, ISO 27001, PCI-DSS | Auditorías de seguridad y compliance |
| `goose-release-manager` | Releases end-to-end: semver, changelog, publish | Publicar releases profesionales |

### 18. 🆕 OpenClaw — Comunidad (6 skills)

> **Fuente:** [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) — Ecosistema OpenClaw (actualizado 7 feb 2026).

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `openclaw-memory` | Triple memoria: LanceDB + Git-Notes + File-based | Persistencia de contexto entre sesiones |
| `openclaw-security` | Seguridad de agentes: inyección, malware, audit | Proteger agentes autónomos |
| `openclaw-self-reflect` | Auto-mejora mediante análisis de conversaciones | Agentes que aprenden de sus errores |
| `openclaw-project-management` | Gestión de proyectos con task-observer | Planificación, sprints, tracking |
| `openclaw-messaging` | Mensajería multi-plataforma (Slack, Discord, etc.) | Integrar con plataformas de mensajería |
| `openclaw-reasoning` | Razonamiento avanzado (Equilibrium-Native) | Problemas complejos, decisiones difíciles |

### 19. 🆕 Testing y Calidad (5 skills)

> Skills de testing y calidad de código basadas en mejores prácticas de Anthropic, MCP Market y la comunidad.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `webapp-testing-playwright` | Testing E2E con Playwright multi-browser | Tests de aplicaciones web completas |
| `systematic-debugging` | Metodología estructurada de debugging | Diagnosticar y resolver bugs |
| `testing-anti-patterns` | Anti-patrones de testing y cómo evitarlos | Mejorar calidad de test suites |
| `code-quality-audit` | Auditoría de salud del codebase | Identificar deuda técnica |
| `tdd-bdd-patterns` | Patrones TDD y BDD con ejemplos prácticos | Desarrollo dirigido por tests |

### 20. 🆕 Orquestación Multi-Agente (5 skills)

> Patrones de orquestación inspirados en Codex Desktop App, n-skills orchestration y la comunidad.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `multi-agent-coordinator` | Coordinador central multi-agente | Orquestar múltiples agentes |
| `agent-specialization` | Configurar agentes especializados por dominio | Frontend, Backend, Security, DevOps agents |
| `task-decomposition` | Descomponer tareas complejas en subtareas | Planificación de trabajo complejo |
| `parallel-execution` | Ejecución paralela de tareas de agentes | Máxima productividad multi-agente |
| `open-source-maintainer` | Mantenimiento end-to-end de repos GitHub | Issues, PRs, releases, comunidad |

### 21. 🆕 Productividad y Herramientas (5 skills)

> Skills de productividad para el desarrollador moderno, basadas en tendencias de MCP Market y SkillsMP.

| Skill | Descripción | Cuándo usar |
|-------|-------------|-------------|
| `skill-writer` | Meta-skill que crea otras skills | Automatizar creación de SKILL.md |
| `codebase-health-reporter` | Reportes automáticos de salud del codebase | Auditorías de deuda técnica |
| `n8n-automation` | Integración con n8n workflows | Automatización de flujos de trabajo |
| `voxtral-transcription` | Transcripción Voxtral 2 (open-source, local) | Voz a texto, transcripción de reuniones |
| `prompt-finder-enhancer` | Biblioteca de 140K+ prompts + optimización | Encontrar y mejorar prompts |

---

## 🛠️ Cómo crear una nueva skill

Ver plantilla en [`_templates/SKILL-TEMPLATE.md`](_templates/SKILL-TEMPLATE.md)

Estructura básica:
```
skills/
└── mi-skill/
    ├── SKILL.md        ← OBLIGATORIO: Descripción + conocimiento
    └── examples/       ← OPCIONAL: Ejemplos de uso
        └── example-01.md
```

El `SKILL.md` debe empezar con frontmatter YAML:
```yaml
---
name: mi-skill
version: 1.0.0
description: Breve descripción de una línea. Cuándo el agente debe usarla.
tags: [categoria, herramienta, lenguaje]
author: garri333
license: MIT
---
```

### Criterios de calidad (basados en mejores prácticas de la industria)

| Criterio | Requisito |
|----------|-----------|
| **Enfoque** | Cada skill debe hacer UN solo trabajo bien |
| **Instrucciones** | Pasos imperativos con inputs y outputs explícitos |
| **Alcance** | Descripción clara de cuándo activar la skill |
| **Límites** | Casos de uso NO soportados claramente definidos |
| **Ejemplos** | Al menos 2-3 ejemplos de uso práctico |
| **Scripts** | Preferir instrucciones sobre scripts, salvo que se requiera comportamiento determinista |

---

## 📊 Estadísticas

| Categoría | Skills | Fuente |
|-----------|--------|--------|
| 01-10 Skills propias | 55 | Custom |
| 11 Científicas | 117 | K-Dense-AI |
| 12 Vercel Labs | 5 | Vercel Oficial |
| 13 Anthropic | 16 | Anthropic Oficial |
| 14 Social/Comms | 5 | Clawdbot-inspired |
| 15 Hugging Face 🆕 | 5 | HuggingFace Oficial |
| 16 OpenAI Codex 🆕 | 6 | OpenAI Oficial |
| 17 Block/Goose 🆕 | 5 | Block Enterprise |
| 18 OpenClaw 🆕 | 6 | OpenClaw Community |
| 19 Testing/Quality 🆕 | 5 | Multi-fuente |
| 20 Orchestration 🆕 | 5 | Multi-fuente |
| 21 Productivity 🆕 | 5 | Multi-fuente |
| **Total** | **245+** | **Multi-fuente** |

- **Categorías:** 21
- **Compatible con:** GitHub Copilot, Claude Code, Cursor, Codex CLI/Desktop, Cline, Windsurf, Aider, Goose
- **Fuentes:** anthropics/skills, openai/skills, huggingface/skills, block/agent-skills, VoltAgent/awesome-openclaw-skills, K-Dense-AI, vercel-labs, skills.sh, clawdbotskills.org, MCP Market, SkillsMP, n-skills

---

## 🔍 Dónde descubrir más skills

| Fuente | Skills | URL | Frecuencia recomendada |
|--------|--------|-----|------------------------|
| **anthropics/skills** | Oficiales | [github.com/anthropics/skills](https://github.com/anthropics/skills) | Diaria |
| **openai/skills** | Oficiales | [github.com/openai/skills](https://github.com/openai/skills) | Diaria |
| **huggingface/skills** | ML/AI | [github.com/huggingface/skills](https://github.com/huggingface/skills) | Semanal |
| **SkillsMP** | 66,541+ | [skillsmp.com](https://skillsmp.com) | Semanal |
| **MCP Market** | 31,000+ | [mcpmarket.com](https://mcpmarket.com) | Semanal |
| **skills.sh** | Directorio | [skills.sh](https://skills.sh) | Semanal |
| **Skills Directory** | 3,514+ verificadas | [skillsdirectory.com](https://skillsdirectory.com) | Mensual |
| **Block Agent Skills** | Enterprise | [block.github.io/goose/skills](https://block.github.io/goose/skills) | Mensual |
| **n-skills** | Curadas | [github.com/numman-ali/n-skills](https://github.com/numman-ali/n-skills) | Mensual |
| **Awesome Claude Skills** | Curadas | [awesomeclaude.ai](https://awesomeclaude.ai) | Mensual |
| **r/ClaudeAI** | Comunidad | [reddit.com/r/ClaudeAI](https://reddit.com/r/ClaudeAI) | Diaria |
| **r/ClaudeCode** | Técnico | [reddit.com/r/ClaudeCode](https://reddit.com/r/ClaudeCode) | Diaria |

---

## 🤝 Créditos y Fuentes

### Repositorios oficiales
- [anthropics/skills](https://github.com/anthropics/skills) — 14,300+ ⭐ Skills oficiales de Anthropic (estándar SKILL.md)
- [openai/skills](https://github.com/openai/skills) — Skills oficiales de OpenAI para Codex
- [huggingface/skills](https://github.com/huggingface/skills) — Skills de ML/AI de Hugging Face
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) — Skills oficiales de Vercel

### Repositorios empresariales y comunitarios
- [block/agent-skills](https://github.com/block/agent-skills) — Skills enterprise de Block/Goose
- [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) — Ecosistema OpenClaw
- [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) — 117 skills científicas
- [numman-ali/n-skills](https://github.com/numman-ali/n-skills) — Skills curadas + OpenSkills
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) — Awesome list curada
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — Integraciones enterprise
- [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) — Recursos LangChain

### Marketplaces y directorios
- [SkillsMP](https://skillsmp.com) — 66,541+ skills indexadas
- [MCP Market](https://mcpmarket.com) — 31,000+ skills con leaderboards
- [skills.sh](https://skills.sh) — Directorio con leaderboard de instalaciones
- [Skills Directory](https://skillsdirectory.com) — 3,514+ skills verificadas
- [clawdbotskills.org](https://clawdbotskills.org) — Marketplace de skills

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea tu skill siguiendo la plantilla en `_templates/`
3. Asegúrate de cumplir los [criterios de calidad](#criterios-de-calidad-basados-en-mejores-prácticas-de-la-industria)
4. Añádela en la categoría correcta
5. Actualiza este README
6. Pull Request

```
fork → branch feature → SKILL.md validado → pull request → merge
```

---

## 📝 Licencia

MIT — Libre para usar, modificar y distribuir.

Skills individuales pueden tener sus propias licencias (ver frontmatter de cada `SKILL.md`).

---

*Skills ecosystem powered by [skills.sh](https://skills.sh/) · Compatible con el [Agent Skills Standard](https://agentskills.io/) · Formato [SKILL.md](https://github.com/anthropics/skills) de Anthropic*

*Última actualización: Febrero 2026 · [garri333](https://github.com/garri333)*
