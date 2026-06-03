"""MARK XL — Retrieval-Augmented Generation (RAG) subsystem.

Provides document ingestion, embedding, vector storage, and semantic
retrieval backed by ChromaDB.
"""

from .document_loader import DocumentLoader
from .embeddings import EmbeddingService
from .indexer import DocumentIndexer
from .retriever import DocumentRetriever

__all__ = [
    "DocumentLoader",
    "EmbeddingService",
    "DocumentIndexer",
    "DocumentRetriever",
]
