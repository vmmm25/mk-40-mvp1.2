import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict

from services.skills.loader import load_skill_from_dir, DynamicSkillTool
from services.skills.updater import check_update, download_and_extract_skill
from tools import registry
import tools.declarations

logger = logging.getLogger(__name__)


class SkillManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SkillManager, cls).__new__(cls)
            return cls._instance

    def __init__(self, ui: Any = None):
        # Prevent re-initialization if already initialized
        if hasattr(self, "_initialized") and self._initialized:
            if ui is not None:
                self.ui = ui
            return

        self.ui = ui
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.skills_dir = self.base_dir / "habilidades"
        self.loaded_skills: Dict[str, DynamicSkillTool] = {}
        self._initialized = True

        # Ensure abilities directory exists
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def write_log(self, text: str):
        logger.info(text)
        if self.ui is not None:
            try:
                self.ui.write_log(text)
            except Exception as e:
                logger.error(f"Error writing to UI log: {e}")

    def scan_and_load(self):
        """Scans the habilidades/ directory and loads all valid skills."""
        self.write_log("SYS: Escaneando habilidades instaladas...")

        # Track loaded ones to see what changed
        current_loaded = list(self.loaded_skills.keys())
        for skill_name in current_loaded:
            self._unregister_skill(skill_name)

        loaded_count = 0

        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_") and not item.name.startswith("."):
                # Check if it has a skill.json
                if (item / "skill.json").exists():
                    try:
                        tool = load_skill_from_dir(item)
                        if tool:
                            self._register_skill(tool)
                            loaded_count += 1
                    except Exception as e:
                        logger.error(f"Failed to load skill from directory {item.name}: {e}")
                        self.write_log(f"SYS: Error al cargar habilidad desde {item.name}: {e}")

        self.write_log(f"SYS: {loaded_count} habilidad(es) cargada(s) con éxito.")

    def _register_skill(self, tool: DynamicSkillTool):
        """Registers the dynamic tool into the global registry and global lists."""
        self.loaded_skills[tool.skill_name] = tool

        # Register in the global registry
        registry._implementations[tool.name] = tool

        import tools
        if hasattr(tools, "TOOL_IMPLEMENTATIONS"):
            tools.TOOL_IMPLEMENTATIONS[tool.name] = tool.execute

        decl = {"name": tool.name, "description": tool.description, "parameters": tool.parameters}

        # Register declaration in ToolRegistry
        if not any(d["name"] == tool.name for d in registry._declarations):
            registry._declarations.append(decl)

        # Register declaration in tools.declarations
        if not any(d["name"] == tool.name for d in tools.declarations.TOOL_DECLARATIONS):
            tools.declarations.TOOL_DECLARATIONS.append(decl)

    def _unregister_skill(self, skill_name: str):
        """Unregisters a skill by its skill_name (from skill.json)."""
        if skill_name in self.loaded_skills:
            tool = self.loaded_skills[skill_name]
            del self.loaded_skills[skill_name]

            # Remove implementation
            if tool.name in registry._implementations:
                del registry._implementations[tool.name]

            import tools
            if hasattr(tools, "TOOL_IMPLEMENTATIONS") and tool.name in tools.TOOL_IMPLEMENTATIONS:
                del tools.TOOL_IMPLEMENTATIONS[tool.name]

            # Remove declarations
            registry._declarations = [d for d in registry._declarations if d["name"] != tool.name]

            import tools.declarations
            tools.declarations.TOOL_DECLARATIONS[:] = [
                d for d in tools.declarations.TOOL_DECLARATIONS if d["name"] != tool.name
            ]

    def _find_skill_dir(self, skill_name: str) -> Path | None:
        """Finds the directory of a skill matching the manifest's name."""
        for item in self.skills_dir.iterdir():
            if item.is_dir() and (item / "skill.json").exists():
                try:
                    with open(item / "skill.json", "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                        if manifest.get("name") == skill_name:
                            return item
                except Exception:
                    pass
        return None

    def install_skill(self, github_repo: str) -> str:
        """Downloads and installs/updates a skill from a GitHub repository."""
        # Check repo format (owner/repo)
        github_repo = github_repo.strip()
        # Handle full url or short format
        if "github.com/" in github_repo:
            github_repo = github_repo.split("github.com/")[-1]

        parts = github_repo.split("/")
        if len(parts) < 2:
            return f"Formato de repositorio inválido: {github_repo}. Debe ser 'usuario/repositorio' o URL de GitHub."

        owner = parts[-2]
        repo = parts[-1].replace(".git", "")
        clean_repo = f"{owner}/{repo}"

        folder_name = f"{owner}__{repo}".lower()
        dest_dir = self.skills_dir / folder_name

        self.write_log(f"SYS: Descargando e instalando habilidad '{clean_repo}'...")

        # Download and extract
        sha = download_and_extract_skill(clean_repo, dest_dir)
        if sha:
            # Re-scan and load
            self.scan_and_load()
            return f"Habilidad '{clean_repo}' instalada y cargada con éxito (commit: {sha[:7]})."
        else:
            return f"Error al descargar o instalar la habilidad '{clean_repo}'."

    def update_skill(self, skill_name: str) -> str:
        """Updates a specific skill if an update is available."""
        skill_dir = self._find_skill_dir(skill_name)
        if not skill_dir:
            return f"No se encontró la habilidad '{skill_name}' instalada."

        # Read github_repo from manifest
        try:
            with open(skill_dir / "skill.json", "r", encoding="utf-8") as f:
                manifest = json.load(f)
                github_repo = manifest.get("github_repo")
        except Exception as e:
            return f"Error leyendo manifiesto para '{skill_name}': {e}"

        if not github_repo:
            return f"La habilidad '{skill_name}' no define un repositorio de GitHub para actualizar."

        self.write_log(f"SYS: Actualizando habilidad '{skill_name}'...")
        sha = download_and_extract_skill(github_repo, skill_dir)
        if sha:
            self.scan_and_load()
            return f"Habilidad '{skill_name}' actualizada con éxito al commit {sha[:7]}."
        else:
            return f"Error al actualizar la habilidad '{skill_name}'."

    def remove_skill(self, skill_name: str) -> str:
        """Removes a skill from disk and unregisters it."""
        skill_dir = self._find_skill_dir(skill_name)
        if not skill_dir:
            return f"No se encontró la habilidad '{skill_name}' instalada."

        import shutil
        try:
            self._unregister_skill(skill_name)
            shutil.rmtree(skill_dir)
            return f"Habilidad '{skill_name}' eliminada con éxito."
        except Exception as e:
            logger.error(f"Failed to delete skill directory {skill_dir}: {e}")
            return f"Error al eliminar la habilidad '{skill_name}' del disco: {e}"

    def check_updates_background(self):
        """Checks for updates for all installed skills in a separate thread."""

        def check_runner():
            time.sleep(5)  # Wait for startup to settle
            self.write_log("SYS: Verificando actualizaciones de habilidades...")

            for item in self.skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_") and not item.name.startswith("."):
                    if (item / "skill.json").exists() and (item / ".git_state.json").exists():
                        try:
                            with open(item / "skill.json", "r", encoding="utf-8") as f:
                                manifest = json.load(f)
                            with open(item / ".git_state.json", "r", encoding="utf-8") as f:
                                git_state = json.load(f)

                            github_repo = manifest.get("github_repo")
                            current_sha = git_state.get("last_commit_sha")
                            skill_name = manifest.get("name")

                            if github_repo and current_sha:
                                res = check_update(github_repo, current_sha)
                                if res.get("update_available"):
                                    self.write_log(
                                        f"SYS: [Update] Habilidad '{skill_name}' tiene una actualización disponible en GitHub ({github_repo})."
                                    )
                        except Exception as e:
                            logger.error(f"Error checking update for {item.name}: {e}")

        threading.Thread(target=check_runner, daemon=True).start()
