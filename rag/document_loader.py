from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    SUPPORTED_EXTENSIONS = {
        ".pdf": "load_pdf",
        ".docx": "load_docx",
        ".txt": "load_text",
        ".md": "load_text",
        ".csv": "load_csv",
        ".xlsx": "load_excel",
        ".py": "load_text",
        ".js": "load_text",
        ".ts": "load_text",
    }
    
    def load(self, path: Path) -> List[Dict[str, Any]]:
        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"Unsupported file extension: {ext} for {path}")
            return []
        
        method_name = self.SUPPORTED_EXTENSIONS[ext]
        method = getattr(self, method_name, None)
        if method:
            try:
                return method(path)
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                return []
        return []

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start += chunk_size - overlap
        return chunks

    def load_pdf(self, path: Path) -> List[Dict[str, Any]]:
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.error("pypdf is not installed.")
            return []
            
        reader = PdfReader(str(path))
        chunks = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Add a chunk per page or break it down further if pages are huge
                chunks.append({"text": text.strip(), "page": i + 1})
        return chunks

    def load_docx(self, path: Path) -> List[Dict[str, Any]]:
        try:
            import docx
        except ImportError:
            logger.error("python-docx is not installed.")
            return []
            
        doc = docx.Document(str(path))
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        text_chunks = self._chunk_text(full_text)
        return [{"text": chunk, "page": 1} for chunk in text_chunks]

    def load_text(self, path: Path) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
        text_chunks = self._chunk_text(full_text)
        return [{"text": chunk, "page": 1} for chunk in text_chunks]

    def load_csv(self, path: Path) -> List[Dict[str, Any]]:
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is not installed.")
            return []
            
        df = pd.read_csv(path)
        # Convert each row to a string chunk
        chunks = []
        for i, row in df.iterrows():
            row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
            chunks.append({"text": row_str, "page": i + 1})
        return chunks

    def load_excel(self, path: Path) -> List[Dict[str, Any]]:
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas or openpyxl is not installed.")
            return []
            
        df = pd.read_excel(path)
        chunks = []
        for i, row in df.iterrows():
            row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
            chunks.append({"text": row_str, "page": i + 1})
        return chunks
