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

class GenerateImageTool(BaseTool):
    name = "generate_image"
    description = """Generate an image from a text description using AI. Supports local SD, Gemini, or DALL-E via OpenRouter."""
    parameters = {'type': 'OBJECT', 'properties': {'prompt': {'type': 'STRING', 'description': 'Detailed description of the image to generate'}, 'style': {'type': 'STRING', 'description': 'Art style: realistic | anime | cyberpunk | oil_painting | watercolor | pixel_art'}, 'size': {'type': 'STRING', 'description': 'Image size: 512x512 | 1024x1024 | 1024x768 (default: 1024x1024)'}, 'save': {'type': 'BOOLEAN', 'description': 'Save to desktop (default: true)'}, 'count': {'type': 'INTEGER', 'description': 'Number of images (default: 1, max: 4)'}, 'backend': {'type': 'STRING', 'description': 'Generation backend: local | gemini | openai (default: auto — tries local first)'}}, 'required': ['prompt']}

    def execute(self, args: dict, ui: Any) -> str:
        prompt = args.get('prompt', '')
        style = args.get('style')
        size = args.get('size', '1024x1024')
        count = args.get('count', 1)
        save = args.get('save', True)
        backend = args.get('backend', 'auto')
        if not prompt:
            return 'No prompt provided.'
    
        async def _generate():
            backends = []
            if backend == 'auto':
                backends = ['local', 'gemini', 'openai']
            else:
                backends = [backend]
            for name in backends:
                try:
                    if name == 'local':
                        from services.image_gen.local_sd import StableDiffusionLocal
                        gen = StableDiffusionLocal()
                        if gen.is_available():
                            images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                            if images:
                                return ('local', images)
                    elif name == 'gemini':
                        from services.image_gen.gemini_gen import GeminiImageGen
                        gen = GeminiImageGen()
                        if gen.is_available():
                            images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                            if images:
                                return ('gemini', images)
                    elif name == 'openai':
                        from services.image_gen.openai_gen import OpenAIImageGen
                        gen = OpenAIImageGen()
                        if gen.is_available():
                            images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                            if images:
                                return ('openai', images)
                except Exception as e:
                    logger = __import__('logging').getLogger(__name__)
                    logger.warning('Image backend %s failed: %s', name, e)
                    continue
            return (None, [])
        try:
            backend_name, images = asyncio.run(_generate())
            if not images:
                return 'No images could be generated. Make sure at least one backend is available (local SD, Gemini, or OpenRouter).'
            if save:
                desk = Path(os.environ.get('USERPROFILE', '.')) / 'Desktop'
                saved = []
                for i, img_bytes in enumerate(images):
                    ts = __import__('time').strftime('%Y%m%d_%H%M%S')
                    fname = f'jarvis_gen_{ts}_{i}.png'
                    fpath = desk / fname
                    fpath.write_bytes(img_bytes)
                    saved.append(str(fpath))
                return f'Generated {len(images)} image(s) via {backend_name}.\nSaved to:\n' + '\n'.join(saved)
            return f'Generated {len(images)} image(s) via {backend_name}.'
        except Exception as e:
            return f'Error generating images: {e}'
