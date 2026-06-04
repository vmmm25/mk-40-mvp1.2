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

class BrowserControlTool(BaseTool):
    name = "browser_control"
    description = """Controls any web browser. Use for: opening websites, searching the web, clicking elements, filling forms, scrolling, screenshots, navigation, any web-based task. Always pass the 'browser' parameter when the user specifies a browser (e.g. 'open in Edge', 'use Firefox', 'open Chrome'). Multiple browsers can run simultaneously."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'go_to | search | click | type | scroll | fill_form | smart_click | smart_type | get_text | get_url | press | new_tab | close_tab | screenshot | back | forward | reload | switch | list_browsers | close | close_all'}, 'browser': {'type': 'STRING', 'description': 'Target browser: chrome | edge | firefox | opera | operagx | brave | vivaldi | safari. Omit to use the currently active browser.'}, 'url': {'type': 'STRING', 'description': 'URL for go_to / new_tab action'}, 'query': {'type': 'STRING', 'description': 'Search query for search action'}, 'engine': {'type': 'STRING', 'description': 'Search engine: google | bing | duckduckgo | yandex (default: google)'}, 'selector': {'type': 'STRING', 'description': 'CSS selector for click/type'}, 'text': {'type': 'STRING', 'description': 'Text to click or type'}, 'description': {'type': 'STRING', 'description': 'Element description for smart_click/smart_type'}, 'direction': {'type': 'STRING', 'description': 'up | down for scroll'}, 'amount': {'type': 'INTEGER', 'description': 'Scroll amount in pixels (default: 500)'}, 'key': {'type': 'STRING', 'description': 'Key name for press action (e.g. Enter, Escape, F5)'}, 'path': {'type': 'STRING', 'description': 'Save path for screenshot'}, 'incognito': {'type': 'BOOLEAN', 'description': 'Open in private/incognito mode'}, 'clear_first': {'type': 'BOOLEAN', 'description': 'Clear field before typing (default: true)'}}, 'required': ['action']}

    def execute(self, args: dict, ui: Any) -> str:
        return browser_control(parameters=args, player=ui) or 'Done.'
