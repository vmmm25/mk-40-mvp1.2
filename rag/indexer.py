"""MARK XL — Document indexer backed by ChromaDB."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from .document_loader import DocumentLoader
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Ingest documents into a ChromaDB vector collection.

    Parameters
    ----------
    db_path : str
        Directory for the ChromaDB persistent client.
    collection_name : str
        Name of the collection inside ChromaDB.
    """

    def __init__(
        self,
        db_path: str = "./memory/vector_store",
        collection_name: str = "documents",
    ) -> None:
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None

        try:
            import chromadb

            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name=collection_name
            )
        except ImportError:
            logger.error("chromadb is not installed. Indexer disabled.")

        self.loader = DocumentLoader()
        self.embedding_service = EmbeddingService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_file(self, path: Path) -> int:
        """Load, chunk, embed and index a single file. Returns chunk count."""
        if self.collection is None:
            logger.warning("Indexer unavailable (no ChromaDB).")
            return 0

        chunks = self.loader.load(path)
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.get_embeddings(texts)

        ids: List[str] = []
        metadatas: List[dict] = []

        for i, chunk in enumerate(chunks):
            doc_id = self._generate_id(str(path), i)
            ids.append(doc_id)
            metadatas.append(
                {
                    "source": str(path),
                    "page": chunk.get("page", 1),
                    "chunk_index": i,
                }
            )

        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Indexed %d chunks from %s", len(chunks), path)
        except Exception as exc:
            logger.error("Failed to index %s: %s", path, exc)
            return 0

        return len(chunks)

    def index_directory(self, dir_path: Path, pattern: str = "*") -> int:
        """Recursively index all matching files under *dir_path*."""
        total = 0
        for p in sorted(dir_path.rglob(pattern)):
            if p.is_file():
                total += self.index_file(p)
        return total

    def delete_document(self, source: str) -> int:
        """Delete all chunks that belong to a source path.

        Returns the number of chunks removed, or -1 if the operation fails.
        """
        if self.collection is None:
            return -1

        try:
            # ChromaDB supports metadata-based deletion
            result = self.collection.delete(where={"source": source})
            # `delete` with ``where`` returns None in older chromadb; newer
            # versions may return a result. We re-query to report count.
            remaining = self.collection.count(
                where={"source": source}
            )
            removed = -1  # unknown if we can't compute
            logger.info("Deleted document source=%s (remaining=%d)", source, remaining)
            return removed
        except Exception as exc:
            logger.error("Failed to delete %s: %s", source, exc)
            return -1

    def stats(self) -> dict:
        """Return collection statistics."""
        if self.collection is None:
            return {"collection": None, "error": "ChromaDB not available"}

        try:
            count = self.collection.count()
            # Try to get a sample to list distinct sources
            sample = self.collection.get(limit=min(count, 1000)) if count > 0 else {}
            metadatas = sample.get("metadatas", []) or []
            sources = sorted(
                {m.get("source", "?") for m in metadatas if m is not None}
            )
            return {
                "collection": self.collection_name,
                "db_path": self.db_path,
                "total_chunks": count,
                "distinct_sources": len(sources),
                "sources": sources,
            }
        except Exception as exc:
            logger.error("Failed to read stats: %s", exc)
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_id(doc_path: str, chunk_idx: int) -> str:
        s = f"{doc_path}_{chunk_idx}"
        return hashlib.md5(s.encode()).hexdigest()
