"""SKILL.md Adapter for JARVIS.

Downloads SKILL.md-style repositories (e.g. garri333/Skills, javiertarazon/agente-copilot),
parses the SKILL.md files with frontmatter, and indexes them into a dedicated
ChromaDB collection for semantic search and activation.
"""

from __future__ import annotations

import io
import json
import logging
import re
import shutil
import zipfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SKILL_MD_COLLECTION = "skill_md"
DEFAULT_DB_PATH = "./memory/vector_store"


# ------------------------------------------------------------------
# SKILL.md Parser
# ------------------------------------------------------------------

SKILL_MD_PATTERN = re.compile(r"\.skill\.md$|/SKILL\.md$", re.IGNORECASE)


def parse_skill_md(content: str, source_path: str) -> Optional[Dict[str, Any]]:
    """Parse a SKILL.md file with YAML-like frontmatter.

    Expected format:
    ---
    name: skill-name
    description: What it does
    trigger: /command
    tags: [tag1, tag2]
    ---
    Content body...
    """
    # Match frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        # No frontmatter — treat entire file as content
        return {
            "name": Path(source_path).stem,
            "description": "SKILL.md skill",
            "trigger": "",
            "tags": [],
            "category": "",
            "content": content.strip(),
            "source": source_path,
        }

    frontmatter_text = match.group(1)
    body = match.group(2).strip()

    # Simple YAML-like parser (no external dependency)
    frontmatter = _parse_simple_yaml(frontmatter_text)

    skill = {
        "name": frontmatter.get("name", Path(source_path).stem),
        "description": frontmatter.get("description", frontmatter.get("desc", "")),
        "trigger": frontmatter.get("trigger", frontmatter.get("triggers", "")),
        "tags": frontmatter.get("tags", frontmatter.get("tag", [])),
        "category": frontmatter.get("category", frontmatter.get("categories", "")),
        "content": body,
        "source": source_path,
    }

    # Normalize tags to list
    if isinstance(skill["tags"], str):
        skill["tags"] = [t.strip() for t in skill["tags"].strip("[]").split(",") if t.strip()]

    return skill


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Parse a minimal YAML-like frontmatter into a dict."""
    result = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            # Parse lists
            if value.startswith("[") and value.endswith("]"):
                items = [x.strip().strip("'\"") for x in value[1:-1].split(",") if x.strip()]
                result[key] = items
            elif value.lower() in ("true", "yes"):
                result[key] = True
            elif value.lower() in ("false", "no"):
                result[key] = False
            else:
                result[key] = value.strip("'\"")
        elif ":" in line:
            # Multi-line value continuation
            pass
    return result


# ------------------------------------------------------------------
# SKILL.md Indexer
# ------------------------------------------------------------------

class SkillMdIndexer:
    """Downloads SKILL.md repos and indexes them into ChromaDB."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.collection_name = SKILL_MD_COLLECTION
        self._collection = None
        self._embedding_service = None
        self._init_chromadb()

    def _init_chromadb(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(name=SKILL_MD_COLLECTION)

            from rag.embeddings import EmbeddingService
            self._embedding_service = EmbeddingService()
        except ImportError:
            logger.error("chromadb is not installed. SkillMdIndexer disabled.")

    def install_repo(self, github_repo: str) -> str:
        """Download a SKILL.md repo and index all SKILL.md files."""
        if self.collection is None:
            return "Error: ChromaDB no está disponible."

        cache_dir = Path(self.db_path).parent / "skillmd_cache" / github_repo.replace("/", "__")
        dest_dir = cache_dir / "repo"

        sha = self._download_repo(github_repo, dest_dir)
        if not sha:
            return f"Error: No se pudo descargar {github_repo}."

        # Find and index all SKILL.md files
        skills_found = []
        for skill_file in dest_dir.rglob("*"):
            if skill_file.is_file() and (
                skill_file.name.lower() == "skill.md" or skill_file.name.lower().endswith(".skill.md")
            ):
                try:
                    content = skill_file.read_text(encoding="utf-8", errors="ignore")
                    parsed = parse_skill_md(content, str(skill_file))
                    if parsed:
                        skills_found.append(parsed)
                except Exception as e:
                    logger.error(f"Error parsing {skill_file}: {e}")

        if not skills_found:
            # Fallback: index all markdown files
            logger.info(f"No SKILL.md files found in {github_repo}, indexing all .md files")
            for md_file in dest_dir.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                    parsed = parse_skill_md(content, str(md_file))
                    if parsed:
                        skills_found.append(parsed)
                except Exception as e:
                    logger.error(f"Error reading {md_file}: {e}")

        if not skills_found:
            return f"No se encontraron SKILL.md ni archivos .md en {github_repo}."

        # Index into ChromaDB
        texts = [s["content"] for s in skills_found]
        metadatas = [
            {
                "name": s["name"],
                "description": s["description"][:200],
                "trigger": s.get("trigger", ""),
                "tags": ",".join(s.get("tags", [])),
                "category": s.get("category", ""),
                "source": s["source"],
                "github_repo": github_repo,
            }
            for s in skills_found
        ]
        ids = []
        for i, s in enumerate(skills_found):
            import hashlib
            doc_id = hashlib.md5(f"{s['source']}_{i}".encode()).hexdigest()
            ids.append(doc_id)

        try:
            embeddings = self._embedding_service.get_embeddings(texts) if self._embedding_service else None
            if embeddings:
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids,
                )
            else:
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids,
                )
        except Exception as e:
            logger.error(f"Failed to index skills: {e}")
            return f"Error al indexar skills: {e}"

        # Save state
        state = {
            "github_repo": github_repo,
            "last_commit_sha": sha,
            "skills_count": len(skills_found),
        }
        state_path = cache_dir / ".state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Indexed {len(skills_found)} skills from {github_repo}")
        return (
            f"Repositorio SKILL.md '{github_repo}' indexado con éxito "
            f"({len(skills_found)} skills en colección '{SKILL_MD_COLLECTION}').\n"
            f"Usá 'search_skill_md' para buscar skills disponibles."
        )

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the SKILL.md collection."""
        if self.collection is None:
            return []

        query_embedding = self._embedding_service.get_embedding(query) if self._embedding_service else None
        if not query_embedding:
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            formatted = []
            if results and results.get("documents") and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                    formatted.append({
                        "text": results["documents"][0][i],
                        "metadata": {
                            "name": meta.get("name", "?"),
                            "description": meta.get("description", ""),
                            "trigger": meta.get("trigger", ""),
                            "tags": meta.get("tags", ""),
                            "category": meta.get("category", ""),
                            "source": meta.get("source", ""),
                            "github_repo": meta.get("github_repo", ""),
                        },
                        "distance": results["distances"][0][i] if results.get("distances") else 0.0,
                    })
            return formatted
        except Exception as e:
            logger.error(f"Skill search failed: {e}")
            return []

    def count(self) -> int:
        if self.collection is None:
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _win_retry_rmtree(path: Path, max_retries: int = 5, delay: float = 0.5) -> None:
        """Remove a directory tree with retries for Windows file locking."""
        import time
        for attempt in range(max_retries):
            try:
                shutil.rmtree(path)
                return
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    logger.warning(f"Could not remove {path} after {max_retries} attempts (Windows lock)")
                    # Last resort: try to rename it so it's at least out of the way
                    try:
                        orphan = path.parent / f"_orphan_{path.name}_{int(time.time())}"
                        os.rename(str(path), str(orphan))
                    except Exception:
                        pass

    def _download_repo(self, github_repo: str, dest_dir: Path) -> str | None:
        import time as _time
        api_url = f"https://api.github.com/repos/{github_repo}/commits?per_page=1"
        req = urllib.request.Request(api_url, headers={"User-Agent": "JARVIS-SkillMd-Adapter"})

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                commits = json.loads(response.read().decode("utf-8"))
                if not commits:
                    return None
                latest_sha = commits[0]["sha"]
        except Exception as e:
            logger.error(f"Failed to fetch commits for {github_repo}: {e}")
            return None

        zip_url = f"https://api.github.com/repos/{github_repo}/zipball"
        zip_req = urllib.request.Request(zip_url, headers={"User-Agent": "JARVIS-SkillMd-Adapter"})

        try:
            with urllib.request.urlopen(zip_req, timeout=60) as response:
                zip_data = response.read()
        except Exception as e:
            logger.error(f"Failed to download {github_repo}: {e}")
            return None

        # Use copy-based approach to avoid Windows cross-device rename issues
        try:
            temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
            if temp_dir.exists():
                self._win_retry_rmtree(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                self._win_retry_rmtree(temp_dir)
                return None

            top_dir = extracted_dirs[0]
            if dest_dir.exists():
                self._win_retry_rmtree(dest_dir)
            _time.sleep(0.2)  # Let OS release file handles
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Use copytree + rmtree instead of move to avoid Windows rename issues
            for item in top_dir.iterdir():
                dest_item = dest_dir / item.name
                if item.is_dir():
                    shutil.copytree(str(item), str(dest_item), dirs_exist_ok=True)
                else:
                    shutil.copy2(str(item), str(dest_item))

            _time.sleep(0.1)
            self._win_retry_rmtree(temp_dir)
            return latest_sha
        except Exception as e:
            logger.exception(f"Error extracting {github_repo}")
            temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
            if temp_dir.exists():
                self._win_retry_rmtree(temp_dir)
            return None
