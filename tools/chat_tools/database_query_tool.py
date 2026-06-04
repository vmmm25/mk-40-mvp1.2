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

class DatabaseQueryTool(BaseTool):
    name = "database_query"
    description = """Execute SQL queries on configured databases (PostgreSQL or MySQL)."""
    parameters = {'type': 'OBJECT', 'properties': {'connection': {'type': 'STRING', 'description': "Connection name from config (e.g. 'local_postgres', 'project_db')"}, 'query': {'type': 'STRING', 'description': 'SQL query to execute'}}, 'required': ['connection', 'query']}

    def execute(self, args: dict, ui: Any) -> str:
        connection = args.get('connection', '')
        query = args.get('query', '')
        if not connection or not query:
            return "Both 'connection' and 'query' parameters are required."
        try:
            from services.database.db_client import DatabaseClient
            db = DatabaseClient()
        except Exception as e:
            return f'Error initialising database client: {e}'
        if not db.is_configured(connection):
            available = db.list_connections()
            if not available:
                return f'No databases configured. Create config/database_connections.json with connection details.'
            return f"Unknown connection '{connection}'. Available: {', '.join(available)}"
        try:
            result = db.execute_query(connection, query)
            if not result.get('success'):
                return f"Query error: {result.get('error', 'Unknown error')}"
            if 'columns' in result:
                cols = result['columns']
                rows = result['rows']
                header = ' | '.join((str(c) for c in cols))
                separator = '-' * len(header)
                lines = [header, separator]
                for row in rows[:50]:
                    lines.append(' | '.join((str(v) for v in row)))
                if len(rows) > 50:
                    lines.append(f'... and {len(rows) - 50} more rows')
                lines.append(f"({result.get('row_count', len(rows))} rows returned)")
                return '\n'.join(lines)
            else:
                return f"Query executed. {result.get('affected_rows', 0)} rows affected."
        except Exception as e:
            return f'Database error: {e}'
