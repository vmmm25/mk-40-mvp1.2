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

class FileProcessorTool(BaseTool):
    name = "file_processor"
    description = """Processes any file that the user has uploaded or dropped onto the interface. Use this when the user refers to an uploaded file and wants an action on it. Supports: images (describe/ocr/resize/compress/convert), PDFs (summarize/extract_text/to_word), Word docs & text files (summarize/fix/reformat/translate), CSV/Excel (analyze/stats/filter/sort/convert), JSON/XML (validate/format/analyze), code files (explain/review/fix/optimize/run/document/test), audio (transcribe/trim/convert/info), video (trim/extract_audio/extract_frame/compress/transcribe/info), archives (list/extract), presentations (summarize/extract_text). ALWAYS call this tool when a file has been uploaded and the user gives a command about it. If the user's command is ambiguous, pick the most logical action for that file type."""
    parameters = {'type': 'OBJECT', 'properties': {'file_path': {'type': 'STRING', 'description': 'Full path to the uploaded file. Leave empty to use the currently uploaded file.'}, 'action': {'type': 'STRING', 'description': 'What to do with the file. Examples by type:\nimage: describe | ocr | resize | compress | convert | info\npdf: summarize | extract_text | to_word | info\ndocx/txt: summarize | fix | reformat | translate_hint | word_count | to_bullet\ncsv/excel: analyze | stats | filter | sort | convert | info\njson: validate | format | analyze | to_csv\ncode: explain | review | fix | optimize | run | document | test\naudio: transcribe | trim | convert | info\nvideo: trim | extract_audio | extract_frame | compress | transcribe | info | convert\narchive: list | extract\npptx: summarize | extract_text | analyze'}, 'instruction': {'type': 'STRING', 'description': "Free-form instruction if action doesn't cover it. E.g. 'translate this to Turkish', 'find all email addresses'"}, 'format': {'type': 'STRING', 'description': "Target format for conversion. E.g. 'mp3', 'pdf', 'csv', 'png'"}, 'width': {'type': 'INTEGER', 'description': 'Target width for image resize'}, 'height': {'type': 'INTEGER', 'description': 'Target height for image resize'}, 'scale': {'type': 'NUMBER', 'description': 'Scale factor for image resize (e.g. 0.5)'}, 'quality': {'type': 'INTEGER', 'description': 'Quality 1-100 for image/video compress'}, 'start': {'type': 'STRING', 'description': 'Start time for trim: seconds or HH:MM:SS'}, 'end': {'type': 'STRING', 'description': 'End time for trim: seconds or HH:MM:SS'}, 'timestamp': {'type': 'STRING', 'description': 'Timestamp for video frame extraction HH:MM:SS'}, 'column': {'type': 'STRING', 'description': 'Column name for CSV filter/sort'}, 'value': {'type': 'STRING', 'description': 'Filter value for CSV filter'}, 'condition': {'type': 'STRING', 'description': 'Filter condition: equals|contains|gt|lt'}, 'ascending': {'type': 'BOOLEAN', 'description': 'Sort order for CSV sort (default: true)'}, 'save': {'type': 'BOOLEAN', 'description': 'Save result to file (default: true)'}, 'destination': {'type': 'STRING', 'description': 'Output folder for archive extract'}}, 'required': []}

    def execute(self, args: dict, ui: Any) -> str:
        if not args.get('file_path') and getattr(ui, 'current_file', None):
            params = {**args, 'file_path': ui.current_file}
            return file_processor(parameters=params, player=ui, speak=None) or 'Done.'
        return file_processor(parameters=args, player=ui, speak=None) or 'Done.'
