---
name: mcp-porter
version: 1.0.0
description: Discover, configure, install, and call MCP (Model Context Protocol) servers directly. Manage your MCP server registry, auth, and tool calls from the command line or Python scripts.
tags: [mcp, model-context-protocol, tools, ai-agents, claude, copilot, cursor, servers]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# MCP Porter Skill

## What is MCP?

Model Context Protocol (MCP) is an open standard by Anthropic that lets AI models connect to external tools, APIs, and data sources. An MCP server exposes "tools" that AI assistants can call.

## Install MCP Tools

```bash
# Core MCP library
pip install mcp

# mcpx — MCP server runner (Cloudflare/Anthropic)
npm install -g @modelcontextprotocol/cli

# uvx — run MCP servers without install
pip install uv

# Popular MCP servers
uvx mcp-server-fetch          # Web fetching
uvx mcp-server-filesystem     # File system access
uvx mcp-server-github         # GitHub integration
uvx mcp-server-postgres       # PostgreSQL queries
uvx mcp-server-sqlite         # SQLite access
uvx mcp-server-slack          # Slack integration
uvx mcp-server-puppeteer      # Browser automation
```

## Configure MCP in Claude Desktop

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "/path/to/allowed/dir"]
    },
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    },
    "postgres": {
      "command": "uvx",
      "args": ["mcp-server-postgres", "postgresql://user:pass@localhost/db"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

## Configure MCP in VS Code (GitHub Copilot)

```json
// .vscode/mcp.json (workspace) or settings.json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github-token",
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ],
  "servers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github-token}"
      }
    },
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "${workspaceFolder}"]
    }
  }
}
```

## Configure MCP in Cursor

```json
// ~/.cursor/mcp.json
{
  "mcpServers": {
    "deepwiki": {
      "command": "uvx",
      "args": ["mcp-deepwiki"]
    },
    "context7": {
      "command": "uvx",
      "args": ["context7-mcp"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

## Python: Connect to an MCP Server Programmatically

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def list_mcp_tools(server_command: str, server_args: list[str], env: dict = None):
    """List all tools available from an MCP server."""
    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env=env
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                }
                for t in tools.tools
            ]

async def call_mcp_tool(
    server_command: str,
    server_args: list[str],
    tool_name: str,
    arguments: dict,
    env: dict = None
):
    """Call a specific tool on an MCP server."""
    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env=env
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result.content

# Example: Use fetch MCP server to get a webpage
async def fetch_url(url: str) -> str:
    result = await call_mcp_tool(
        server_command="uvx",
        server_args=["mcp-server-fetch"],
        tool_name="fetch",
        arguments={"url": url}
    )
    return result[0].text if result else ""

# Run it:
content = asyncio.run(fetch_url("https://modelcontextprotocol.io/"))
print(content[:500])
```

## Build a Custom MCP Server

```python
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
import mcp.types as types

app = Server("my-custom-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Declare available tools."""
    return [
        Tool(
            name="weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="calculate",
            description="Evaluate a math expression",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression like '2 + 2'"}
                },
                "required": ["expression"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "weather":
        city = arguments["city"]
        import httpx
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://wttr.in/{city}?format=3")
            return [TextContent(type="text", text=res.text)]
    
    elif name == "calculate":
        expr = arguments["expression"]
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="my-custom-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

Register custom server:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/my_server.py"]
    }
  }
}
```

## MCP Server Registry — Popular Servers

```python
MCP_REGISTRY = {
    "fetch":      {"package": "mcp-server-fetch",    "purpose": "Fetch web pages/APIs"},
    "filesystem": {"package": "mcp-server-filesystem","purpose": "Read/write local files"},
    "github":     {"package": "mcp-server-github",   "purpose": "GitHub repos, PRs, issues"},
    "postgres":   {"package": "mcp-server-postgres",  "purpose": "PostgreSQL queries"},
    "sqlite":     {"package": "mcp-server-sqlite",    "purpose": "SQLite database"},
    "slack":      {"package": "mcp-server-slack",     "purpose": "Slack messages, channels"},
    "puppeteer":  {"package": "mcp-server-puppeteer", "purpose": "Browser automation"},
    "memory":     {"package": "@modelcontextprotocol/server-memory", "purpose": "Persistent memory"},
    "deepwiki":   {"package": "mcp-deepwiki",         "purpose": "GitHub repo Q&A"},
    "context7":   {"package": "context7-mcp",         "purpose": "Up-to-date library docs"},
    "sequential-thinking": {"package": "mcp-server-sequential-thinking", "purpose": "Chain of thought"},
}

def get_install_command(server_name: str) -> str:
    info = MCP_REGISTRY.get(server_name)
    if not info:
        return f"Server '{server_name}' not found in registry"
    return f"uvx {info['package']}"
```

## Discover Tools on a Running Server

```python
async def explore_server(command: str, args: list[str], env: dict = None):
    """Full exploration of an MCP server's capabilities."""
    tools = await list_mcp_tools(command, args, env)
    
    print(f"\n{'='*50}")
    print(f"MCP Server: {command} {' '.join(args)}")
    print(f"Available tools: {len(tools)}")
    print('='*50)
    
    for t in tools:
        print(f"\n  [{t['name']}]")
        print(f"  {t['description']}")
        schema = t.get("input_schema", {})
        props = schema.get("properties", {})
        if props:
            print(f"  Parameters: {', '.join(props.keys())}")
    
    return tools

# Explore the fetch server:
asyncio.run(explore_server("uvx", ["mcp-server-fetch"]))
```

## References
- [MCP Official Docs](https://modelcontextprotocol.io/) — Full protocol spec
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — Python library
- [MCP Servers Repo](https://github.com/modelcontextprotocol/servers) — Official server catalog
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) — Community list
- [Claude MCP Setup](https://docs.anthropic.com/en/docs/claude-desktop) — Claude Desktop guide
