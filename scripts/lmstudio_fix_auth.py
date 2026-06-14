"""Fix LM Studio API auth to allow JARVIS connections."""
import json
from pathlib import Path

store = Path.home() / ".lmstudio" / ".internal" / "permissions-store.json"
backup = store.with_suffix(".json.backup2")

# Read
data = json.loads(store.read_text(encoding="utf-8"))
print(f"Current tokenMode: {data['json']['tokenMode']}")

# Backup
store.rename(backup)
print(f"Backup at: {backup}")

# Change
data["json"]["tokenMode"] = "optional"
store.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Changed tokenMode to: optional")
