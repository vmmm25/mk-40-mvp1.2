import os
import json
from pathlib import Path
from config import is_windows, is_mac

def epic_manifests_path() -> Path | None:
    if is_windows():
        p = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) \
            / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
        return p if p.exists() else None
    if is_mac():
        p = Path.home() / "Library" / "Application Support" \
            / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
        return p if p.exists() else None
    return None

def get_epic_games() -> list[dict]:
    manifests = epic_manifests_path()
    if not manifests:
        return []
    games = []
    for item_file in manifests.glob("*.item"):
        try:
            data = json.loads(item_file.read_text(encoding="utf-8"))
            name = data.get("DisplayName") or data.get("AppName", "")
            if name:
                games.append({"id": data.get("AppName", ""), "name": name})
        except Exception:
            continue
    return games
