"""MARK XL — Gemini Image Generation (via Gemini 2.0 Flash / Imagen)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class GeminiImageGen:
    """Generate images using Gemini 2.0 Flash / Imagen API.

    Requires a valid Gemini API key configured in ``config/api_keys.json``
    under the key ``gemini_api_key``.
    """

    def __init__(self) -> None:
        self._client = None
        self._init_client()

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
        """Generate images using Gemini's Imagen capability."""
        if not self._client:
            logger.error("Gemini client not initialised")
            return []

        # Gemini 2.0 Flash currently generates one image per call
        # and doesn't support style params directly — we embed style into prompt
        full_prompt = prompt
        if style:
            full_prompt = f"[Style: {style}] {prompt}"

        try:
            # The google-genai library uses live generation for images
            response = self._client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=full_prompt,
                config={
                    "response_modalities": ["Text", "Image"],
                },
            )

            images: List[bytes] = []
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        images.append(part.inline_data.data)

            if not images:
                logger.warning("Gemini returned no image data for: %s", prompt[:60])

            logger.info("Gemini generated %d image(s)", len(images))
            return images

        except Exception as exc:
            logger.error("Gemini image generation failed: %s", exc)
            return []

    def is_available(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_client(self) -> None:
        """Initialise the Gemini client from config."""
        try:
            from google import genai
        except ImportError:
            logger.error("google-genai library not installed")
            return

        try:
            from memory.config_manager import get_config
            config = get_config()
            api_key = config.get("gemini_api_key", "")
            if not api_key:
                logger.warning("Gemini API key not configured")
                return
            self._client = genai.Client(api_key=api_key)
            logger.info("Gemini image-gen client initialised")
        except Exception as exc:
            logger.error("Failed to init Gemini client: %s", exc)
