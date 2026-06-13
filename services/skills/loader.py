import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any
from tools.base import BaseTool

logger = logging.getLogger(__name__)


class DynamicSkillTool(BaseTool):
    """Wrapper that wraps a dynamically loaded python module function as a BaseTool."""

    def __init__(self, name: str, description: str, parameters: dict, execute_fn: Any, skill_name: str, skill_dir: Path):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.execute_fn = execute_fn
        self.skill_name = skill_name
        self.skill_dir = skill_dir

    def execute(self, args: dict, ui: Any) -> str:
        # Temporarily append skill directory to sys.path to allow internal imports
        skill_dir_str = str(self.skill_dir.resolve())
        added_to_path = False
        if skill_dir_str not in sys.path:
            sys.path.insert(0, skill_dir_str)
            added_to_path = True
            
        try:
            res = self.execute_fn(args, ui)
            return str(res) if res is not None else "Done."
        except Exception as e:
            logger.exception(f"Error executing dynamic skill {self.name} ({self.skill_name})")
            return f"Error executing skill {self.name}: {e}"
        finally:
            if added_to_path:
                try:
                    sys.path.remove(skill_dir_str)
                except ValueError:
                    pass


def load_skill_from_dir(skill_dir: Path) -> DynamicSkillTool | None:
    """Read skill.json, dynamically import entry point, and return a DynamicSkillTool."""
    manifest_path = skill_dir / "skill.json"
    if not manifest_path.exists():
        logger.warning(f"No skill.json found in {skill_dir}")
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read skill.json in {skill_dir}: {e}")
        return None

    # Validate manifest
    required_fields = ["name", "entry_point", "tool_name", "tool_description", "tool_parameters"]
    for field in required_fields:
        if field not in manifest:
            logger.error(f"Missing required field '{field}' in skill.json at {skill_dir}")
            return None

    entry_point_file = skill_dir / manifest["entry_point"]
    if not entry_point_file.exists():
        logger.error(f"Entry point file {entry_point_file} not found for skill {manifest['name']}")
        return None

    # Add skill directory to sys.path during import
    skill_dir_str = str(skill_dir.resolve())
    added_to_path = False
    if skill_dir_str not in sys.path:
        sys.path.insert(0, skill_dir_str)
        added_to_path = True

    try:
        # Load module dynamically
        module_name = f"dynamic_skill_{manifest['name']}"
        spec = importlib.util.spec_from_file_location(module_name, str(entry_point_file))
        if spec is None or spec.loader is None:
            logger.error(f"Could not load spec for {entry_point_file}")
            return None

        module = importlib.util.module_from_spec(spec)
        # Make the module discoverable in sys.modules
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find entry function
        tool_name = manifest["tool_name"]
        execute_fn = None

        # Check priority names
        for fn_name in ["execute", "handler", tool_name]:
            if hasattr(module, fn_name) and callable(getattr(module, fn_name)):
                execute_fn = getattr(module, fn_name)
                break

        if execute_fn is None:
            # Fallback: find any callable that doesn't start with underscore
            callables = [
                getattr(module, a)
                for a in dir(module)
                if not a.startswith("_") and callable(getattr(module, a))
            ]
            if callables:
                execute_fn = callables[0]

        if execute_fn is None:
            logger.error(f"No callable function found in entry point {entry_point_file} for skill {manifest['name']}")
            return None

        tool = DynamicSkillTool(
            name=tool_name,
            description=manifest["tool_description"],
            parameters=manifest["tool_parameters"],
            execute_fn=execute_fn,
            skill_name=manifest["name"],
            skill_dir=skill_dir
        )
        logger.info(f"Loaded skill tool '{tool_name}' from {skill_dir}")
        return tool
    except Exception as e:
        logger.exception(f"Error importing skill module {manifest['name']} from {entry_point_file}")
        return None
    finally:
        if added_to_path:
            try:
                sys.path.remove(skill_dir_str)
            except ValueError:
                pass
