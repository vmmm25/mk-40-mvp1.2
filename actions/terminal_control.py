import subprocess
import os

def terminal_control(parameters: dict, player=None) -> str:
    """
    Ejecuta comandos en la terminal (PowerShell por defecto en Windows)
    y devuelve la salida estándar y de error.
    """
    command = parameters.get("command", "")
    timeout = parameters.get("timeout", 60)
    
    if not command:
        return "Error: No command provided."
        
    if player:
        player.write_log(f"[Terminal] Executing: {command[:50]}...")
        
    try:
        # En Windows usamos powershell por defecto
        # Se ejecuta con shell=True para poder encadenar comandos o usar built-ins
        result = subprocess.run(
            ["powershell", "-Command", command] if os.name == "nt" else ["bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False # ya estamos llamando al shell directamente
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        response = ""
        if output:
            response += f"Output:\n{output}\n"
        if error:
            response += f"Error:\n{error}\n"
            
        if not response:
            response = "Command executed successfully with no output."
            
        # Truncate if too long to avoid flooding the context
        if len(response) > 4000:
            response = response[:4000] + "\n...[Output truncated]"
            
        return response
        
    except subprocess.TimeoutExpired:
        return f"Error: Command execution timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
