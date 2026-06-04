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

class SaveMemoryTool(BaseTool):
    name = "save_memory"
    description = """Save an important personal fact about the user to long-term memory. Call this silently whenever the user reveals something worth remembering: name, age, city, job, preferences, hobbies, relationships, projects, or future plans. Do NOT call for: weather, reminders, searches, or one-time commands. Do NOT announce that you are saving — just call it silently. Values must be in English regardless of the conversation language."""
    parameters = {'type': 'OBJECT', 'properties': {'category': {'type': 'STRING', 'description': 'identity — name, age, birthday, city, job, language, nationality | preferences — favorite food/color/music/film/game/sport, hobbies | projects — active projects, goals, things being built | relationships — friends, family, partner, colleagues | wishes — future plans, things to buy, travel dreams | notes — habits, schedule, anything else worth remembering'}, 'key': {'type': 'STRING', 'description': 'Short snake_case key (e.g. name, favorite_food, sister_name)'}, 'value': {'type': 'STRING', 'description': 'Concise value in English (e.g. Ana, pizza, older sister)'}}, 'required': ['category', 'key', 'value']}

    def execute(self, args: dict, ui: Any) -> str:
        if args.get('key') and args.get('value'):
            update_memory({args.get('category', 'notes'): {args.get('key', ''): {'value': args.get('value', '')}}})
        return 'Memory saved.'
