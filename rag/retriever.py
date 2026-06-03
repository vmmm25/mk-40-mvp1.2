"""MARK XL — Document retriever for semantic search."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Semantic search over a ChromaDB vector collection.

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
            logger.error("chromadb is not installed. Retriever disabled.")

        self.embedding_service = EmbeddingService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic search and return ranked results."""
        if self.collection is None:
            return []

        query_embedding = self.embedding_service.get_embedding(query)
        if not query_embedding:
            logger.warning("Empty embedding for query: %s", query[:60])
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            formatted: List[Dict[str, Any]] = []
            if results and results.get("documents") and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted.append(
                        {
                            "text": results["documents"][0][i],
                            "metadata": (
                                results["metadatas"][0][i]
                                if results.get("metadatas")
                                else {}
                            ),
                            "distance": (
                                results["distances"][0][i]
                                if results.get("distances")
                                else 0.0
                            ),
                        }
                    )
            return formatted
        except Exception as exc:
            logger.error("Search failed for query=%s: %s", query[:60], exc)
            return []

    def count(self) -> int:
        """Return total chunk count in the collection."""
        if self.collection is None:
            return 0
        try:
            return self.collection.count()
        except Exception as exc:
            logger.error("count() failed: %s", exc)
            return 0
