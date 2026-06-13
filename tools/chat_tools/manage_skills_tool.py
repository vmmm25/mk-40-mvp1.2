import json
from typing import Any
from tools.base import BaseTool


class ManageSkillsTool(BaseTool):
    name = "manage_skills"
    description = "Manages JARVIS skills (habilidades). Allows listing, installing, updating, or removing skills."
    parameters = {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "The action to perform: 'list', 'install', 'update', or 'remove'",
                "enum": ["list", "install", "update", "remove"],
            },
            "github_repo": {
                "type": "STRING",
                "description": "The GitHub repository to install (e.g. 'owner/repo' or URL). Required if action is 'install'.",
            },
            "skill_name": {
                "type": "STRING",
                "description": "The name of the skill to update or remove. Required if action is 'update' or 'remove'.",
            },
        },
        "required": ["action"],
    }

    def execute(self, args: dict, ui: Any) -> str:
        from services.skills.manager import SkillManager

        action = args.get("action")
        github_repo = args.get("github_repo")
        skill_name = args.get("skill_name")

        manager = SkillManager(ui)

        if action == "list":
            skills = manager.loaded_skills
            if not skills:
                return "No hay habilidades (skills) cargadas."

            res = "Habilidades instaladas:\n"
            for name, tool in skills.items():
                version = "desconocida"
                repo_url = "local"

                # Try to read info from skill.json
                skill_dir = tool.skill_dir
                if (skill_dir / "skill.json").exists():
                    try:
                        with open(skill_dir / "skill.json", "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                            version = manifest.get("version", version)
                            repo_url = manifest.get("github_repo", repo_url)
                    except Exception:
                        pass

                res += f"- **{name}** (v{version}) - Repo: {repo_url} - Herramienta: `{tool.name}`\n"
            return res

        elif action == "install":
            if not github_repo:
                return "Error: Se requiere el parámetro 'github_repo' para la acción 'install'."
            return manager.install_skill(github_repo)

        elif action == "update":
            if not skill_name:
                return "Error: Se requiere el parámetro 'skill_name' para la acción 'update'."
            if skill_name == "all":
                # Special case: update all
                results = []
                for name in list(manager.loaded_skills.keys()):
                    res = manager.update_skill(name)
                    results.append(f"{name}: {res}")
                return "\n".join(results) if results else "No hay habilidades instaladas para actualizar."
            return manager.update_skill(skill_name)

        elif action == "remove":
            if not skill_name:
                return "Error: Se requiere el parámetro 'skill_name' para la acción 'remove'."
            return manager.remove_skill(skill_name)

        else:
            return f"Acción desconocida: {action}"
