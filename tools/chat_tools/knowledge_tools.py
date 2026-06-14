"""Tools for installing and searching knowledge-space repos via ChromaDB RAG."""
from typing import Any
from tools.base import BaseTool


class SearchKnowledgeTool(BaseTool):
    name = "search_knowledge"
    description = """Searches the knowledge-space collection for technical articles, concepts, and reference material across 26 domains (programming, AI, math, science, history, etc.). Use this when the user asks about technical concepts, how things work, or wants reference information."""
    parameters = {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query for technical knowledge",
            },
            "n_results": {
                "type": "INTEGER",
                "description": "Number of results to return (default: 5)",
            },
        },
        "required": ["query"],
    }

    def execute(self, args: dict, ui: Any) -> str:
        query = args.get("query", "")
        n_results = args.get("n_results", 5)
        if not query:
            return "No query provided."

        try:
            from rag.knowledge_indexer import KnowledgeIndexer
            indexer = KnowledgeIndexer()
            results = indexer.search(query, n_results=n_results)
            if not results:
                return "No se encontraron resultados en la base de conocimiento. Probá con search_documents o web_search."

            lines = [f"📚 Resultados de búsqueda en knowledge-space:"]
            for i, r in enumerate(results, 1):
                source = r["metadata"].get("source", "Unknown")
                # Truncate source path for readability
                source_short = source.split("knowledge_cache")[-1].strip("/\\") if "knowledge_cache" in source else source
                lines.append(f"\n--- Resultado {i} ---")
                lines.append(f"Fuente: {source_short}")
                lines.append(r["text"][:500])
                if len(r["text"]) > 500:
                    lines.append("... (truncado)")

            return "\n".join(lines)
        except Exception as e:
            return f"Error searching knowledge: {e}"


class InstallKnowledgeRepoTool(BaseTool):
    name = "install_knowledge_repo"
    description = """Downloads a GitHub repository and indexes all its markdown files into the knowledge-space RAG collection for semantic search. Use this to install new knowledge bases."""
    parameters = {
        "type": "OBJECT",
        "properties": {
            "github_repo": {
                "type": "STRING",
                "description": "GitHub repository in 'owner/repo' format (e.g. 'AnastasiyaW/knowledge-space')",
            },
            "subdir": {
                "type": "STRING",
                "description": "Optional subdirectory within the repo to index (e.g. 'articles')",
            },
        },
        "required": ["github_repo"],
    }

    def execute(self, args: dict, ui: Any) -> str:
        github_repo = args.get("github_repo", "").strip()
        subdir = args.get("subdir")

        if not github_repo:
            return "Error: Se requiere el parámetro 'github_repo'."

        if "github.com/" in github_repo:
            github_repo = github_repo.split("github.com/")[-1]
        parts = github_repo.split("/")
        if len(parts) < 2:
            return f"Formato inválido: {github_repo}. Debe ser 'owner/repo'."
        owner = parts[-2]
        repo = parts[-1].replace(".git", "")
        clean_repo = f"{owner}/{repo}"

        try:
            from rag.knowledge_indexer import KnowledgeIndexer
            indexer = KnowledgeIndexer()
            result = indexer.install_repo(clean_repo, subdir=subdir)
            stats = indexer.stats()
            if stats.get("collection"):
                total = stats.get("total_chunks", 0)
                result += f"\n\nTotal en colección: {total} fragmentos."
            return result
        except Exception as e:
            return f"Error al instalar repositorio de conocimiento: {e}"
