"""MARK XL — Generic SQL database client.

Supports PostgreSQL and MySQL/MariaDB connections via configuration.
Connection details are stored in ``config/database_connections.json``.

Example config::

    {
        "local_postgres": {
            "engine": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "postgres",
            "password": "secret"
        },
        "project_db": {
            "engine": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "project",
            "user": "root",
            "password": "secret"
        }
    }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Execute SQL queries on configured databases."""

    CONFIG_PATH = Path("config/database_connections.json")

    def __init__(self) -> None:
        self._connections: dict[str, dict[str, Any]] = {}
        self._load_config()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_connections(self) -> list[str]:
        """Return names of configured connections."""
        return list(self._connections.keys())

    def execute_query(self, connection_name: str, query: str) -> dict[str, Any]:
        """Execute a SQL query on a named connection.

        Returns::

            {"success": true, "columns": [...], "rows": [[...], ...]}
            or
            {"success": false, "error": "..."}
        """
        conn_info = self._connections.get(connection_name)
        if not conn_info:
            return {"success": False, "error": f"Unknown connection: {connection_name}"}

        engine = conn_info.get("engine", "").lower()

        if engine == "postgresql":
            return self._query_postgres(conn_info, query)
        elif engine == "mysql":
            return self._query_mysql(conn_info, query)
        else:
            return {"success": False, "error": f"Unsupported engine: {engine}"}

    def is_configured(self, connection_name: str) -> bool:
        """Check if a connection is configured."""
        return connection_name in self._connections

    # ------------------------------------------------------------------
    # Backends
    # ------------------------------------------------------------------

    def _query_postgres(self, conn: dict[str, Any], query: str) -> dict[str, Any]:
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            return {"success": False, "error": "psycopg2 not installed. Run: pip install psycopg2-binary"}

        try:
            conn_obj = psycopg2.connect(
                host=conn.get("host", "localhost"),
                port=conn.get("port", 5432),
                dbname=conn.get("database", ""),
                user=conn.get("user", ""),
                password=conn.get("password", ""),
                connect_timeout=10,
            )
            cursor = conn_obj.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("WITH"):
                rows = cursor.fetchall()
                columns = list(rows[0].keys()) if rows else []
                return {
                    "success": True,
                    "columns": columns,
                    "rows": [[r[col] for col in columns] for r in rows],
                    "row_count": len(rows),
                }
            else:
                conn_obj.commit()
                return {
                    "success": True,
                    "affected_rows": cursor.rowcount,
                }
        except Exception as exc:
            logger.error("PostgreSQL query error: %s", exc)
            return {"success": False, "error": str(exc)}
        finally:
            try:
                conn_obj.close()
            except Exception:
                pass

    def _query_mysql(self, conn: dict[str, Any], query: str) -> dict[str, Any]:
        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ImportError:
            return {"success": False, "error": "pymysql not installed. Run: pip install pymysql"}

        try:
            connection = pymysql.connect(
                host=conn.get("host", "localhost"),
                port=conn.get("port", 3306),
                database=conn.get("database", ""),
                user=conn.get("user", ""),
                password=conn.get("password", ""),
                connect_timeout=10,
                cursorclass=DictCursor,
            )
            with connection.cursor() as cursor:
                cursor.execute(query)
                if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("WITH"):
                    rows = cursor.fetchall()
                    columns = list(rows[0].keys()) if rows else []
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": [list(r.values()) for r in rows],
                        "row_count": len(rows),
                    }
                else:
                    connection.commit()
                    return {
                        "success": True,
                        "affected_rows": cursor.rowcount,
                    }
        except Exception as exc:
            logger.error("MySQL query error: %s", exc)
            return {"success": False, "error": str(exc)}
        finally:
            try:
                connection.close()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        if not self.CONFIG_PATH.exists():
            logger.info(
                "No database connections config at %s. "
                "Create it to enable database queries.", self.CONFIG_PATH
            )
            return
        try:
            self._connections = json.loads(self.CONFIG_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded %d database connection(s)", len(self._connections))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load database config: %s", exc)
