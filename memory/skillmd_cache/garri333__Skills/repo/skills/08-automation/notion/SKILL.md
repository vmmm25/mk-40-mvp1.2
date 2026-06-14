---
name: notion
version: 1.0.0
description: API de Notion para crear y gestionar páginas, bases de datos y bloques. Usa cuando necesites leer, escribir o sincronizar datos con Notion desde el agente.
tags: [notion, productivity, api, database, pages, wiki, notes]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Notion Skill

## Configuración

```bash
# pip install notion-client
# Variables de entorno
NOTION_API_KEY=secret_...               # De https://www.notion.so/my-integrations
NOTION_DATABASE_ID=your-database-id    # ID de la base de datos
```

## Setup de la integración

```
1. Ir a https://www.notion.so/my-integrations
2. Crear nueva integración (Internal / Public)
3. Copiar el "Internal Integration Token" → NOTION_API_KEY
4. En la página/base de datos de Notion: "..." → "Connections" → añadir tu integración
5. Copiar el ID de la URL: notion.so/[workspace]/[DATABASE_ID]?...
```

## Cliente base

```python
from notion_client import Client
import os

notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
```

## Bases de datos — CRUD

```python
# ── LEER ──────────────────────────────────────────────────────────────────
def query_database(
    database_id: str,
    filter: dict = None,
    sorts: list = None,
    page_size: int = 100,
) -> list:
    """Consultar una base de datos con filtros y ordenación"""
    params = {"database_id": database_id, "page_size": page_size}
    if filter:
        params["filter"] = filter
    if sorts:
        params["sorts"] = sorts
    
    results = notion.databases.query(**params)
    return results["results"]


# Ejemplo: filtrar tareas no completadas, ordenadas por fecha
tasks = query_database(
    DATABASE_ID,
    filter={
        "property": "Status",
        "select": {"does_not_equal": "Done"}
    },
    sorts=[{"property": "Due Date", "direction": "ascending"}]
)


def get_database_schema(database_id: str) -> dict:
    """Ver las propiedades disponibles en una base de datos"""
    db = notion.databases.retrieve(database_id=database_id)
    return {k: v["type"] for k, v in db["properties"].items()}


# ── CREAR ─────────────────────────────────────────────────────────────────
def create_page(
    database_id: str,
    title: str,
    properties: dict = None,
    children: list = None,
) -> dict:
    """Crear una nueva entrada en una base de datos"""
    page_properties = {
        "Name": {
            "title": [{"text": {"content": title}}]
        }
    }
    
    if properties:
        page_properties.update(properties)
    
    params = {
        "parent": {"database_id": database_id},
        "properties": page_properties,
    }
    
    if children:
        params["children"] = children
    
    return notion.pages.create(**params)


# Ejemplo: crear tarea con propiedades
create_page(
    DATABASE_ID,
    title="Revisar PR #42",
    properties={
        "Status": {"select": {"name": "In Progress"}},
        "Priority": {"select": {"name": "High"}},
        "Due Date": {"date": {"start": "2025-02-01"}},
        "Tags": {"multi_select": [{"name": "review"}, {"name": "urgent"}]},
        "Assignee": {"people": [{"id": "user-id"}]},
    }
)


# ── ACTUALIZAR ────────────────────────────────────────────────────────────
def update_page(page_id: str, properties: dict) -> dict:
    return notion.pages.update(page_id=page_id, properties=properties)


# Marcar tarea como completada
update_page(
    page_id="page-id-here",
    properties={"Status": {"select": {"name": "Done"}}}
)
```

## Páginas — contenido

```python
# ── LEER CONTENIDO DE UNA PÁGINA ──────────────────────────────────────────
def get_page_content(page_id: str) -> str:
    """Extraer texto de los bloques de una página"""
    blocks = notion.blocks.children.list(block_id=page_id)
    
    text_parts = []
    for block in blocks["results"]:
        block_type = block["type"]
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            rich_texts = block[block_type].get("rich_text", [])
            text_parts.append("".join(t["plain_text"] for t in rich_texts))
        elif block_type == "bulleted_list_item":
            rich_texts = block[block_type].get("rich_text", [])
            text = "".join(t["plain_text"] for t in rich_texts)
            text_parts.append(f"• {text}")
        elif block_type == "to_do":
            checked = block["to_do"]["checked"]
            rich_texts = block["to_do"].get("rich_text", [])
            text = "".join(t["plain_text"] for t in rich_texts)
            text_parts.append(f"{'✅' if checked else '☐'} {text}")
    
    return "\n".join(text_parts)


# ── AÑADIR CONTENIDO A UNA PÁGINA ─────────────────────────────────────────
def append_to_page(page_id: str, blocks: list) -> dict:
    return notion.blocks.children.append(block_id=page_id, children=blocks)


# Helpers para crear bloques
def paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading_2(text: str) -> dict:
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}

def code_block(code: str, language: str = "python") -> dict:
    return {"object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": code}}], "language": language}}


# Uso
append_to_page(PAGE_ID, [
    heading_2("Resumen del análisis"),
    paragraph("Los datos muestran una tendencia positiva..."),
    bullet("Métrica 1: 42% mejora"),
    bullet("Métrica 2: -15% errores"),
    divider(),
    code_block("df.describe()", "python"),
])
```

## Exportar base de datos a datos usables

```python
import pandas as pd

def database_to_dataframe(database_id: str) -> pd.DataFrame:
    """Convertir una base de datos Notion a DataFrame de pandas"""
    pages = query_database(database_id)
    rows = []
    
    for page in pages:
        row = {"id": page["id"]}
        for prop_name, prop_value in page["properties"].items():
            prop_type = prop_value["type"]
            
            if prop_type == "title":
                row[prop_name] = "".join(t["plain_text"] for t in prop_value["title"])
            elif prop_type == "rich_text":
                row[prop_name] = "".join(t["plain_text"] for t in prop_value["rich_text"])
            elif prop_type == "select":
                row[prop_name] = prop_value["select"]["name"] if prop_value["select"] else None
            elif prop_type == "multi_select":
                row[prop_name] = [s["name"] for s in prop_value["multi_select"]]
            elif prop_type == "date":
                row[prop_name] = prop_value["date"]["start"] if prop_value["date"] else None
            elif prop_type == "checkbox":
                row[prop_name] = prop_value["checkbox"]
            elif prop_type == "number":
                row[prop_name] = prop_value["number"]
            elif prop_type == "url":
                row[prop_name] = prop_value["url"]
            elif prop_type == "email":
                row[prop_name] = prop_value["email"]
        
        rows.append(row)
    
    return pd.DataFrame(rows)
```

## Referencias
- [Notion API docs](https://developers.notion.com/) — Documentación oficial
- [notion-client Python](https://github.com/ramnes/notion-sdk-py) — SDK no oficial pero completo
- [Notion Block types](https://developers.notion.com/reference/block) — Todos los tipos de bloques
