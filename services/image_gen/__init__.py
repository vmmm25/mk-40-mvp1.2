"""MARK XL — Image Generation services (local SD + cloud)."""

from __future__ import annotations

from .base import ImageGenerator
from .local_sd import StableDiffusionLocal
from .gemini_gen import GeminiImageGen

__all__ = [
    "ImageGenerator",
    "StableDiffusionLocal",
    "GeminiImageGen",
]
