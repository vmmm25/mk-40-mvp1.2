"""MARK XL — Embedding service (local SBERT / Ollama) with optional caching."""

from __future__ import annotations

import logging
from typing import List, Optional

try:
    from functools import lru_cache
except ImportError:
    from functools import lru_cache  # noqa: F811 — always available in 3.14

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate text embeddings via local SentenceTransformers or Ollama.

    Parameters
    ----------
    model_name : str
        SentenceTransformers model name (default ``all-MiniLM-L6-v2``)
        or Ollama embedding model (``nomic-embed-text``).
    use_ollama : bool
        Force Ollama backend even if sentence-transformers is installed.
    ollama_url : str
        Base URL for the Ollama API.
    cache_size : int
        Maximum number of (text → embedding) results to memoize in-memory.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_ollama: bool = False,
        ollama_url: str = "http://localhost:11434",
        cache_size: int = 512,
    ) -> None:
        self.use_ollama = use_ollama
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self._model = None  # lazy-loaded SBERT

        # Simple in-memory LRU cache for individual text → embedding
        self._text_cache: dict[int, List[float]] = {}
        self._cache_max = cache_size

        if not self.use_ollama:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(model_name)
                logger.info("Loaded local SentenceTransformer model: %s", model_name)
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed; falling back to Ollama."
                )
                self.use_ollama = True
                self.model_name = "nomic-embed-text"

    # ------------------------------------------------------------------
    # Public API — synchronous
    # ------------------------------------------------------------------

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for a batch of texts."""
        if not texts:
            return []

        if self.use_ollama:
            return self._get_ollama_embeddings(texts)
        return self._get_local_embeddings(texts)

    def get_embedding(self, text: str) -> List[float]:
        """Return a single embedding (cached)."""
        key = hash(text)
        cached = self._text_cache.get(key)
        if cached is not None:
            return cached

        emb = self.get_embeddings([text])[0]
        if len(self._text_cache) < self._cache_max:
            self._text_cache[key] = emb
        return emb

    def clear_cache(self) -> None:
        """Reset the in-memory text embedding cache."""
        self._text_cache.clear()

    # ------------------------------------------------------------------
    # Backends
    # ------------------------------------------------------------------

    def _get_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self._model is None:
            logger.error("Local model not loaded; returning empty embeddings.")
            return [[] for _ in texts]
        try:
            return self._model.encode(texts).tolist()
        except Exception as exc:
            logger.error("Local embedding failed: %s", exc)
            return [[] for _ in texts]

    def _get_ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        import requests

        embeddings: List[List[float]] = []
        for text in texts:
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=10,
                )
                if resp.status_code == 200:
                    emb = resp.json().get("embedding", [])
                else:
                    logger.error(
                        "Ollama embedding error: %s — %s", resp.status_code, resp.text
                    )
                    emb = []
                embeddings.append(emb)
            except requests.RequestException as exc:
                logger.error("Ollama embedding connection error: %s", exc)
                embeddings.append([])
        return embeddings
