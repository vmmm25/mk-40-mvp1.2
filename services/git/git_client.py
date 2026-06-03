"""MARK XL — Git client wrapping common git operations."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class GitClient:
    """Execute common Git operations via subprocess."""

    def __init__(self, repo_path: str | Path | None = None) -> None:
        self.repo_path = Path(repo_path).resolve() if repo_path else Path.cwd()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def status(self) -> str:
        """Return ``git status`` output."""
        return self._run_git("status")

    def log(self, count: int = 10) -> str:
        """Return recent commit log."""
        return self._run_git("log", f"--oneline -{count}")

    def diff(self, staged: bool = False) -> str:
        """Return working-tree or staged diff."""
        return self._run_git("diff", "--cached" if staged else "")

    def add(self, paths: str | list[str] = ".") -> str:
        """Stage file(s)."""
        if isinstance(paths, list):
            return self._run_git("add", *paths)
        return self._run_git("add", paths)

    def commit(self, message: str) -> str:
        """Create a commit."""
        return self._run_git("commit", "-m", message)

    def push(self, remote: str = "origin", branch: str | None = None) -> str:
        """Push to remote."""
        args = ["push", remote]
        if branch:
            args.append(branch)
        return self._run_git(*args)

    def pull(self, remote: str = "origin", branch: str | None = None) -> str:
        """Pull from remote."""
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return self._run_git(*args)

    def branch(self, name: str | None = None) -> str:
        """List branches or create a new one."""
        if name:
            return self._run_git("branch", name)
        return self._run_git("branch", "-a")

    def checkout(self, branch: str) -> str:
        """Switch branch."""
        return self._run_git("checkout", branch)

    def merge(self, branch: str) -> str:
        """Merge *branch* into current."""
        return self._run_git("merge", branch)

    def clone(self, url: str, dest: str | Path | None = None) -> str:
        """Clone a repository."""
        args = ["clone", url]
        if dest:
            args.append(str(dest))
        return self._run_git(*args)

    def is_git_repo(self) -> bool:
        """Check if the current path is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_git(self, *args: str) -> str:
        try:
            filtered = [a for a in args if a]  # remove empty strings
            result = subprocess.run(
                ["git", *filtered],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout.strip()
            if result.returncode != 0:
                error = result.stderr.strip()
                logger.error("Git error: %s", error)
                return f"Error: {error}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Git command timed out."
        except FileNotFoundError:
            return "Error: Git is not installed or not in PATH."
        except Exception as exc:
            logger.error("Git exception: %s", exc)
            return f"Error: {exc}"

    def __repr__(self) -> str:
        return f"<GitClient repo={self.repo_path}>"
