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

class GitOperationTool(BaseTool):
    name = "git_operation"
    description = """Perform Git operations: status, commit, push, pull, branch, log, diff, clone, add, checkout, merge."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'status | commit | push | pull | branch | log | diff | clone | add | checkout | merge'}, 'path': {'type': 'STRING', 'description': 'Repository path (default: current project)'}, 'message': {'type': 'STRING', 'description': 'Commit message'}, 'branch': {'type': 'STRING', 'description': 'Branch name'}, 'url': {'type': 'STRING', 'description': 'Repository URL for clone'}}, 'required': ['action']}

    def execute(self, args: dict, ui: Any) -> str:
        action = args.get('action', '')
        path = args.get('path', '')
        message = args.get('message', '')
        branch = args.get('branch', '')
        url = args.get('url', '')
        try:
            from services.git.git_client import GitClient
            repo_path = path if path else None
            git = GitClient(repo_path=repo_path)
        except Exception as e:
            return f'Error initialising Git client: {e}'
        try:
            if action == 'status':
                return git.status()
            elif action == 'log':
                return git.log()
            elif action == 'diff':
                return git.diff()
            elif action == 'add':
                return git.add('.') if not message else git.add(message)
            elif action == 'commit':
                if not message:
                    return 'Commit message required.'
                return git.commit(message)
            elif action == 'push':
                return git.push(branch=branch or None)
            elif action == 'pull':
                return git.pull(branch=branch or None)
            elif action == 'branch':
                return git.branch(name=branch or None)
            elif action == 'checkout':
                if not branch:
                    return 'Branch name required for checkout.'
                return git.checkout(branch)
            elif action == 'merge':
                if not branch:
                    return 'Branch name required for merge.'
                return git.merge(branch)
            elif action == 'clone':
                if not url:
                    return 'URL required for clone.'
                return git.clone(url, path or None)
            else:
                return f'Unknown git action: {action}'
        except Exception as e:
            return f'Git error: {e}'
