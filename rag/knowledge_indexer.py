"""MARK XL — Knowledge-Space Indexer.

Downloads and indexes knowledge repositories (like AnastasiyaW/knowledge-space)
into a dedicated ChromaDB collection for semantic search.
"""

from __future__ import annotations

import io
import json
import logging
import shutil
import zipfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

from .indexer import DocumentIndexer
from .retriever import DocumentRetriever

logger = logging.getLogger(__name__)

KNOWLEDGE_COLLECTION = "knowledge_space"
DEFAULT_DB_PATH = "./memory/vector_store"


class KnowledgeIndexer:
    """Downloads and indexes knowledge repos into a dedicated RAG collection."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.collection_name = KNOWLEDGE_COLLECTION
        self._indexer = DocumentIndexer(db_path=db_path, collection_name=KNOWLEDGE_COLLECTION)
        self._retriever = None  # lazy init

    def get_retriever(self) -> DocumentRetriever:
        if self._retriever is None:
            self._retriever = DocumentRetriever(db_path=self.db_path, collection_name=KNOWLEDGE_COLLECTION)
        return self._retriever

    # ------------------------------------------------------------------
    # Install knowledge repo from GitHub
    # ------------------------------------------------------------------

    def install_repo(self, github_repo: str, subdir: str | None = None) -> str:
        """Download a GitHub repo and index its markdown files into the knowledge collection.

        Args:
            github_repo: "owner/repo" format
            subdir: Optional subdirectory within the repo to index (e.g. "articles")

        Returns:
            Status message with chunk count.
        """
        cache_dir = Path(self.db_path).parent / "knowledge_cache" / github_repo.replace("/", "__")
        dest_dir = cache_dir / "repo"

        # Download fresh copy
        sha = self._download_repo(github_repo, dest_dir)
        if not sha:
            return f"Error: No se pudo descargar {github_repo}."

        # Determine what to index
        target = dest_dir
        if subdir:
            target = dest_dir / subdir
            if not target.exists():
                return f"Error: Subdirectorio '{subdir}' no encontrado en {github_repo}."

        # Index all .md files
        count = self._indexer.index_directory(target, pattern="*.md")
        if count == 0:
            count = self._indexer.index_directory(target, pattern="*.mdx")

        # Save state
        state = {"github_repo": github_repo, "last_commit_sha": sha, "subdir": subdir, "chunk_count": count}
        state_path = cache_dir / ".state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Indexed {count} chunks from {github_repo} into {KNOWLEDGE_COLLECTION}")
        return f"Repositorio '{github_repo}' indexado con éxito ({count} fragmentos en colección '{KNOWLEDGE_COLLECTION}')."

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge collection."""
        retriever = self.get_retriever()
        return retriever.search(query, n_results=n_results)

    def stats(self) -> dict:
        """Return collection statistics."""
        return self._indexer.stats()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _download_repo(self, github_repo: str, dest_dir: Path) -> str | None:
        """Download zipball from GitHub and extract."""
        api_url = f"https://api.github.com/repos/{github_repo}/commits?per_page=1"
        req = urllib.request.Request(api_url, headers={"User-Agent": "JARVIS-Knowledge-Indexer"})

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                commits = json.loads(response.read().decode("utf-8"))
                if not commits:
                    logger.error(f"No commits found for {github_repo}")
                    return None
                latest_sha = commits[0]["sha"]
        except Exception as e:
            logger.error(f"Failed to fetch commits for {github_repo}: {e}")
            return None

        zip_url = f"https://api.github.com/repos/{github_repo}/zipball"
        zip_req = urllib.request.Request(zip_url, headers={"User-Agent": "JARVIS-Knowledge-Indexer"})

        try:
            logger.info(f"Downloading zipball from {zip_url}...")
            with urllib.request.urlopen(zip_req, timeout=60) as response:
                zip_data = response.read()
        except Exception as e:
            logger.error(f"Failed to download zipball for {github_repo}: {e}")
            return None

        try:
            temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                logger.error(f"No folder found in zipball for {github_repo}")
                shutil.rmtree(temp_dir)
                return None

            top_dir = extracted_dirs[0]

            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            dest_dir.mkdir(parents=True, exist_ok=True)

            for item in top_dir.iterdir():
                shutil.move(str(item), str(dest_dir))

            shutil.rmtree(temp_dir)

            logger.info(f"Successfully downloaded {github_repo} at commit {latest_sha}")
            return latest_sha
        except Exception as e:
            logger.exception(f"Error extracting zipball for {github_repo}")
            temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None
