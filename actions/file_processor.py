import logging
from pathlib import Path
from services.file_processing import process_file as _process_file_impl

logger = logging.getLogger(__name__)

def file_processor(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    path_str = params.get("path") or params.get("file_path") or params.get("filepath")
    action   = params.get("action", "")
    
    if not path_str:
        return "Please provide a valid file path."
        
    path = Path(path_str.replace("\"", "").replace("'", "")).resolve()
    
    if player:
        player.write_log(f"[File] {action} {path.name}")
        
    return _process_file_impl(path, action, params, player)