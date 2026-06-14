"""Tools for installing and searching SKILL.md repositories (garri333/Skills ecosystem)."""
from typing import Any
from tools.base import BaseTool


class SearchSkillMdTool(BaseTool):
    name = "search_skill_md"
    description = """Searches the SKILL.md skill library for agentic capabilities, domain expertise, and reusable skill patterns. Use this when the user asks about specific skills, capabilities, or when you need specialized knowledge from the skill ecosystem."""
    parameters = {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query for skills (e.g. 'python testing', 'react patterns', 'security')",
            },
            "n_results": {
                "type": "INTEGER",
                "description": "Number of results to return (default: 5)",
            },
        },
        "required": ["query"],
    }

    def execute(self, args: dict, ui: Any) -> str:
        query = args.get("query", "")
        n_results = args.get("n_results", 5)
        if not query:
            return "No query provided."

        try:
            from services.skills.md_adapter import SkillMdIndexer
            indexer = SkillMdIndexer()
            results = indexer.search(query, n_results=n_results)
            if not results:
                return (
                    "No se encontraron skills. Primero instalá un repositorio SKILL.md con 'install_skill_md_repo'.\n"
                    "Repos disponibles: garri333/Skills (245+ skills), javiertarazon/agente-copilot (963 skills)"
                )

            lines = [f"🔧 Skills encontradas ({len(results)}):"]
            for i, r in enumerate(results, 1):
                meta = r["metadata"]
                name = meta.get("name", "?")
                desc = meta.get("description", "")
                trigger = meta.get("trigger", "")
                tags = meta.get("tags", "")
                repo = meta.get("github_repo", "")

                lines.append(f"\n--- Skill {i}: {name} ---")
                if desc:
                    lines.append(f"Descripción: {desc}")
                if trigger:
                    lines.append(f"Trigger: {trigger}")
                if tags:
                    lines.append(f"Tags: {tags}")
                if repo:
                    lines.append(f"Repo: {repo}")
                lines.append(r["text"][:300])
                if len(r["text"]) > 300:
                    lines.append("... (truncado)")

            return "\n".join(lines)
        except Exception as e:
            return f"Error searching skills: {e}"


class InstallSkillMdRepoTool(BaseTool):
    name = "install_skill_md_repo"
    description = """Downloads a SKILL.md-style GitHub repository and indexes all its skills into the skill library for semantic search. Supports the garri333/Skills ecosystem."""
    parameters = {
        "type": "OBJECT",
        "properties": {
            "github_repo": {
                "type": "STRING",
                "description": "GitHub repository in 'owner/repo' format (e.g. 'garri333/Skills', 'javiertarazon/agente-copilot')",
            },
        },
        "required": ["github_repo"],
    }

    def execute(self, args: dict, ui: Any) -> str:
        github_repo = args.get("github_repo", "").strip()
        if not github_repo:
            return "Error: Se requiere el parámetro 'github_repo'."

        if "github.com/" in github_repo:
            github_repo = github_repo.split("github.com/")[-1]
        parts = github_repo.split("/")
        if len(parts) < 2:
            return f"Formato inválido: {github_repo}. Debe ser 'owner/repo'."
        owner = parts[-2]
        repo = parts[-1].replace(".git", "")
        clean_repo = f"{owner}/{repo}"

        try:
            from services.skills.md_adapter import SkillMdIndexer
            indexer = SkillMdIndexer()
            result = indexer.install_repo(clean_repo)

            total = indexer.count()
            result += f"\n\nTotal en colección: {total} skills indexadas."

            return result
        except Exception as e:
            return f"Error al instalar repositorio SKILL.md: {e}"
