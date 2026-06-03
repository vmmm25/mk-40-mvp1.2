"""MARK XL — MCP (Model Context Protocol) Server Manager.

Manages external MCP server processes and exposes their tools
to the agent as dynamic tool declarations.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manage connections to MCP server processes for dynamic tools.

    MCP servers are long-lived subprocesses that communicate via
    JSON-RPC over ``stdin/stdout``.
    """

    def __init__(self) -> None:
        self._servers: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    async def connect(
        self,
        name: str,
        command: str,
        args: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
    ) -> bool:
        """Start and connect to an MCP server process.

        Parameters
        ----------
        name : str
            Unique identifier for this server.
        command : str
            Executable path.
        args : list of str, optional
            Command-line arguments.
        env : dict, optional
            Extra environment variables.

        Returns
        -------
        bool
            True if the server started successfully.
        """
        if name in self._servers:
            logger.warning("MCP server '%s' already connected", name)
            return True

        try:
            process = await asyncio.create_subprocess_exec(
                command,
                *(args or []),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**self._base_env(), **(env or {})},
            )
            self._servers[name] = {
                "process": process,
                "tools": [],
                "command": command,
                "args": args or [],
            }
            # Discover available tools
            tools = await self._list_tools(name)
            self._servers[name]["tools"] = tools
            logger.info(
                "MCP server '%s' connected — %d tool(s) available",
                name, len(tools),
            )
            return True
        except Exception as exc:
            logger.error("Failed to connect MCP server '%s': %s", name, exc)
            return False

    async def disconnect(self, name: str) -> bool:
        """Stop an MCP server."""
        server = self._servers.pop(name, None)
        if server is None:
            return False
        try:
            server["process"].terminate()
            await asyncio.wait_for(server["process"].wait(), timeout=5)
            logger.info("MCP server '%s' disconnected", name)
        except asyncio.TimeoutError:
            server["process"].kill()
            logger.warning("MCP server '%s' killed (timeout)", name)
        return True

    async def disconnect_all(self) -> None:
        """Stop all connected MCP servers."""
        for name in list(self._servers.keys()):
            await self.disconnect(name)

    # ------------------------------------------------------------------
    # Tool discovery & execution
    # ------------------------------------------------------------------

    async def list_all_tools(self) -> list[dict[str, Any]]:
        """Aggregate tools from all connected MCP servers."""
        all_tools: list[dict[str, Any]] = []
        for name, server in self._servers.items():
            for tool in server.get("tools", []):
                tool["_mcp_server"] = name
                all_tools.append(tool)
        return all_tools

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a tool on a specific MCP server via JSON-RPC."""
        server = self._servers.get(server_name)
        if server is None:
            return {"error": f"Unknown MCP server: {server_name}"}

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        try:
            process = server["process"]
            if process.stdin is None or process.stdout is None:
                return {"error": "Server process pipes not available"}

            request_bytes = (json.dumps(request) + "\n").encode("utf-8")
            process.stdin.write(request_bytes)
            await process.stdin.drain()

            response_bytes = await asyncio.wait_for(
                process.stdout.readline(), timeout=30
            )
            response = json.loads(response_bytes.decode("utf-8"))

            if "error" in response:
                return {"error": response["error"]["message"]}
            return response.get("result", {})
        except asyncio.TimeoutError:
            return {"error": "MCP tool call timed out"}
        except Exception as exc:
            logger.error("MCP tool call failed: %s", exc)
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # JSON-RPC helpers
    # ------------------------------------------------------------------

    async def _list_tools(self, name: str) -> list[dict[str, Any]]:
        """Request the list of tools from an MCP server."""
        server = self._servers.get(name)
        if server is None:
            return []

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
        }

        try:
            process = server["process"]
            if process.stdin is None or process.stdout is None:
                return []

            request_bytes = (json.dumps(request) + "\n").encode("utf-8")
            process.stdin.write(request_bytes)
            await process.stdin.drain()

            response_bytes = await asyncio.wait_for(
                process.stdout.readline(), timeout=10
            )
            response = json.loads(response_bytes.decode("utf-8"))

            if "error" in response:
                logger.error("MCP list_tools error for '%s': %s", name, response["error"])
                return []
            return response.get("result", {}).get("tools", [])
        except asyncio.TimeoutError:
            logger.warning("MCP list_tools timed out for '%s'", name)
            return []
        except Exception as exc:
            logger.error("MCP list_tools exception for '%s': %s", name, exc)
            return []

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Return a snapshot of all connected servers."""
        return {
            name: {
                "tools": len(srv.get("tools", [])),
                "command": srv.get("command"),
                "running": srv.get("process", None) is not None
                and srv["process"].returncode is None,
            }
            for name, srv in self._servers.items()
        }

    def is_connected(self, name: str) -> bool:
        return name in self._servers

    @staticmethod
    def _base_env() -> dict[str, str]:
        """Return base environment with PATH etc."""
        import os
        return dict(os.environ)
