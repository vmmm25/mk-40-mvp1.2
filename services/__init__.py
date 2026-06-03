"""MARK XL — External services (Email, Calendar, Image Gen, Media, Git, Docker, Database, MCP)."""

from __future__ import annotations

# Import submodules so they are available when services is imported
from . import email
from . import calendar
from . import image_gen
from . import media
from . import git
from . import docker
from . import database
from . import mcp

__all__ = [
    "email",
    "calendar",
    "image_gen",
    "media",
    "git",
    "docker",
    "database",
    "mcp",
]
