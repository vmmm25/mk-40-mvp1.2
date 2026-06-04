from typing import Any, Callable
from tools.base import BaseTool
import json
import os
import subprocess
import threading
import time

import os
import time
import threading
from typing import Callable, Any
from actions.file_processor import file_processor
from actions.flight_finder import flight_finder
from actions.open_app import open_app
from actions.weather_report import weather_action
from actions.send_message import send_message
from actions.reminder import reminder
from actions.computer_settings import computer_settings
from actions.screen_processor import screen_process
from actions.youtube_video import youtube_video
from actions.desktop import desktop_control
from actions.browser_control import browser_control
from actions.file_controller import file_controller
from actions.code_helper import code_helper
from actions.dev_agent import dev_agent
from actions.web_search import web_search as web_search_action
from actions.computer_control import computer_control
from actions.game_updater import game_updater
from actions.terminal_control import terminal_control
from agent.task_queue import get_queue, TaskPriority
from memory.memory_manager import update_memory
from memory.config_manager import get_os_system
import asyncio
import os
from pathlib import Path

class ShutdownJarvisTool(BaseTool):
    name = "shutdown_jarvis"
    description = """Shuts down the assistant completely. Call this when the user expresses intent to end the conversation, close the assistant, say goodbye, or stop Jarvis. The user can say this in ANY language."""
    parameters = {'type': 'OBJECT', 'properties': {}}

    def execute(self, args: dict, ui: Any) -> str:
        ui.write_log('SYS: Shutdown requested.')
        try:
            import main
            main._engine_stop.set()
        except Exception:
            pass
    
        def _delayed_exit():
            time.sleep(1.5)
            try:
                ui.root.quit()
            except Exception:
                os._exit(0)
        threading.Thread(target=_delayed_exit, daemon=True).start()
        return 'Goodbye, sir.'
