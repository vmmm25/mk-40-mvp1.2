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

class GameUpdaterTool(BaseTool):
    name = "game_updater"
    description = """THE ONLY tool for ANY Steam or Epic Games request. Use for: installing, downloading, updating games, listing installed games, checking download status, scheduling updates. ALWAYS call directly for any Steam/Epic/game request. NEVER use agent_task, browser_control, or web_search for Steam/Epic."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'update | install | list | download_status | schedule | cancel_schedule | schedule_status (default: update)'}, 'platform': {'type': 'STRING', 'description': 'steam | epic | both (default: both)'}, 'game_name': {'type': 'STRING', 'description': 'Game name (partial match supported)'}, 'app_id': {'type': 'STRING', 'description': 'Steam AppID for install (optional)'}, 'hour': {'type': 'INTEGER', 'description': 'Hour for scheduled update 0-23 (default: 3)'}, 'minute': {'type': 'INTEGER', 'description': 'Minute for scheduled update 0-59 (default: 0)'}, 'shutdown_when_done': {'type': 'BOOLEAN', 'description': 'Shut down PC when download finishes'}}, 'required': []}

    def execute(self, args: dict, ui: Any) -> str:
        return game_updater(parameters=args, player=ui, speak=None) or 'Done.'
