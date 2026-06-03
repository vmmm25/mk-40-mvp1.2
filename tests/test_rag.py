"""Tests for the RAG subsystem — embeddings, indexer, retriever, loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from rag.document_loader import DocumentLoader
from rag.embeddings import EmbeddingService
from rag.indexer import DocumentIndexer
from rag.retriever import DocumentRetriever


# ======================================================================
# DocumentLoader
# ======================================================================


class TestDocumentLoader:
    def test_unsupported_extension(self, tmp_path: Path):
        f = tmp_path / "test.xyz"
        f.write_text("hello", encoding="utf-8")
        loader = DocumentLoader()
        result = loader.load(f)
        assert result == []

    def test_load_text(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("Hello World", encoding="utf-8")
        loader = DocumentLoader()
        chunks = loader.load(f)
        assert len(chunks) >= 1
        assert "Hello World" in chunks[0]["text"]

    def test_load_markdown(self, tmp_path: Path):
        f = tmp_path / "readme.md"
        f.write_text("# Title\n\nContent here.", encoding="utf-8")
        loader = DocumentLoader()
        chunks = loader.load(f)
        assert len(chunks) >= 1
        assert "# Title" in chunks[0]["text"]

    def test_load_python(self, tmp_path: Path):
        f = tmp_path / "script.py"
        f.write_text("def hello():\n    print('hi')", encoding="utf-8")
        loader = DocumentLoader()
        chunks = loader.load(f)
        assert len(chunks) >= 1
        assert "def hello()" in chunks[0]["text"]

    def test_chunk_text_overlap(self):
        loader = DocumentLoader()
        text = "A" * 1200
        chunks = loader._chunk_text(text, chunk_size=500, overlap=100)
        assert len(chunks) == 3
        assert len(chunks[0]) == 500
        assert len(chunks[-1]) <= 500

    def test_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        loader = DocumentLoader()
        chunks = loader.load(f)
        assert all(c["text"] == "" for c in chunks) or chunks == []


# ======================================================================
# EmbeddingService (unit, Ollama backend)
# ======================================================================


class TestEmbeddingService:
    def test_empty_texts(self):
        svc = EmbeddingService(use_ollama=True)
        assert svc.get_embeddings([]) == []

    def test_single_text_returns_vector(self):
        svc = EmbeddingService(use_ollama=True)
        # Without a running Ollama server the call returns []
        embs = svc.get_embeddings(["hello"])
        assert len(embs) == 1
        assert isinstance(embs[0], list)

    def test_embedding_cache(self):
        svc = EmbeddingService(use_ollama=True)
        svc.get_embeddings(["abc"])
        svc._text_cache.clear()
        assert len(svc._text_cache) == 0

    def test_clear_cache(self):
        svc = EmbeddingService(use_ollama=True)
        svc._text_cache[hash("x")] = [0.1, 0.2]
        svc.clear_cache()
        assert len(svc._text_cache) == 0

    def test_get_embedding_single(self):
        svc = EmbeddingService(use_ollama=True)
        emb = svc.get_embedding("foo")
        assert isinstance(emb, list)
        assert hash("foo") in svc._text_cache


# ======================================================================
# DocumentIndexer (ChromaDB absent → graceful fallback)
# ======================================================================


class TestDocumentIndexer:
    def test_indexer_disabled_when_chromadb_missing(self):
        indexer = DocumentIndexer(db_path=":memory:")
        assert indexer.collection is None
        assert indexer.index_file(Path("nope.txt")) == 0

    def test_index_directory_empty(self, tmp_path: Path):
        indexer = DocumentIndexer(db_path=":memory:")
        indexer.collection = None
        assert indexer.index_directory(tmp_path) == 0

    def test_delete_document_no_chromadb(self):
        indexer = DocumentIndexer(db_path=":memory:")
        indexer.collection = None
        assert indexer.delete_document("/some/path") == -1

    def test_stats_no_chromadb(self):
        indexer = DocumentIndexer(db_path=":memory:")
        indexer.collection = None
        stats = indexer.stats()
        assert stats["collection"] is None
        assert "error" in stats

    def test_generate_id(self):
        indexer = DocumentIndexer(db_path=":memory:")
        id1 = indexer._generate_id("/a.txt", 0)
        id2 = indexer._generate_id("/a.txt", 0)
        id3 = indexer._generate_id("/a.txt", 1)
        assert id1 == id2  # deterministic
        assert id1 != id3  # different chunk → different id


# ======================================================================
# DocumentRetriever (unit, no real ChromaDB)
# ======================================================================


class TestDocumentRetriever:
    def test_no_chromadb(self):
        retriever = DocumentRetriever(db_path=":memory:")
        retriever.collection = None
        assert retriever.search("hello") == []
        assert retriever.count() == 0

    def test_empty_query_embedding(self, monkeypatch: pytest.MonkeyPatch):
        retriever = DocumentRetriever(db_path=":memory:")
        monkeypatch.setattr(
            retriever.embedding_service, "get_embedding", lambda text: []
        )
        assert retriever.search("anything") == []
