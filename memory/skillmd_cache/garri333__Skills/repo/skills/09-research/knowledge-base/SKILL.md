---
name: knowledge-base
version: 1.0.0
description: Base de conocimiento vectorial para proyectos — indexa archivos, docs y código para búsqueda semántica instantánea. Usa cuando necesites que el agente "conozca" un proyecto entero o una colección de documentos y pueda responder preguntas sobre él.
tags: [knowledge-base, embeddings, rag, vector-search, lancedb, chromadb, semantic-search]
author: garri333
license: MIT
source: https://skills.sh/
---

# Knowledge Base Skill

## Cuándo usar esta skill

- Proyecto con muchos archivos y necesitas "preguntar" sobre el código
- Documentación extensa (manuales, PDFs, wikis) que el agente debe conocer
- Implementar un chatbot con conocimiento sobre tu empresa/producto
- Sistema de onboarding que responde preguntas sobre el proyecto
- Búsqueda semántica sobre notas, emails, transcripciones

## Arquitectura de una Knowledge Base

```
Documentos  →  Chunking  →  Embeddings  →  Vector DB  →  Búsqueda semántica
  (texto)      (trozos)    (OpenAI/local)  (LanceDB)     (query → top-k docs)
                                                              ↓
                                                        LLM + contexto = Respuesta
```

## Setup inicial con LanceDB (local, sin servidor)

```python
# pip install lancedb openai pypdf2 python-docx
import lancedb
import openai
import os
from pathlib import Path

# Configurar embedding
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed(texts: list[str]) -> list[list[float]]:
    """Generar embeddings con OpenAI text-embedding-3-small"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]

# Crear/conectar base de datos
db = lancedb.connect("./knowledge-base")
```

## Indexar un directorio de proyectos

```python
import hashlib
from typing import Generator

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Dividir texto en chunks con overlap"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks


def load_file(path: Path) -> str | None:
    """Cargar contenido de un archivo según su extensión"""
    try:
        suffix = path.suffix.lower()
        
        if suffix in [".txt", ".md", ".py", ".ts", ".js", ".json", ".yaml", ".yml", ".env.example"]:
            return path.read_text(encoding="utf-8")
        
        elif suffix == ".pdf":
            import PyPDF2
            reader = PyPDF2.PdfReader(str(path))
            return "\n".join(page.extract_text() for page in reader.pages)
        
        elif suffix in [".docx"]:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        
        return None
    
    except Exception as e:
        print(f"[warn] No se pudo leer {path}: {e}")
        return None


def index_directory(
    directory: str,
    db: lancedb.LanceDBConnection,
    table_name: str = "knowledge",
    exclude: list[str] = None,
    extensions: list[str] = None,
) -> int:
    """
    Indexar todos los archivos de un directorio.
    Retorna el número de chunks indexados.
    """
    exclude = exclude or ["node_modules", ".git", "__pycache__", ".venv", "dist", "build"]
    extensions = extensions or [".md", ".txt", ".py", ".ts", ".js", ".json", ".pdf", ".docx"]
    
    records = []
    
    for path in Path(directory).rglob("*"):
        # Saltar directorios excluidos
        if any(ex in path.parts for ex in exclude):
            continue
        
        if path.is_file() and path.suffix.lower() in extensions:
            content = load_file(path)
            if not content or len(content.strip()) < 50:
                continue
            
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                records.append({
                    "text": chunk,
                    "source": str(path),
                    "chunk_index": i,
                    "file_type": path.suffix.lower(),
                    "doc_id": hashlib.md5(f"{path}{i}".encode()).hexdigest(),
                })
    
    if not records:
        print("No se encontraron documentos para indexar.")
        return 0
    
    # Generar embeddings en lotes
    BATCH_SIZE = 100
    all_embeddings = []
    
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        texts = [r["text"] for r in batch]
        embeddings = embed(texts)
        all_embeddings.extend(embeddings)
        print(f"  Embeddings: {i + len(batch)}/{len(records)}")
    
    # Añadir embeddings a los records
    for record, embedding in zip(records, all_embeddings):
        record["vector"] = embedding
    
    # Crear/actualizar tabla en LanceDB
    if table_name in db.table_names():
        table = db.open_table(table_name)
        table.add(records)
    else:
        table = db.create_table(table_name, data=records)
    
    print(f"✅ {len(records)} chunks indexados desde {directory}")
    return len(records)
```

## Búsqueda semántica

```python
def search(
    query: str,
    db: lancedb.LanceDBConnection,
    table_name: str = "knowledge",
    top_k: int = 5,
    filter: str = None,  # Ej: "file_type = '.py'"
) -> list[dict]:
    """
    Buscar en la knowledge base por similitud semántica.
    """
    table = db.open_table(table_name)
    query_embedding = embed([query])[0]
    
    results = (
        table.search(query_embedding)
        .limit(top_k)
        .where(filter, prefilter=True) if filter else
        table.search(query_embedding).limit(top_k)
    ).to_list()
    
    # Deduplicar por source + chunk_index
    seen = set()
    unique_results = []
    for r in results:
        key = r["doc_id"]
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    return unique_results


def format_context(results: list[dict]) -> str:
    """Formatear resultados como contexto para el LLM"""
    context_parts = []
    
    for i, result in enumerate(results, 1):
        source = result["source"].replace("\\", "/")
        context_parts.append(
            f"[Fuente {i}: {source}]\n{result['text']}\n"
        )
    
    return "\n---\n".join(context_parts)
```

## Pipeline RAG completo (Retrieval-Augmented Generation)

```python
def answer_with_rag(
    question: str,
    db: lancedb.LanceDBConnection,
    table_name: str = "knowledge",
    system_prompt: str = None,
) -> str:
    """
    Responder una pregunta usando RAG sobre la knowledge base.
    """
    # 1. Recuperar contexto relevante
    results = search(question, db, table_name, top_k=5)
    context = format_context(results)
    
    if not results:
        return "No encontré información relevante en la knowledge base."
    
    # 2. Generar respuesta con contexto
    system = system_prompt or (
        "Eres un asistente experto en este proyecto. "
        "Responde SOLO basándote en el contexto dado. "
        "Si la información no está en el contexto, dilo claramente. "
        "Cita la fuente cuando uses información específica."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"Contexto de la knowledge base:\n\n{context}\n\n---\n\nPregunta: {question}"
            }
        ],
        temperature=0.1,  # Respuestas más fieles al contexto
    )
    
    return response.choices[0].message.content


# Uso
if __name__ == "__main__":
    db = lancedb.connect("./knowledge-base")
    
    # Primera vez: indexar
    index_directory("./my-project", db)
    
    # Responder preguntas
    answer = answer_with_rag(
        "¿Cómo se configura la autenticación en este proyecto?",
        db
    )
    print(answer)
```

## Alternativa con ChromaDB

```python
# pip install chromadb
import chromadb
from chromadb.utils import embedding_functions

# Usar embeddings de OpenAI
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

chroma_client = chromadb.PersistentClient(path="./chroma-db")
collection = chroma_client.get_or_create_collection(
    name="knowledge",
    embedding_function=openai_ef
)

# Añadir documentos
collection.add(
    documents=["Documento 1 content...", "Documento 2 content..."],
    ids=["doc1", "doc2"],
    metadatas=[{"source": "file1.md"}, {"source": "file2.md"}]
)

# Buscar
results = collection.query(
    query_texts=["¿Qué es X?"],
    n_results=5
)
```

## Alternativa local (sin API de OpenAI) con sentence-transformers

```python
# pip install sentence-transformers lancedb
from sentence_transformers import SentenceTransformer

# Modelo local — no requiere API key — 80MB en disco
model = SentenceTransformer("all-MiniLM-L6-v2")  # Rápido
# model = SentenceTransformer("BAAI/bge-m3")  # Multilingüe, mejor calidad

def embed_local(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, convert_to_numpy=True).tolist()
```

## CLI para gestionar la knowledge base

```python
# kb.py — gestión de knowledge base
import argparse

def main():
    parser = argparse.ArgumentParser(description="Knowledge Base manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcomando: index
    idx = subparsers.add_parser("index", help="Indexar directorio")
    idx.add_argument("directory", help="Directorio a indexar")
    idx.add_argument("--table", default="knowledge")
    idx.add_argument("--rebuild", action="store_true", help="Borrar y reconstruir")
    
    # Subcomando: search
    srch = subparsers.add_parser("search", help="Buscar en la knowledge base")
    srch.add_argument("query", help="Texto a buscar")
    srch.add_argument("--top-k", type=int, default=5)
    srch.add_argument("--table", default="knowledge")
    
    # Subcomando: ask
    ask = subparsers.add_parser("ask", help="Pregunta con RAG")
    ask.add_argument("question", help="Pregunta a responder")
    ask.add_argument("--table", default="knowledge")
    
    args = parser.parse_args()
    db = lancedb.connect("./knowledge-base")
    
    if args.command == "index":
        if args.rebuild and args.table in db.table_names():
            db.drop_table(args.table)
        index_directory(args.directory, db, args.table)
    
    elif args.command == "search":
        results = search(args.query, db, args.table, top_k=args.top_k)
        for r in results:
            print(f"\n[{r['source']}]\n{r['text'][:200]}...")
    
    elif args.command == "ask":
        answer = answer_with_rag(args.question, db, args.table)
        print(f"\n{answer}")

if __name__ == "__main__":
    main()
```

## Casos de uso comunes

```python
# 1. Knowledge base del proyecto (para onboarding)
index_directory("./my-project", db, table_name="project")
answer_with_rag("¿Qué framework se usa y por qué?", db, "project")

# 2. Knowledge base de documentación
index_directory("./docs", db, table_name="docs")
answer_with_rag("¿Cómo se hace un deploy a producción?", db, "docs")

# 3. Knowledge base personal (notas, emails)
index_directory("~/Obsidian", db, table_name="personal")
answer_with_rag("¿Qué decisiones tomé sobre X el año pasado?", db, "personal")

# 4. Búsqueda filtrada por tipo de archivo
results = search("autenticación JWT", db, filter="file_type = '.ts'")
```

## Referencias
- [LanceDB](https://lancedb.github.io/lancedb/) — Base de datos vectorial embebible
- [ChromaDB](https://docs.trychroma.com/) — Vector DB de código abierto
- [sentence-transformers](https://www.sbert.net/) — Embeddings locales de alta calidad
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/) — Framework para RAG
- [ByteRover](https://github.com/byterover) — Inspiración para gestión de knowledge
