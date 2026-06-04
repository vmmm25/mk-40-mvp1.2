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

class PlayMusicTool(BaseTool):
    name = "play_music"
    description = """Control Spotify music playback: play, pause, next, previous, search, playlist, volume, and info."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'play | pause | next | previous | search | playlist | volume | info'}, 'query': {'type': 'STRING', 'description': 'Song/artist/playlist name for search/play action'}, 'volume': {'type': 'INTEGER', 'description': 'Volume level 0-100 for volume action'}}, 'required': ['action']}

    def execute(self, args: dict, ui: Any) -> str:
        action = args.get('action', '')
        query = args.get('query', '')
        volume = args.get('volume')
        try:
            from services.media.spotify_client import SpotifyClient
            client = SpotifyClient()
        except ImportError:
            return 'Spotify client not available (spotipy not installed).'
        except Exception as e:
            return f'Error initialising Spotify: {e}'
        if not client.is_authenticated():
            return 'Spotify not configured. Please create config/spotify_credentials.json with your Spotify client_id, client_secret, and redirect_uri.'
        try:
            if action == 'play':
                return client.play(query=query)
            elif action == 'pause':
                return client.pause()
            elif action == 'next':
                return client.next_track()
            elif action == 'previous':
                return client.previous_track()
            elif action == 'volume':
                if volume is None:
                    return 'Volume parameter required.'
                return client.set_volume(int(volume))
            elif action == 'info':
                info = client.current_playback()
                if 'error' in info:
                    return f"Spotify error: {info['error']}"
                if 'message' in info:
                    return info['message']
                return f"Now playing: {info['track']} by {info['artists']} ({info.get('album', '')})"
            elif action == 'search':
                if not query:
                    return 'Query parameter required for search.'
                results = client.search(query=query)
                if not results:
                    return f"No results found for '{query}'."
                lines = [f"{r['name']} — {r.get('artists', '')}" for r in results]
                return 'Search results:\n' + '\n'.join(lines)
            else:
                return f'Unknown action: {action}. Use: play, pause, next, previous, volume, info, search.'
        except Exception as e:
            return f'Spotify error: {e}'
