import io
import json
import logging
import os
import shutil
import zipfile
import urllib.request
import urllib.error
from pathlib import Path

logger = logging.getLogger(__name__)


def check_update(github_repo: str, current_sha: str) -> dict:
    """Checks if there's a newer commit on GitHub than current_sha.

    Returns a dict with:
      - 'update_available': bool
      - 'latest_sha': str
      - 'error': str or None
    """
    api_url = f"https://api.github.com/repos/{github_repo}/commits?per_page=1"
    req = urllib.request.Request(api_url, headers={"User-Agent": "JARVIS-Skills-Manager"})
    try:
        # Timeout after 10 seconds to avoid blocking startup
        with urllib.request.urlopen(req, timeout=10) as response:
            commits = json.loads(response.read().decode("utf-8"))
            if not commits:
                return {"update_available": False, "latest_sha": "", "error": "No commits found"}
            latest_sha = commits[0]["sha"]
            return {
                "update_available": latest_sha != current_sha,
                "latest_sha": latest_sha,
                "error": None,
            }
    except Exception as e:
        logger.warning(f"Failed to check updates for {github_repo}: {e}")
        return {"update_available": False, "latest_sha": "", "error": str(e)}


def download_and_extract_skill(github_repo: str, dest_dir: Path) -> str | None:
    """Downloads the zipball for the given github_repo (e.g. 'owner/repo'),

    extracts its contents, and places them into dest_dir.
    Returns the latest commit SHA if successful, otherwise None.
    """
    # 1. Fetch latest commit SHA
    api_url = f"https://api.github.com/repos/{github_repo}/commits?per_page=1"
    req = urllib.request.Request(api_url, headers={"User-Agent": "JARVIS-Skills-Manager"})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            commits = json.loads(response.read().decode("utf-8"))
            if not commits:
                logger.error(f"No commits found for repository {github_repo}")
                return None
            latest_sha = commits[0]["sha"]
    except Exception as e:
        logger.error(f"Failed to fetch commits for {github_repo}: {e}")
        return None

    # 2. Download zipball
    zip_url = f"https://api.github.com/repos/{github_repo}/zipball"
    zip_req = urllib.request.Request(zip_url, headers={"User-Agent": "JARVIS-Skills-Manager"})

    try:
        logger.info(f"Downloading zipball from {zip_url}...")
        with urllib.request.urlopen(zip_req, timeout=30) as response:
            zip_data = response.read()
    except Exception as e:
        logger.error(f"Failed to download zipball for {github_repo}: {e}")
        return None

    try:
        # Create temporary extraction folder
        temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Extract zip
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the single top-level directory in the extracted zip
        extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            logger.error(f"No folder found in zipball for {github_repo}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None

        top_dir = extracted_dirs[0]

        # Clean destination directory if it exists
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Move files from top_dir to dest_dir
        for item in top_dir.iterdir():
            shutil.move(str(item), str(dest_dir))

        # Remove temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        # Write .git_state.json
        state = {"last_commit_sha": latest_sha, "github_repo": github_repo}
        with open(dest_dir / ".git_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Successfully installed/updated {github_repo} to {dest_dir} at commit {latest_sha}")
        return latest_sha
    except Exception as e:
        logger.exception(f"Error extracting zipball for {github_repo}")
        # Clean up temp folder just in case
        temp_dir = dest_dir.parent / f"_temp_{dest_dir.name}"
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
        return None
