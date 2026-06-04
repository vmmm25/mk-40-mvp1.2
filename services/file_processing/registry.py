from pathlib import Path
import logging

from .image_handler import process_image
from .pdf_handler import process_pdf
from .text_handler import process_text_doc
from .data_handler import process_data
from .json_handler import process_json
from .code_handler import process_code
from .audio_handler import process_audio
from .video_handler import process_video
from .archive_handler import process_archive
from .pptx_handler import process_pptx

logger = logging.getLogger(__name__)

def detect_file_type(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    image_exts = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "svg", "ico"}
    video_exts = {"mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "m4v", "3gp"}
    audio_exts = {"mp3", "wav", "ogg", "m4a", "aac", "flac", "wma", "opus"}
    code_exts  = {"py", "js", "ts", "jsx", "tsx", "html", "css", "java", "c",
                  "cpp", "cs", "go", "rs", "rb", "php", "swift", "kt", "sh",
                  "bash", "ps1", "lua", "r", "m", "sql", "yaml", "toml"}
    archive_exts = {"zip", "rar", "tar", "gz", "7z", "bz2", "xz"}

    if ext in image_exts:  return "image"
    if ext in video_exts:  return "video"
    if ext in audio_exts:  return "audio"
    if ext in code_exts:   return "code"
    if ext in archive_exts: return "archive"
    if ext == "pdf":       return "pdf"
    if ext in ("docx", "doc"): return "docx"
    if ext in ("txt", "md", "rst", "log"): return "text"
    if ext in ("csv", "tsv"): return "csv"
    if ext in ("xlsx", "xls", "ods"): return "excel"
    if ext == "json":      return "json"
    if ext == "xml":       return "xml"
    if ext in ("pptx", "ppt"): return "pptx"
    return "unknown"

def process_file(path: Path, action: str, params: dict, speak=None) -> str:
    if not path.exists():
        return f"File not found: {path}"
    
    file_type = detect_file_type(path)
    logger.info("Processing file: %s (Type: %s) (Action: %s)", path.name, file_type, action)

    try:
        if file_type == "image":
            return process_image(path, action, params, speak)
        elif file_type == "pdf":
            return process_pdf(path, action, params, speak)
        elif file_type in ("text", "docx"):
            return process_text_doc(path, file_type, action, params, speak)
        elif file_type in ("csv", "excel"):
            return process_data(path, file_type, action, params, speak)
        elif file_type == "json":
            return process_json(path, action, params, speak)
        elif file_type == "code":
            return process_code(path, action, params, speak)
        elif file_type == "audio":
            return process_audio(path, action, params, speak)
        elif file_type == "video":
            return process_video(path, action, params, speak)
        elif file_type == "archive":
            return process_archive(path, action, params, speak)
        elif file_type == "pptx":
            return process_pptx(path, action, params, speak)
        else:
            return f"Unsupported file type: {path.suffix}"
    except Exception as e:
        logger.exception("Error processing file")
        return f"Error processing file {path.name}: {e}"
