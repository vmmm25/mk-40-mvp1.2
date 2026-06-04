import sys
import subprocess
from pathlib import Path
from config import is_windows, is_mac, is_linux

def get_script_path() -> Path:
    # We point to game_updater.py which will handle the scheduled run
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "actions" / "game_updater.py"

def schedule_daily_update(hour: int = 3, minute: int = 0) -> str:
    if is_windows(): return _schedule_windows(hour, minute)
    if is_mac():     return _schedule_mac(hour, minute)
    return _schedule_linux(hour, minute)

def _schedule_windows(hour: int, minute: int) -> str:
    task_name   = "JARVIS_GameUpdater"
    script_path = get_script_path()
    subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], capture_output=True)
    for extra in (["/RL", "HIGHEST", "/RU", "SYSTEM"], []):
        cmd    = ["schtasks", "/Create", "/TN", task_name,
                  "/TR", f'"{sys.executable}" "{script_path}" --scheduled',
                  "/SC", "DAILY", "/ST", f"{hour:02d}:{minute:02d}", "/F", *extra]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Daily game update scheduled at {hour:02d}:{minute:02d}."
    return f"Scheduling failed: {result.stderr.strip()}"

def _schedule_mac(hour: int, minute: int) -> str:
    plist_dir   = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_path  = plist_dir / "com.jarvis.gameupdater.plist"
    script_path = get_script_path()
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>Label</key><string>com.jarvis.gameupdater</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
        <string>--scheduled</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>{hour}</integer>
        <key>Minute</key><integer>{minute}</integer>
    </dict>
    <key>RunAtLoad</key><false/>
</dict></plist>"""
    try:
        plist_path.write_text(plist_content, encoding="utf-8")
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        result = subprocess.run(["launchctl", "load", str(plist_path)],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return f"Daily game update scheduled at {hour:02d}:{minute:02d} via launchd."
        return f"Scheduling failed: {result.stderr.strip()}"
    except Exception as e:
        return f"Scheduling failed: {e}"

def _schedule_linux(hour: int, minute: int) -> str:
    script_path = get_script_path()
    marker      = "# JARVIS_GameUpdater"
    cron_entry  = f"{minute} {hour} * * * {sys.executable} {script_path} --scheduled  {marker}"
    try:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines    = [l for l in existing.stdout.splitlines()
                    if marker not in l and str(script_path) not in l]
        lines.append(cron_entry)
        proc = subprocess.run(["crontab", "-"],
                              input="\n".join(lines) + "\n",
                              text=True, capture_output=True)
        if proc.returncode == 0:
            return f"Daily game update scheduled at {hour:02d}:{minute:02d} via cron."
        return f"Scheduling failed: {proc.stderr.strip()}"
    except Exception as e:
        return f"Scheduling failed: {e}"

def cancel_scheduled_update() -> str:
    if is_windows():
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", "JARVIS_GameUpdater", "/F"],
            capture_output=True, text=True
        )
        return ("Scheduled update cancelled."
                if result.returncode == 0 else "No scheduled update found.")
    if is_mac():
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.jarvis.gameupdater.plist"
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink()
            return "Scheduled update cancelled."
        return "No scheduled update found."

    try:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines    = [l for l in existing.stdout.splitlines()
                    if "JARVIS_GameUpdater" not in l]
        subprocess.run(["crontab", "-"],
                       input="\n".join(lines) + "\n", text=True)
        return "Scheduled update cancelled."
    except Exception as e:
        return f"Cancel failed: {e}"

def get_schedule_status() -> str:
    if is_windows():
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", "JARVIS_GameUpdater", "/FO", "LIST"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return "No scheduled game update found."
        for line in result.stdout.strip().splitlines():
            if any(k in line for k in
                   ("Next Run", "Sonraki", "Prochaine", "Próxima", "Nächste")):
                return f"Game update scheduled. {line.strip()}"
        return "Game update is scheduled."
    if is_mac():
        plist_path = (Path.home() / "Library" / "LaunchAgents"
                      / "com.jarvis.gameupdater.plist")
        return ("Game update is scheduled via launchd."
                if plist_path.exists() else "No scheduled game update found.")

    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if "JARVIS_GameUpdater" in result.stdout:
            for line in result.stdout.splitlines():
                if "JARVIS_GameUpdater" in line:
                    return f"Game update is scheduled: {line.split('#')[0].strip()}"
        return "No scheduled game update found."
    except Exception:
        return "No scheduled game update found."
