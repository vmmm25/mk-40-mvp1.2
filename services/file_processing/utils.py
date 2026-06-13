import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_file_size_str(path: Path) -> str:
    size = path.stat().st_size
    if size < 1024:        return f"{size} B"
    if size < 1024**2:     return f"{size/1024:.1f} KB"
    if size < 1024**3:     return f"{size/1024**2:.1f} MB"
    return f"{size/1024**3:.1f} GB"

def get_output_path(src: Path, suffix: str, new_ext: str = None) -> Path:
    ext  = new_ext or src.suffix
    name = f"{src.stem}_{suffix}{ext}"
    return src.parent / name

def gemini_client():
    from providers.or_client import client
    # Helper to generate content, adapting to our central client where needed
    # We will just expose a simple interface matching the old _GeminiModel
    class GeminiWrapper:
        def generate_content(self, prompt, **kwargs):
            try:
                class DummyResponse:
                    pass
                resp = DummyResponse()
                
                # If prompt is a list containing text and parts (like images)
                if isinstance(prompt, list):
                    text_part = next((p for p in prompt if isinstance(p, str)), "")
                    resp.text = client.chat(text_part)
                else:
                    resp.text = client.chat(prompt)
                return resp
            except Exception as e:
                logger.error("Gemini wrapper failed: %s", e)
                raise
    return GeminiWrapper()
