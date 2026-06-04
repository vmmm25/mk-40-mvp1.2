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

class SmartHomeTool(BaseTool):
    name = "smart_home"
    description = """Control smart home devices via Home Assistant API. Use for lights, thermostats, switches, and scenes."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'list_devices | turn_on | turn_off | set_temperature | get_status | scene'}, 'device': {'type': 'STRING', 'description': 'Device name or entity ID'}, 'value': {'type': 'STRING', 'description': "Value for set_temperature (e.g. '22')"}, 'scene': {'type': 'STRING', 'description': 'Scene name for scene action'}}, 'required': ['action']}

    def execute(self, args: dict, ui: Any) -> str:
        action = args.get('action', '')
        device = args.get('device', '')
        value = args.get('value', '')
        scene = args.get('scene', '')
        try:
            from memory.config_manager import get_config
            config = get_config()
            ha_url = config.get('home_assistant_url', '')
            ha_token = config.get('home_assistant_token', '')
        except Exception as e:
            return f'Config error: {e}'
        if not ha_url or not ha_token:
            return "Home Assistant not configured. Add 'home_assistant_url' and 'home_assistant_token' to config/api_keys.json."
        import requests
        ha_url = ha_url.rstrip('/')
        headers = {'Authorization': f'Bearer {ha_token}', 'Content-Type': 'application/json'}
        try:
            if action == 'list_devices':
                resp = requests.get(f'{ha_url}/api/states', headers=headers, timeout=10)
                if resp.status_code != 200:
                    return f'Error fetching devices: {resp.status_code}'
                states = resp.json()
                devices = [s for s in states if s['entity_id'].startswith(('light.', 'switch.', 'climate.', 'scene.', 'cover.'))]
                if not devices:
                    return 'No controllable devices found.'
                lines = []
                for d in devices:
                    state = d.get('state', '?')
                    attrs = d.get('attributes', {})
                    friendly = attrs.get('friendly_name', d['entity_id'])
                    lines.append(f"  {friendly} ({d['entity_id']}) — {state}")
                return 'Home Assistant devices:\n' + '\n'.join(lines)
            elif action in ('turn_on', 'turn_off'):
                if not device:
                    return 'Device entity_id required.'
                domain = device.split('.')[0] if '.' in device else 'homeassistant'
                service = 'turn_on' if action == 'turn_on' else 'turn_off'
                resp = requests.post(f'{ha_url}/api/services/{domain}/{service}', headers=headers, json={'entity_id': device}, timeout=10)
                if resp.status_code in (200, 201):
                    return f"Device '{device}' {action}."
                return f'Error: {resp.status_code} — {resp.text}'
            elif action == 'set_temperature':
                if not device or not value:
                    return 'Device entity_id and temperature value required.'
                resp = requests.post(f'{ha_url}/api/services/climate/set_temperature', headers=headers, json={'entity_id': device, 'temperature': float(value)}, timeout=10)
                if resp.status_code in (200, 201):
                    return f"Temperature set to {value}° for '{device}'."
                return f'Error: {resp.status_code} — {resp.text}'
            elif action == 'get_status':
                if not device:
                    return 'Device entity_id required.'
                resp = requests.get(f'{ha_url}/api/states/{device}', headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    state = data.get('state', '?')
                    attrs = data.get('attributes', {})
                    friendly = attrs.get('friendly_name', device)
                    return f'{friendly} ({device}): {state}'
                return f'Device not found: {resp.status_code}'
            elif action == 'scene':
                if not scene:
                    return 'Scene name required.'
                resp = requests.get(f'{ha_url}/api/states', headers=headers, timeout=10)
                if resp.status_code != 200:
                    return f'Error fetching scenes: {resp.status_code}'
                states = resp.json()
                scene_entity = None
                for s in states:
                    if s['entity_id'].startswith('scene.'):
                        attrs = s.get('attributes', {})
                        if scene.lower() in attrs.get('friendly_name', '').lower():
                            scene_entity = s['entity_id']
                            break
                if not scene_entity:
                    return f"Scene '{scene}' not found."
                resp = requests.post(f'{ha_url}/api/services/scene/turn_on', headers=headers, json={'entity_id': scene_entity}, timeout=10)
                if resp.status_code in (200, 201):
                    return f"Scene '{scene}' activated."
                return f'Error: {resp.status_code} — {resp.text}'
            else:
                return f'Unknown action: {action}. Use: list_devices, turn_on, turn_off, set_temperature, get_status, scene.'
        except requests.RequestException as e:
            return f'Home Assistant connection error: {e}'
        except Exception as e:
            return f'Smart home error: {e}'
