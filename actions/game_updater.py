import sys
import time
import threading
import subprocess
import logging
from datetime import datetime
from config import is_windows, is_mac, is_linux

from services.steam import (
    find_steam_path, steam_exe, launch_steam_url, is_steam_running,
    ensure_steam_running, system_shutdown, _KNOWN_APPIDS,
    get_steam_games, search_steam_appid,
    schedule_daily_update, cancel_scheduled_update, get_schedule_status
)
from services.epic import (
    find_epic_exe, is_epic_running, get_epic_games
)

logger = logging.getLogger(__name__)

def _update_steam_games(steam_path, game_name: str = None) -> str:
    if not ensure_steam_running(steam_path):
        return "Could not start Steam."

    exe   = steam_exe(steam_path)
    games = get_steam_games(steam_path)
    if not games:
        return "No Steam games found."

    if game_name:
        name_lower = game_name.lower()
        targets    = [g for g in games if name_lower in g["name"].lower()]
        if not targets:
            available = ", ".join(g["name"] for g in games[:5])
            return f"Game '{game_name}' not found. Installed: {available}..."
    else:
        targets = games

    already_updated, already_running, update_started, errors = [], [], [], []

    for game in targets:
        state = game["state"]
        name  = game["name"]
        if state == 4:
            already_updated.append(name)
        elif state == 1026:
            already_running.append(name)
        else:
            try:
                launch_steam_url(exe, f"steam://update/{game['id']}")
                update_started.append(name)
                time.sleep(0.3)
            except Exception as e:
                errors.append(f"{name}: {e}")

    parts = []
    if update_started:
        names  = ", ".join(update_started[:3])
        suffix = f" and {len(update_started) - 3} more" if len(update_started) > 3 else ""
        parts.append(f"Update started for: {names}{suffix}.")
    if already_running:
        parts.append(f"Already updating: {', '.join(already_running)}.")
    if already_updated:
        parts.append(
            f"{already_updated[0]} is already up to date."
            if game_name else
            f"{len(already_updated)} game(s) already up to date."
        )
    if errors:
        parts.append(f"Errors: {'; '.join(errors)}.")
    return " ".join(parts) if parts else "No games to update."

def _install_steam_game(steam_path, game_name: str = None, app_id: str = None) -> str:
    if not ensure_steam_running(steam_path):
        return "Could not start Steam."

    exe             = steam_exe(steam_path)
    installed_games = get_steam_games(steam_path)

    already = None
    if app_id:
        already = next((g for g in installed_games if g["id"] == str(app_id)), None)
    elif game_name:
        name_lower = game_name.lower()
        already    = next((g for g in installed_games if name_lower in g["name"].lower()), None)
    else:
        return "Please specify a game name or AppID."

    if already:
        state = already["state"]
        name  = already["name"]
        if state == 4:
            return f"'{name}' is already installed and up to date."
        if state == 1026:
            return f"'{name}' is currently downloading or updating."
        if state in (6, 516):
            launch_steam_url(exe, f"steam://update/{already['id']}")
            return f"'{name}' has a pending update. Update started."
        return f"'{name}' is already installed."

    if not app_id and game_name:
        found_id, found_name = search_steam_appid(game_name, steam_path, _KNOWN_APPIDS)
        if not found_id:
            return (f"Could not find '{game_name}' on Steam. Try providing the AppID directly.")
        app_id    = found_id
        game_name = found_name or game_name
        logger.info("Installing %s (AppID: %s)", game_name, app_id)

    try:
        launch_steam_url(exe, f"steam://install/{app_id}")
        return f"Install started for '{game_name}'. Steam will open the download dialog."
    except Exception as e:
        return f"Install failed: {e}"

def _get_download_status(steam_path) -> str:
    games   = get_steam_games(steam_path)
    active  = [g for g in games if g["state"] == 1026]
    pending = [g for g in games if g["state"] in (6, 516)]
    lines   = []
    if active:
        lines.append(f"Downloading: {', '.join(g['name'] for g in active)}.")
    if pending:
        names  = ", ".join(g["name"] for g in pending[:5])
        suffix = f" and {len(pending) - 5} more" if len(pending) > 5 else ""
        lines.append(f"Pending updates: {names}{suffix}.")
    return " ".join(lines) if lines else "No active downloads or pending updates."

def _watch_and_shutdown(steam_path, speak=None, check_interval: int = 30, timeout_hours: int = 12):
    deadline = time.time() + timeout_hours * 3600

    for _ in range(24):
        time.sleep(5)
        active = [g for g in get_steam_games(steam_path) if g["state"] == 1026]
        if active:
            names = ", ".join(g["name"] for g in active)
            if speak: speak(f"Download started for {names}. I'll shut down when done.")
            break
    else:
        return

    while time.time() < deadline:
        time.sleep(check_interval)
        if not any(g["state"] == 1026 for g in get_steam_games(steam_path)):
            if speak: speak("Download complete. Shutting down now.")
            time.sleep(5)
            system_shutdown()
            return

    if speak:
        speak("Download taking too long. Cancelling auto-shutdown.")

def _update_epic_games(epic_exe, game_name: str = None) -> str:
    games = get_epic_games()

    if game_name:
        name_lower = game_name.lower()
        matched    = [g for g in games if name_lower in g["name"].lower()]
        if not matched:
            return f"'{game_name}' not found in Epic."
        try:
            url = f"com.epicgames.launcher://apps/{matched[0]['id']}?action=launch&silent=true"
            if is_mac():
                subprocess.Popen(["open", url])
            elif is_linux():
                subprocess.Popen([str(epic_exe), url] if epic_exe else ["xdg-open", url])
            else:
                subprocess.Popen([str(epic_exe), url])
            return f"Opened Epic for '{matched[0]['name']}'."
        except Exception as e:
            return f"Epic update failed: {e}"
    else:
        try:
            if is_mac():
                subprocess.Popen(["open", "-a", "Epic Games Launcher"])
            elif is_linux():
                if epic_exe:
                    subprocess.Popen([str(epic_exe)])
                else:
                    return "Epic Games is not natively supported on Linux."
            else:
                if is_epic_running():
                    for g in games[:10]:
                        subprocess.Popen([str(epic_exe), f"com.epicgames.launcher://apps/{g['id']}?action=launch&silent=true"])
                        time.sleep(0.5)
                    return f"Triggered update check for {len(games)} Epic game(s)."
                else:
                    subprocess.Popen([str(epic_exe)])
            return f"Epic Games Launcher opened. {len(games)} game(s) will be checked." if games else "Epic Games Launcher opened."
        except Exception as e:
            return f"Epic launch failed: {e}"

def game_updater(parameters: dict, player=None, speak=None) -> str:
    p         = parameters or {}
    action    = p.get("action",    "update").lower().strip()
    platform  = p.get("platform",  "both").lower().strip()
    game_name = (p.get("game_name") or "").strip() or None
    app_id    = (p.get("app_id")    or "").strip() or None
    hour      = int(p.get("hour",   3))
    minute    = int(p.get("minute", 0))
    shutdown  = str(p.get("shutdown_when_done", "false")).lower() == "true"

    results = []

    if action == "schedule":        return schedule_daily_update(hour=hour, minute=minute)
    if action == "cancel_schedule": return cancel_scheduled_update()
    if action == "schedule_status": return get_schedule_status()

    if action == "list":
        if platform in ("steam", "both"):
            steam_path = find_steam_path()
            if steam_path:
                games = get_steam_games(steam_path)
                if games:
                    names  = ", ".join(g["name"] for g in games[:8])
                    suffix = f" and {len(games) - 8} more" if len(games) > 8 else ""
                    results.append(f"Steam ({len(games)} games): {names}{suffix}.")
                else:
                    results.append("Steam: No games found.")
            else:
                results.append("Steam: Not installed.")
        if platform in ("epic", "both"):
            if is_linux():
                results.append("Epic: Not natively supported on Linux.")
            else:
                games = get_epic_games()
                if games:
                    names  = ", ".join(g["name"] for g in games[:8])
                    suffix = f" and {len(games) - 8} more" if len(games) > 8 else ""
                    results.append(f"Epic ({len(games)} games): {names}{suffix}.")
                else:
                    results.append("Epic: No games found.")
        return " | ".join(results) or "No platforms found."

    if action == "download_status":
        if platform in ("steam", "both"):
            steam_path = find_steam_path()
            results.append(_get_download_status(steam_path) if steam_path else "Steam: Not installed.")
        if platform in ("epic", "both"):
            results.append("Epic download status not available directly.")
        return " ".join(results)

    if action in ("install", "update"):
        if platform in ("steam", "both"):
            steam_path = find_steam_path()
            if not steam_path:
                results.append("Steam: Not installed.")
            else:
                if game_name:
                    installed  = get_steam_games(steam_path)
                    is_installed = any(game_name.lower() in g["name"].lower() for g in installed)
                    if not is_installed:
                        msg = _install_steam_game(steam_path, game_name=game_name, app_id=app_id)
                        if shutdown:
                            threading.Thread(target=_watch_and_shutdown, kwargs={"steam_path": steam_path, "speak": speak}, daemon=True).start()
                            msg += " Auto-shutdown enabled."
                        if player: player.write_log(f"[GameUpdater] {msg[:100]}")
                        if speak:  speak(msg)
                        return msg
                    else:
                        results.append(f"Steam: {_update_steam_games(steam_path, game_name=game_name)}")
                else:
                    results.append("Steam: Please specify a game name to install." if action == "install" else f"Steam: {_update_steam_games(steam_path)}")

                if shutdown:
                    threading.Thread(target=_watch_and_shutdown, kwargs={"steam_path": steam_path, "speak": speak}, daemon=True).start()
                    results.append("Auto-shutdown enabled.")

        if platform in ("epic", "both"):
            if is_linux():
                results.append("Epic: Not natively supported on Linux. Use Heroic Launcher.")
            else:
                epic_exe = find_epic_exe()
                results.append(f"Epic: {_update_epic_games(epic_exe, game_name=game_name)}" if epic_exe else "Epic: Not installed.")

        output = " | ".join(results) or "Nothing to do."
        if player: player.write_log(f"[GameUpdater] {output[:100]}")
        if speak:  speak(output)
        return output

    return f"Unknown action: '{action}'."

if __name__ == "__main__":
    if "--scheduled" in sys.argv:
        logger.info("Scheduled run at %s", datetime.now().strftime('%H:%M'))
        result = game_updater({"action": "update", "platform": "both"})
        logger.info("Result: %s", result)