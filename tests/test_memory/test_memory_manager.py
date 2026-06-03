import os
import json
import tempfile
from pathlib import Path

import pytest
from unittest.mock import patch

from memory import memory_manager

@pytest.fixture
def temp_memory_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        path = Path(f.name)
    
    # Patch the MEMORY_PATH in the module
    with patch("memory.memory_manager.MEMORY_PATH", path):
        yield path
    
    # Cleanup
    if path.exists():
        path.unlink()

def test_load_memory_empty(temp_memory_file):
    if temp_memory_file.exists():
        temp_memory_file.unlink()
    
    memory = memory_manager.load_memory()
    assert "identity" in memory
    assert "notes" in memory
    assert isinstance(memory["notes"], dict)

def test_update_memory(temp_memory_file):
    update = {"notes": {"color": {"value": "blue"}}}
    memory = memory_manager.update_memory(update)
    assert memory["notes"]["color"]["value"] == "blue"
    
    # Load again to ensure it was saved
    memory2 = memory_manager.load_memory()
    assert memory2["notes"]["color"]["value"] == "blue"

def test_remember_and_forget(temp_memory_file):
    memory_manager.remember("favorite_food", "pizza")
    memory = memory_manager.load_memory()
    assert memory["notes"]["favorite_food"]["value"] == "pizza"
    
    memory_manager.forget("favorite_food")
    memory = memory_manager.load_memory()
    assert "favorite_food" not in memory["notes"]
