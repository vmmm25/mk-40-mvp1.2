"""MARK XL — OpenAI / DALL-E image generation via OpenRouter."""

from __future__ import annotations

import base64
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class OpenAIImageGen:
    """Generate images via DALL-E 3 (or other models) through OpenRouter.

    Uses the OpenRouter API so no direct OpenAI key is needed — the
    configured OpenRouter key is used instead.
    """

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._load_key()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        style: Optional[str] = None,
        size: Optional[str] = None,
        count: int = 1,
        **kwargs: Any,
    ) -> List[bytes]:
        """Generate image(s) via DALL-E 3 / OpenRouter."""
        if not self._api_key:
            logger.error("OpenRouter API key not configured")
            return []

        width, height = self._parse_size(size or "1024x1024")
        size_str = f"{width}x{height}"

        full_prompt = prompt
        if style:
            full_prompt = f"[{style}] {prompt}"

        import aiohttp

        payload = {
            "model": "openai/dall-e-3",
            "prompt": full_prompt,
            "n": min(count, 4),  # DALL-E max 4
            "size": size_str,
            "response_format": "b64_json",
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/images/generations",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error("OpenRouter image error %s: %s", resp.status, text)
                        return []
                    data = await resp.json()
                    images: List[bytes] = []
                    for item in data.get("data", []):
                        b64 = item.get("b64_json")
                        if b64:
                            images.append(base64.b64decode(b64))
                    logger.info("OpenRouter/DALL-E generated %d image(s)", len(images))
                    return images
        except Exception as exc:
            logger.error("OpenRouter image generation failed: %s", exc)
            return []

    def is_available(self) -> bool:
        return bool(self._api_key)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_key(self) -> None:
        try:
            from memory.config_manager import get_config
            config = get_config()
            self._api_key = config.get("openrouter_api_key", "")
        except Exception:
            pass

    @staticmethod
    def _parse_size(size: str) -> tuple[int, int]:
        try:
            parts = size.lower().split("x")
            return int(parts[0]), int(parts[1])
        except (IndexError, ValueError):
            return 1024, 1024
