from typing import Any
from actions.terminal_control import terminal_control
from tools.base import BaseTool

class TerminalControlTool(BaseTool):
    name = "terminal_control"
    description = """Executes a command in the system terminal (PowerShell on Windows, Bash on Linux/Mac). Use this to launch applications via command line, start services like Ollama, run Python scripts, manage environments, or execute any system command requested by the user."""
    parameters = {'type': 'OBJECT', 'properties': {'command': {'type': 'STRING', 'description': 'The terminal command to execute'}, 'timeout': {'type': 'INTEGER', 'description': 'Timeout in seconds (default: 60)'}}, 'required': ['command']}

    def execute(self, args: dict, ui: Any) -> str:
        return terminal_control(parameters=args, player=ui) or 'Done.'
