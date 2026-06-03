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

def handle_terminal_control(args: dict, ui: Any) -> str:
    return terminal_control(parameters=args, player=ui) or "Done."

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

def handle_search_documents(args: dict, ui: Any) -> str:
    query = args.get("query", "")
    n_results = args.get("n_results", 5)
    if not query:
        return "No query provided."
    try:
        from rag.retriever import DocumentRetriever
        retriever = DocumentRetriever()
        results = retriever.search(query, n_results=n_results)
        if not results:
            return "No results found in the document database."
        formatted = [f"- {r['text']} (Source: {r['metadata'].get('source', 'Unknown')}, Page {r['metadata'].get('page', 1)})" for r in results]
        return "\n".join(formatted)
    except Exception as e:
        return f"Error searching documents: {e}"

def handle_index_document(args: dict, ui: Any) -> str:
    path = args.get("path", "")
    if not path:
        return "No path provided."
    try:
        from pathlib import Path
        from rag.indexer import DocumentIndexer
        p = Path(path)
        if not p.exists():
            return f"Path does not exist: {path}"
            
        indexer = DocumentIndexer()
        if p.is_dir():
            count = indexer.index_directory(p)
            return f"Indexed directory {path}. Total chunks: {count}"
        else:
            count = indexer.index_file(p)
            return f"Indexed file {path}. Total chunks: {count}"
    except Exception as e:
        return f"Error indexing document: {e}"

def handle_email_read(args: dict, ui: Any) -> str:
    max_results = args.get("max_results", 5)
    query = args.get("query", "")
    try:
        from services.email.gmail_client import GmailClient
        client = GmailClient()
        emails = client.read_emails(max_results=max_results, query=query)
        if not emails:
            return "No emails found."
        
        formatted = []
        for e in emails:
            formatted.append(f"From: {e['sender']}\nSubject: {e['subject']}\nSnippet: {e['snippet']}\n---")
        return "\n".join(formatted)
    except Exception as e:
        return f"Error reading emails: {e}"

import asyncio
import os
from pathlib import Path

def handle_smart_home(args: dict, ui: Any) -> str:
    action = args.get("action", "")
    device = args.get("device", "")
    value = args.get("value", "")
    scene = args.get("scene", "")

    # Home Assistant connection details from config
    try:
        from memory.config_manager import get_config
        config = get_config()
        ha_url = config.get("home_assistant_url", "")
        ha_token = config.get("home_assistant_token", "")
    except Exception as e:
        return f"Config error: {e}"

    if not ha_url or not ha_token:
        return (
            "Home Assistant not configured. "
            "Add 'home_assistant_url' and 'home_assistant_token' to config/api_keys.json."
        )

    import requests

    ha_url = ha_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }

    try:
        if action == "list_devices":
            resp = requests.get(
                f"{ha_url}/api/states",
                headers=headers,
                timeout=10,
            )
            if resp.status_code != 200:
                return f"Error fetching devices: {resp.status_code}"
            states = resp.json()
            # Filter to controllable entities
            devices = [
                s for s in states
                if s["entity_id"].startswith(("light.", "switch.", "climate.", "scene.", "cover."))
            ]
            if not devices:
                return "No controllable devices found."
            lines = []
            for d in devices:
                state = d.get("state", "?")
                attrs = d.get("attributes", {})
                friendly = attrs.get("friendly_name", d["entity_id"])
                lines.append(f"  {friendly} ({d['entity_id']}) — {state}")
            return "Home Assistant devices:\n" + "\n".join(lines)

        elif action in ("turn_on", "turn_off"):
            if not device:
                return "Device entity_id required."
            domain = device.split(".")[0] if "." in device else "homeassistant"
            service = "turn_on" if action == "turn_on" else "turn_off"
            resp = requests.post(
                f"{ha_url}/api/services/{domain}/{service}",
                headers=headers,
                json={"entity_id": device},
                timeout=10,
            )
            if resp.status_code in (200, 201):
                return f"Device '{device}' {action}."
            return f"Error: {resp.status_code} — {resp.text}"

        elif action == "set_temperature":
            if not device or not value:
                return "Device entity_id and temperature value required."
            resp = requests.post(
                f"{ha_url}/api/services/climate/set_temperature",
                headers=headers,
                json={"entity_id": device, "temperature": float(value)},
                timeout=10,
            )
            if resp.status_code in (200, 201):
                return f"Temperature set to {value}° for '{device}'."
            return f"Error: {resp.status_code} — {resp.text}"

        elif action == "get_status":
            if not device:
                return "Device entity_id required."
            resp = requests.get(
                f"{ha_url}/api/states/{device}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                state = data.get("state", "?")
                attrs = data.get("attributes", {})
                friendly = attrs.get("friendly_name", device)
                return f"{friendly} ({device}): {state}"
            return f"Device not found: {resp.status_code}"

        elif action == "scene":
            if not scene:
                return "Scene name required."
            # Find scene entity ID by name
            resp = requests.get(
                f"{ha_url}/api/states",
                headers=headers,
                timeout=10,
            )
            if resp.status_code != 200:
                return f"Error fetching scenes: {resp.status_code}"
            states = resp.json()
            scene_entity = None
            for s in states:
                if s["entity_id"].startswith("scene."):
                    attrs = s.get("attributes", {})
                    if scene.lower() in attrs.get("friendly_name", "").lower():
                        scene_entity = s["entity_id"]
                        break
            if not scene_entity:
                return f"Scene '{scene}' not found."
            resp = requests.post(
                f"{ha_url}/api/services/scene/turn_on",
                headers=headers,
                json={"entity_id": scene_entity},
                timeout=10,
            )
            if resp.status_code in (200, 201):
                return f"Scene '{scene}' activated."
            return f"Error: {resp.status_code} — {resp.text}"

        else:
            return f"Unknown action: {action}. Use: list_devices, turn_on, turn_off, set_temperature, get_status, scene."

    except requests.RequestException as e:
        return f"Home Assistant connection error: {e}"
    except Exception as e:
        return f"Smart home error: {e}"

def handle_git_operation(args: dict, ui: Any) -> str:
    action = args.get("action", "")
    path = args.get("path", "")
    message = args.get("message", "")
    branch = args.get("branch", "")
    url = args.get("url", "")

    try:
        from services.git.git_client import GitClient
        repo_path = path if path else None
        git = GitClient(repo_path=repo_path)
    except Exception as e:
        return f"Error initialising Git client: {e}"

    try:
        if action == "status":
            return git.status()
        elif action == "log":
            return git.log()
        elif action == "diff":
            return git.diff()
        elif action == "add":
            return git.add(".") if not message else git.add(message)
        elif action == "commit":
            if not message:
                return "Commit message required."
            return git.commit(message)
        elif action == "push":
            return git.push(branch=branch or None)
        elif action == "pull":
            return git.pull(branch=branch or None)
        elif action == "branch":
            return git.branch(name=branch or None)
        elif action == "checkout":
            if not branch:
                return "Branch name required for checkout."
            return git.checkout(branch)
        elif action == "merge":
            if not branch:
                return "Branch name required for merge."
            return git.merge(branch)
        elif action == "clone":
            if not url:
                return "URL required for clone."
            return git.clone(url, path or None)
        else:
            return f"Unknown git action: {action}"
    except Exception as e:
        return f"Git error: {e}"

def handle_docker_control(args: dict, ui: Any) -> str:
    action = args.get("action", "")
    container = args.get("container", "")
    compose_file = args.get("compose_file", "")

    try:
        from services.docker.docker_client import DockerClient
        docker = DockerClient()
    except Exception as e:
        return f"Error initialising Docker client: {e}"

    if not docker.is_available():
        return "Docker is not available (not installed or Docker daemon not running)."

    try:
        if action == "list":
            return docker.list_containers()
        elif action == "start":
            if not container:
                return "Container name required."
            return docker.start(container)
        elif action == "stop":
            if not container:
                return "Container name required."
            return docker.stop(container)
        elif action == "restart":
            if not container:
                return "Container name required."
            return docker.restart(container)
        elif action == "logs":
            if not container:
                return "Container name required."
            return docker.logs(container)
        elif action == "stats":
            return docker.stats()
        elif action == "compose_up":
            return docker.compose_up(compose_file or None)
        elif action == "compose_down":
            return docker.compose_down(compose_file or None)
        else:
            return f"Unknown docker action: {action}"
    except Exception as e:
        return f"Docker error: {e}"

def handle_database_query(args: dict, ui: Any) -> str:
    connection = args.get("connection", "")
    query = args.get("query", "")
    if not connection or not query:
        return "Both 'connection' and 'query' parameters are required."

    try:
        from services.database.db_client import DatabaseClient
        db = DatabaseClient()
    except Exception as e:
        return f"Error initialising database client: {e}"

    if not db.is_configured(connection):
        available = db.list_connections()
        if not available:
            return (
                f"No databases configured. Create config/database_connections.json "
                f"with connection details."
            )
        return f"Unknown connection '{connection}'. Available: {', '.join(available)}"

    try:
        result = db.execute_query(connection, query)
        if not result.get("success"):
            return f"Query error: {result.get('error', 'Unknown error')}"

        if "columns" in result:
            # Format as table
            cols = result["columns"]
            rows = result["rows"]
            header = " | ".join(str(c) for c in cols)
            separator = "-" * len(header)
            lines = [header, separator]
            for row in rows[:50]:  # limit display
                lines.append(" | ".join(str(v) for v in row))
            if len(rows) > 50:
                lines.append(f"... and {len(rows) - 50} more rows")
            lines.append(f"({result.get('row_count', len(rows))} rows returned)")
            return "\n".join(lines)
        else:
            return f"Query executed. {result.get('affected_rows', 0)} rows affected."
    except Exception as e:
        return f"Database error: {e}"

def handle_play_music(args: dict, ui: Any) -> str:
    action = args.get("action", "")
    query = args.get("query", "")
    volume = args.get("volume")

    try:
        from services.media.spotify_client import SpotifyClient
        client = SpotifyClient()
    except ImportError:
        return "Spotify client not available (spotipy not installed)."
    except Exception as e:
        return f"Error initialising Spotify: {e}"

    if not client.is_authenticated():
        return (
            "Spotify not configured. Please create config/spotify_credentials.json "
            "with your Spotify client_id, client_secret, and redirect_uri."
        )

    try:
        if action == "play":
            return client.play(query=query)
        elif action == "pause":
            return client.pause()
        elif action == "next":
            return client.next_track()
        elif action == "previous":
            return client.previous_track()
        elif action == "volume":
            if volume is None:
                return "Volume parameter required."
            return client.set_volume(int(volume))
        elif action == "info":
            info = client.current_playback()
            if "error" in info:
                return f"Spotify error: {info['error']}"
            if "message" in info:
                return info["message"]
            return (
                f"Now playing: {info['track']} by {info['artists']} "
                f"({info.get('album', '')})"
            )
        elif action == "search":
            if not query:
                return "Query parameter required for search."
            results = client.search(query=query)
            if not results:
                return f"No results found for '{query}'."
            lines = [f"{r['name']} — {r.get('artists', '')}" for r in results]
            return "Search results:\n" + "\n".join(lines)
        else:
            return f"Unknown action: {action}. Use: play, pause, next, previous, volume, info, search."
    except Exception as e:
        return f"Spotify error: {e}"

def handle_generate_image(args: dict, ui: Any) -> str:
    prompt = args.get("prompt", "")
    style = args.get("style")
    size = args.get("size", "1024x1024")
    count = args.get("count", 1)
    save = args.get("save", True)
    backend = args.get("backend", "auto")

    if not prompt:
        return "No prompt provided."

    async def _generate():
        backends = []
        if backend == "auto":
            backends = ["local", "gemini", "openai"]
        else:
            backends = [backend]

        for name in backends:
            try:
                if name == "local":
                    from services.image_gen.local_sd import StableDiffusionLocal
                    gen = StableDiffusionLocal()
                    if gen.is_available():
                        images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                        if images:
                            return "local", images
                elif name == "gemini":
                    from services.image_gen.gemini_gen import GeminiImageGen
                    gen = GeminiImageGen()
                    if gen.is_available():
                        images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                        if images:
                            return "gemini", images
                elif name == "openai":
                    from services.image_gen.openai_gen import OpenAIImageGen
                    gen = OpenAIImageGen()
                    if gen.is_available():
                        images = await gen.generate(prompt=prompt, style=style, size=size, count=count)
                        if images:
                            return "openai", images
            except Exception as e:
                logger = __import__("logging").getLogger(__name__)
                logger.warning("Image backend %s failed: %s", name, e)
                continue
        return None, []

    try:
        backend_name, images = asyncio.run(_generate())
        if not images:
            return "No images could be generated. Make sure at least one backend is available (local SD, Gemini, or OpenRouter)."

        if save:
            desk = Path(os.environ.get("USERPROFILE", ".")) / "Desktop"
            saved = []
            for i, img_bytes in enumerate(images):
                ts = __import__("time").strftime("%Y%m%d_%H%M%S")
                fname = f"jarvis_gen_{ts}_{i}.png"
                fpath = desk / fname
                fpath.write_bytes(img_bytes)
                saved.append(str(fpath))
            return f"Generated {len(images)} image(s) via {backend_name}.\nSaved to:\n" + "\n".join(saved)

        return f"Generated {len(images)} image(s) via {backend_name}."

    except Exception as e:
        return f"Error generating images: {e}"

def handle_calendar_list_events(args: dict, ui: Any) -> str:
    max_results = args.get("max_results", 10)
    days_ahead = args.get("days_ahead", 7)
    try:
        from services.calendar.gcal_client import GoogleCalendarClient
        client = GoogleCalendarClient()
        events = client.list_events(max_results=max_results, days_ahead=days_ahead)
        if not events:
            return "No upcoming events found."
        formatted = []
        for ev in events:
            formatted.append(
                f"- {ev['summary']} ({ev['start']})"
                f"{' — ' + ev['location'] if ev.get('location') else ''}"
            )
        return "Upcoming events:\n" + "\n".join(formatted)
    except Exception as e:
        return f"Error listing calendar events: {e}"

def handle_calendar_create_event(args: dict, ui: Any) -> str:
    summary = args.get("summary", "")
    date = args.get("date", "")
    time = args.get("time", "12:00")
    duration = args.get("duration_minutes", 60)
    description = args.get("description", "")
    attendees = args.get("attendees", None)
    if not summary or not date:
        return "Missing required parameters: summary and date."
    try:
        from services.calendar.gcal_client import GoogleCalendarClient
        client = GoogleCalendarClient()
        result = client.create_event(
            summary=summary, date=date, time=time,
            duration_minutes=duration, description=description,
            attendees=attendees,
        )
        if result:
            return f"Event created: {result['summary']} (link: {result.get('htmlLink', 'N/A')})"
        return "Failed to create calendar event."
    except Exception as e:
        return f"Error creating calendar event: {e}"

def handle_email_send(args: dict, ui: Any) -> str:
    to = args.get("to")
    subject = args.get("subject")
    body = args.get("body")
    if not to or not subject or not body:
        return "Missing required parameters for email_send."
    try:
        from services.email.gmail_client import GmailClient
        client = GmailClient()
        success = client.send_email(to=to, subject=subject, body=body)
        return "Email sent successfully." if success else "Failed to send email."
    except Exception as e:
        return f"Error sending email: {e}"

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
    "terminal_control": handle_terminal_control,
    "shutdown_jarvis": handle_shutdown_jarvis,
    "process_with_openrouter": handle_process_with_openrouter,
    "search_documents": handle_search_documents,
    "index_document": handle_index_document,
    "email_read": handle_email_read,
    "email_send": handle_email_send,
    "smart_home": handle_smart_home,
    "git_operation": handle_git_operation,
    "docker_control": handle_docker_control,
    "database_query": handle_database_query,
    "play_music": handle_play_music,
    "generate_image": handle_generate_image,
    "calendar_list_events": handle_calendar_list_events,
    "calendar_create_event": handle_calendar_create_event,
}
