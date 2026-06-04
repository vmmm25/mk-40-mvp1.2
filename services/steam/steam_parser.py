import re
import json
from pathlib import Path

def get_steam_libraries(steam_path: Path) -> list[Path]:
    libraries = [steam_path / "steamapps"]
    vdf_path  = steam_path / "steamapps" / "libraryfolders.vdf"
    if not vdf_path.exists():
        return libraries
    try:
        content = vdf_path.read_text(encoding="utf-8", errors="ignore")
        for raw_path in re.findall(r'"path"\s+"([^"]+)"', content):
            lib = Path(raw_path.replace("\\\\", "/")) / "steamapps"
            if lib.exists() and lib not in libraries:
                libraries.append(lib)
    except Exception:
        pass
    return libraries

def get_steam_games(steam_path: Path) -> list[dict]:
    games = []
    for lib in get_steam_libraries(steam_path):
        for acf in lib.glob("appmanifest_*.acf"):
            try:
                content  = acf.read_text(encoding="utf-8", errors="ignore")
                app_id   = re.search(r'"appid"\s+"(\d+)"',     content)
                name     = re.search(r'"name"\s+"([^"]+)"',     content)
                state    = re.search(r'"StateFlags"\s+"(\d+)"', content)
                size     = re.search(r'"SizeOnDisk"\s+"(\d+)"', content)
                if app_id and name:
                    games.append({
                        "id":    app_id.group(1),
                        "name":  name.group(1),
                        "state": int(state.group(1)) if state else 0,
                        "size":  int(size.group(1))  if size  else 0,
                        "lib":   str(lib),
                        "acf":   str(acf),
                    })
            except Exception:
                continue
    return games

def search_steam_appid(game_name: str, steam_path: Path, known_appids: dict) -> tuple[str | None, str | None]:
    name_lower = game_name.lower().strip()
    if steam_path:
        for g in get_steam_games(steam_path):
            if name_lower in g["name"].lower():
                return g["id"], g["name"]
    
    if name_lower in known_appids:
        app_id, canonical = known_appids[name_lower]
        return app_id, canonical

    for key, (app_id, canonical) in known_appids.items():
        if name_lower in key or key in name_lower:
            return app_id, canonical

    try:
        import urllib.request, urllib.parse
        query = urllib.parse.quote(game_name)
        url   = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
        req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            items = json.loads(resp.read().decode()).get("items", [])
        if items:
            best = items[0]
            return str(best["id"]), best["name"]
    except Exception:
        pass

    return None, None
