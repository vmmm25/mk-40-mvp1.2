"""MARK XL — Docker client wrapping common docker / docker-compose operations."""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DockerClient:
    """Execute Docker and Docker Compose commands via subprocess."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ps(self, all_containers: bool = False) -> list[dict[str, Any]]:
        """List containers."""
        args = ["ps", "-a"] if all_containers else ["ps"]
        output = self._run_docker(*args, "--format", "{{json .}}")
        return self._parse_json_lines(output)

    def list_containers(self, all_containers: bool = False) -> str:
        """Human-readable container list."""
        containers = self.ps(all_containers=all_containers)
        if not containers:
            return "No containers found."
        lines = []
        for c in containers:
            status = c.get("Status", "?")
            name = c.get("Names", "?")
            image = c.get("Image", "?")
            ports = c.get("Ports", "")
            lines.append(f"  {name} ({image}) — {status}  {ports}")
        return "Containers:\n" + "\n".join(lines)

    def start(self, container: str) -> str:
        """Start a container."""
        output = self._run_docker("start", container)
        return f"Container '{container}' started." if output else f"Failed to start '{container}'."

    def stop(self, container: str) -> str:
        """Stop a container."""
        output = self._run_docker("stop", container)
        return f"Container '{container}' stopped." if output else f"Failed to stop '{container}'."

    def restart(self, container: str) -> str:
        """Restart a container."""
        output = self._run_docker("restart", container)
        return f"Container '{container}' restarted." if output else f"Failed to restart '{container}'."

    def logs(self, container: str, tail: int = 50) -> str:
        """Fetch container logs."""
        return self._run_docker("logs", "--tail", str(tail), container)

    def stats(self) -> str:
        """Live container resource stats."""
        return self._run_docker("stats", "--no-stream", "--format", "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}")

    def compose_up(self, compose_file: str | None = None) -> str:
        """Run ``docker-compose up -d``."""
        args = ["compose", "up", "-d"]
        if compose_file:
            args = ["compose", "-f", compose_file, "up", "-d"]
        return self._run_docker(*args)

    def compose_down(self, compose_file: str | None = None) -> str:
        """Run ``docker-compose down``."""
        args = ["compose", "down"]
        if compose_file:
            args = ["compose", "-f", compose_file, "down"]
        return self._run_docker(*args)

    def is_available(self) -> bool:
        """Check if Docker CLI is reachable."""
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.ServerVersion}}"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_docker(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                error = result.stderr.strip()
                logger.error("Docker error: %s", error)
                return f"Error: {error}"
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Error: Docker command timed out."
        except FileNotFoundError:
            return "Error: Docker is not installed or not in PATH."
        except Exception as exc:
            logger.error("Docker exception: %s", exc)
            return f"Error: {exc}"

    @staticmethod
    def _parse_json_lines(output: str) -> list[dict[str, Any]]:
        if not output or output.startswith("Error"):
            return []
        lines = output.strip().split("\n")
        result = []
        for line in lines:
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return result
