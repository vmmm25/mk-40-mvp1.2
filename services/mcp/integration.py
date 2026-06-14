import logging
import asyncio
import json
import shlex
from typing import Any
from memory.config_manager import load_config
from services.mcp.server import MCPServerManager
from tools.declarations import TOOL_DECLARATIONS
from tools import TOOL_IMPLEMENTATIONS

logger = logging.getLogger(__name__)

# Global singleton to prevent reconnecting on engine restarts
_mcp_manager = None
_mcp_initialized = False

def _uppercase_types(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    out = {}
    for k, v in schema.items():
        if k == "type" and isinstance(v, str):
            out[k] = v.upper()
        elif isinstance(v, dict):
            out[k] = _uppercase_types(v)
        elif isinstance(v, list):
            out[k] = [_uppercase_types(i) for i in v]
        else:
            out[k] = v
    return out

async def init_mcp_servers(ui: Any):
    global _mcp_manager, _mcp_initialized
    
    if _mcp_initialized:
        return
        
    cfg = load_config()
    servers = cfg.get("mcp_servers", {})
    if not servers:
        return
        
    if _mcp_manager is None:
        _mcp_manager = MCPServerManager()
        
    logger.info("Initializing MCP Servers...")
    ui.write_log("SYS: Inicializando servidores MCP...")
    
    for name, config in servers.items():
        command = config.get("command")
        if not command:
            continue
        args = config.get("args", [])
        # Defensive: if args is a string (common config mistake), split it properly
        if isinstance(args, str):
            args = shlex.split(args)
        env = config.get("env", None)
        
        ui.write_log(f"SYS: Conectando a servidor MCP '{name}'...")
        success = await _mcp_manager.connect(name, command, args, env)
        if success:
            logger.info(f"Connected to MCP Server: {name}")
            ui.write_log(f"SYS: MCP '{name}' conectado exitosamente.")
        else:
            logger.error(f"Failed to connect to MCP Server: {name}")
            ui.write_log(f"SYS: Error al conectar MCP '{name}'.")
            
    tools = await _mcp_manager.list_all_tools()
    
    added_count = 0
    for t in tools:
        server_name = t.get("_mcp_server", "")
        tool_name = f"mcp_{server_name}_{t['name']}".replace("-", "_")
        
        if tool_name in TOOL_IMPLEMENTATIONS:
            continue
            
        raw_schema = t.get("inputSchema", {})
        parameters = _uppercase_types(raw_schema)
        if "type" not in parameters:
            parameters["type"] = "OBJECT"
            
        decl = {
            "name": tool_name,
            "description": t.get("description", f"Tool {t['name']} from MCP server {server_name}"),
            "parameters": parameters
        }
        
        TOOL_DECLARATIONS.append(decl)
        
        # Factory function to capture closure variables correctly
        def make_handler(srv, tname):
            async def handler(args: dict, ui_obj: Any = None) -> str:
                res = await _mcp_manager.call_tool(srv, tname, args)
                if isinstance(res, dict) and "error" in res:
                    return f"Error: {res['error']}"
                    
                if isinstance(res, dict) and "content" in res:
                    texts = []
                    for c in res["content"]:
                        if c.get("type") == "text":
                            texts.append(c.get("text", ""))
                    if texts:
                        return "\n".join(texts)
                return json.dumps(res, ensure_ascii=False)
            return handler
            
        TOOL_IMPLEMENTATIONS[tool_name] = make_handler(server_name, t['name'])
        added_count += 1
        
    _mcp_initialized = True
    if added_count > 0:
        logger.info(f"Injected {added_count} MCP tools into engine.")
        ui.write_log(f"SYS: {added_count} herramientas MCP inyectadas nativamente.")
