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

class AgentTaskTool(BaseTool):
    name = "agent_task"
    description = """Executes complex multi-step tasks requiring multiple different tools. Examples: 'research X and save to file', 'find and organize files'. DO NOT use for single commands. NEVER use for Steam/Epic — use game_updater."""
    parameters = {'type': 'OBJECT', 'properties': {'goal': {'type': 'STRING', 'description': 'Complete description of what to accomplish'}, 'priority': {'type': 'STRING', 'description': 'low | normal | high (default: normal)'}}, 'required': ['goal']}

    def execute(self, args: dict, ui: Any) -> str:
        priority_map = {'low': TaskPriority.LOW, 'normal': TaskPriority.NORMAL, 'high': TaskPriority.HIGH}
        priority = priority_map.get(args.get('priority', 'normal').lower(), TaskPriority.NORMAL)
        get_queue().submit(goal=args.get('goal', ''), priority=priority, speak=None)
        return f"Task '{args.get('goal', '')[:60]}' queued."
