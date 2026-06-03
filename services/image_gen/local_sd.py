"""MARK XL — Stable Diffusion local (Automatic1111 / ComfyUI API)."""

from __future__ import annotations

import base64
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# Style → positive prompt prefix mapping
STYLE_PREFIXES = {
    "realistic": "photorealistic, highly detailed, 8K, DSLR, ",
    "anime": "anime style, cel shaded, Studio Ghibli inspired, ",
    "cyberpunk": "cyberpunk, neon lights, futuristic city, dark rainy streets, ",
    "oil_painting": "oil painting, textured canvas, classical art style, ",
    "watercolor": "watercolor painting, soft washes, paper texture, ",
    "pixel_art": "pixel art, 8-bit, retro game style, low resolution, ",
}


class StableDiffusionLocal:
    """Generate images using a local Stable Diffusion API
    (Automatic1111 / SD WebUI or ComfyUI).

    Expects the SD WebUI to be running with ``--api`` enabled.
    """

    def __init__(self, api_url: str = "http://127.0.0.1:7860") -> None:
        self.api_url = api_url.rstrip("/")

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
        """Generate images via the SD WebUI API."""
        # Apply style prefix
        full_prompt = prompt
        if style and style.lower() in STYLE_PREFIXES:
            full_prompt = STYLE_PREFIXES[style.lower()] + prompt

        width, height = self._parse_size(size or "1024x1024")

        payload = {
            "prompt": full_prompt,
            "negative_prompt": kwargs.get(
                "negative_prompt", "nsfw, low quality, blurry, distorted"
            ),
            "steps": kwargs.get("steps", 30),
            "width": width,
            "height": height,
            "batch_size": count,
            "cfg_scale": kwargs.get("cfg_scale", 7.0),
        }

        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sdapi/v1/txt2img",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error("SD API error %s: %s", resp.status, text)
                        return []
                    data = await resp.json()
                    images_b64 = data.get("images", [])
                    result = [base64.b64decode(img) for img in images_b64]
                    logger.info(
                        "Generated %d image(s) via local SD (style=%s)",
                        len(result), style or "none",
                    )
                    return result
        except Exception as exc:
            logger.error("SD local generation failed: %s", exc)
            return []

    def is_available(self) -> bool:
        """Check if the SD WebUI is reachable."""
        import requests
        try:
            resp = requests.get(f"{self.api_url}/sdapi/v1/sd-models", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_size(size: str) -> tuple[int, int]:
        """Parse ``'WxH'`` string, defaulting to 1024x1024."""
        try:
            parts = size.lower().split("x")
            return int(parts[0]), int(parts[1])
        except (IndexError, ValueError):
            return 1024, 1024
