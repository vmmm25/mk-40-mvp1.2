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

class SearchDocumentsTool(BaseTool):
    name = "search_documents"
    description = """Searches the personal document database (RAG) for information. Use this when the user asks about their own documents, files, or previously indexed information."""
    parameters = {'type': 'OBJECT', 'properties': {'query': {'type': 'STRING', 'description': 'The search query'}, 'n_results': {'type': 'INTEGER', 'description': 'Number of results to return (default: 5)'}}, 'required': ['query']}

    def execute(self, args: dict, ui: Any) -> str:
        query = args.get('query', '')
        n_results = args.get('n_results', 5)
        if not query:
            return 'No query provided.'
        try:
            from rag.retriever import DocumentRetriever
            retriever = DocumentRetriever()
            results = retriever.search(query, n_results=n_results)
            if not results:
                return 'No results found in the document database.'
            formatted = [f"- {r['text']} (Source: {r['metadata'].get('source', 'Unknown')}, Page {r['metadata'].get('page', 1)})" for r in results]
            return '\n'.join(formatted)
        except Exception as e:
            return f'Error searching documents: {e}'
