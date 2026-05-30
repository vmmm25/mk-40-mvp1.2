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
from agent.task_queue import get_queue, TaskPriority
from memory.memory_manager import update_memory
from memory.config_manager import get_os_system

def _get_os_system() -> str:
    return get_os_system() or "windows"

def handle_save_memory(args: dict, ui: Any) -> str:
    if args.get("key") and args.get("value"):
        update_memory({args.get("category", "notes"): {args.get("key", ""): {"value": args.get("value", "")}}})
    return "Memory saved."

def handle_open_app(args: dict, ui: Any) -> str:
    return open_app(parameters=args, response=None, player=ui) or "Done."

def handle_weather_report(args: dict, ui: Any) -> str:
    return weather_action(parameters=args, player=ui) or "Done."

def handle_browser_control(args: dict, ui: Any) -> str:
    return browser_control(parameters=args, player=ui) or "Done."

def handle_file_controller(args: dict, ui: Any) -> str:
    return file_controller(parameters=args, player=ui) or "Done."

def handle_send_message(args: dict, ui: Any) -> str:
    return send_message(parameters=args, response=None, player=ui, session_memory=None) or "Done."

def handle_reminder(args: dict, ui: Any) -> str:
    return reminder(parameters=args, response=None, player=ui) or "Done."

def handle_youtube_video(args: dict, ui: Any) -> str:
    return youtube_video(parameters=args, response=None, player=ui) or "Done."

def handle_screen_process(args: dict, ui: Any) -> str:
    threading.Thread(
        target=screen_process,
        kwargs={"parameters": args, "response": None, "player": ui, "session_memory": None},
        daemon=True
    ).start()
    return "Screen processing started."

def handle_computer_settings(args: dict, ui: Any) -> str:
    return computer_settings(parameters=args, response=None, player=ui) or "Done."

def handle_desktop_control(args: dict, ui: Any) -> str:
    return desktop_control(parameters=args, player=ui) or "Done."

def handle_code_helper(args: dict, ui: Any) -> str:
    return code_helper(parameters=args, player=ui, speak=None) or "Done."

def handle_dev_agent(args: dict, ui: Any) -> str:
    return dev_agent(parameters=args, player=ui, speak=None) or "Done."

def handle_agent_task(args: dict, ui: Any) -> str:
    priority_map = {"low": TaskPriority.LOW, "normal": TaskPriority.NORMAL, "high": TaskPriority.HIGH}
    priority = priority_map.get(args.get("priority", "normal").lower(), TaskPriority.NORMAL)
    get_queue().submit(goal=args.get("goal", ""), priority=priority, speak=None)
    return f"Task '{args.get('goal', '')[:60]}' queued."

def handle_web_search(args: dict, ui: Any) -> str:
    return web_search_action(parameters=args, player=ui) or "Done."

def handle_file_processor(args: dict, ui: Any) -> str:
    if not args.get("file_path") and getattr(ui, "current_file", None):
        params = {**args, "file_path": ui.current_file}
        return file_processor(parameters=params, player=ui, speak=None) or "Done."
    return file_processor(parameters=args, player=ui, speak=None) or "Done."

def handle_computer_control(args: dict, ui: Any) -> str:
    return computer_control(parameters=args, player=ui) or "Done."

def handle_game_updater(args: dict, ui: Any) -> str:
    return game_updater(parameters=args, player=ui, speak=None) or "Done."

def handle_flight_finder(args: dict, ui: Any) -> str:
    return flight_finder(parameters=args, player=ui) or "Done."

def handle_shutdown_jarvis(args: dict, ui: Any) -> str:
    ui.write_log("SYS: Shutdown requested.")
    
    # Try graceful shutdown via main
    try:
        import main
        main._engine_stop.set()
    except Exception:
        pass

    def _delayed_exit():
        time.sleep(1.5)
        try:
            ui.root.quit()
        except Exception:
            os._exit(0)
            
    threading.Thread(target=_delayed_exit, daemon=True).start()
    return "Goodbye, sir."

def handle_process_with_openrouter(args: dict, ui: Any) -> str:
    try:
        from or_client import client
        prompt = args.get("prompt", "").strip()
        if not prompt:
            return "No prompt provided."
        # Always use the pool — the AI should NOT pass model IDs directly
        # (they tend to be malformed and cause fallback to liquid/lfm)
        result = client.chat(prompt, model=None)
        return result if result else "OpenRouter returned an empty response."
    except Exception as e:
        return f"OpenRouter error: {e}"

TOOL_IMPLEMENTATIONS: dict[str, Callable] = {
    "save_memory": handle_save_memory,
    "open_app": handle_open_app,
    "weather_report": handle_weather_report,
    "browser_control": handle_browser_control,
    "file_controller": handle_file_controller,
    "send_message": handle_send_message,
    "reminder": handle_reminder,
    "youtube_video": handle_youtube_video,
    "screen_process": handle_screen_process,
    "computer_settings": handle_computer_settings,
    "desktop_control": handle_desktop_control,
    "code_helper": handle_code_helper,
    "dev_agent": handle_dev_agent,
    "agent_task": handle_agent_task,
    "web_search": handle_web_search,
    "file_processor": handle_file_processor,
    "computer_control": handle_computer_control,
    "game_updater": handle_game_updater,
    "flight_finder": handle_flight_finder,
    "shutdown_jarvis": handle_shutdown_jarvis,
    "process_with_openrouter": handle_process_with_openrouter,
}
