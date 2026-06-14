"""MARK XL — Model Registry with capability badges + rotation metadata.

Single source of truth for every model's capabilities across all providers.
Each model carries structured flags so the SmartRouter can pick the best
model for each turn based on intent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Capability Flags ─────────────────────────────────────────────────────────

@dataclass
class ModelCapabilities:
    """What a model can do."""
    tools: bool = False       # Tool / function calling
    vision: bool = False      # Image input / multimodal
    reasoning: bool = False   # Chain-of-thought / deep thinking
    coding: bool = False      # Code generation specialist


@dataclass
class ModelInfo:
    """Full metadata for a single model entry."""
    id: str                          # API model ID, e.g. "qwen/qwen3-coder:free"
    name: str                        # Short display name, e.g. "Qwen 3 Coder"
    provider: str = "openrouter"     # "openrouter" | "gemini" | "ollama" | "lmstudio"
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    speed: str = "medium"            # "fast" | "medium" | "slow"
    strength: str = "medium"         # "small" | "medium" | "large"
    notes: str = ""                  # Optional context (uncensored, preview, etc.)

    # ── Badge string ────────────────────────────────────────────────────
    def badge(self) -> str:
        parts = []
        if self.capabilities.tools:      parts.append("🛠️")
        if self.capabilities.vision:     parts.append("👁️")
        if self.capabilities.reasoning:  parts.append("🧠")
        if self.capabilities.coding:     parts.append("💻")
        return "".join(parts) if parts else ""

    def display_name(self) -> str:
        b = self.badge()
        return f"{b} {self.name}" if b else self.name


# ── OpenRouter Free Models ──────────────────────────────────────────────────

OPENROUTER_MODELS: dict[str, ModelInfo] = {
    # ── DeepSeek ──
    "deepseek/deepseek-r1:free": ModelInfo(
        id="deepseek/deepseek-r1:free", name="DeepSeek R1",
        capabilities=ModelCapabilities(tools=True, reasoning=True, coding=True),
        speed="slow", strength="large", notes="Reasoning specialist",
    ),
    "deepseek/deepseek-r1-distill-llama-70b:free": ModelInfo(
        id="deepseek/deepseek-r1-distill-llama-70b:free", name="DeepSeek R1 Llama 70B",
        capabilities=ModelCapabilities(tools=True, reasoning=True, coding=True),
        speed="slow", strength="large", notes="Reasoning distilled",
    ),

    # ── Google Gemini ──
    "google/gemini-2.0-pro-exp-02-05:free": ModelInfo(
        id="google/gemini-2.0-pro-exp-02-05:free", name="Gemini 2.0 Pro Exp",
        capabilities=ModelCapabilities(tools=True, vision=True, coding=True),
        speed="medium", strength="large",
    ),
    "google/gemini-2.0-flash-thinking-exp:free": ModelInfo(
        id="google/gemini-2.0-flash-thinking-exp:free", name="Gemini 2.0 Flash Thinking",
        capabilities=ModelCapabilities(tools=True, vision=True, reasoning=True, coding=True),
        speed="fast", strength="large", notes="Vision + reasoning",
    ),
    "google/gemini-2.0-flash-lite-preview-02-05:free": ModelInfo(
        id="google/gemini-2.0-flash-lite-preview-02-05:free", name="Gemini 2.0 Flash Lite",
        capabilities=ModelCapabilities(tools=True, vision=True),
        speed="fast", strength="medium",
    ),

    # ── Google Gemma ──
    "google/gemma-2-9b-it:free": ModelInfo(
        id="google/gemma-2-9b-it:free", name="Gemma 2 9B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="small",
    ),
    "google/gemma-4-26b-a4b-it:free": ModelInfo(
        id="google/gemma-4-26b-a4b-it:free", name="Gemma 4 26B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="fast", strength="medium",
    ),
    "google/gemma-4-31b-it:free": ModelInfo(
        id="google/gemma-4-31b-it:free", name="Gemma 4 31B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large",
    ),

    # ── Google Lyria ──
    "google/lyria-3-pro-preview": ModelInfo(
        id="google/lyria-3-pro-preview", name="Lyria 3 Pro",
        capabilities=ModelCapabilities(tools=True, vision=True),
        speed="medium", strength="large", notes="Preview",
    ),
    "google/lyria-3-clip-preview": ModelInfo(
        id="google/lyria-3-clip-preview", name="Lyria 3 Clip",
        capabilities=ModelCapabilities(tools=True, vision=True),
        speed="fast", strength="medium", notes="Preview",
    ),

    # ── Meta Llama ──
    "meta-llama/llama-3.3-70b-instruct:free": ModelInfo(
        id="meta-llama/llama-3.3-70b-instruct:free", name="Llama 3.3 70B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large", notes="Best general",
    ),
    "meta-llama/llama-3.2-3b-instruct:free": ModelInfo(
        id="meta-llama/llama-3.2-3b-instruct:free", name="Llama 3.2 3B",
        capabilities=ModelCapabilities(),
        speed="fast", strength="small",
    ),
    "meta-llama/llama-3.1-8b-instruct:free": ModelInfo(
        id="meta-llama/llama-3.1-8b-instruct:free", name="Llama 3.1 8B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="small",
    ),

    # ── NVIDIA / Nemotron ──
    "nvidia/llama-3.1-nemotron-70b-instruct:free": ModelInfo(
        id="nvidia/llama-3.1-nemotron-70b-instruct:free", name="Nemotron 70B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large",
    ),
    "nvidia/nemotron-3-super-120b-a12b:free": ModelInfo(
        id="nvidia/nemotron-3-super-120b-a12b:free", name="Nemotron 3 Super 120B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="slow", strength="large",
    ),
    "nvidia/nemotron-3-nano-30b-a3b:free": ModelInfo(
        id="nvidia/nemotron-3-nano-30b-a3b:free", name="Nemotron 3 Nano 30B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="medium",
    ),
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": ModelInfo(
        id="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", name="Nemotron 3 Nano Omni",
        capabilities=ModelCapabilities(tools=True, reasoning=True, coding=True),
        speed="medium", strength="medium", notes="Reasoning",
    ),
    "nvidia/nemotron-nano-12b-v2-vl:free": ModelInfo(
        id="nvidia/nemotron-nano-12b-v2-vl:free", name="Nemotron Nano 12B VL",
        capabilities=ModelCapabilities(tools=True, vision=True),
        speed="fast", strength="medium", notes="Vision model",
    ),
    "nvidia/nemotron-nano-9b-v2:free": ModelInfo(
        id="nvidia/nemotron-nano-9b-v2:free", name="Nemotron Nano 9B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="small",
    ),

    # ── Qwen ──
    "qwen/qwen-2.5-72b-instruct:free": ModelInfo(
        id="qwen/qwen-2.5-72b-instruct:free", name="Qwen 2.5 72B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="slow", strength="large",
    ),
    "qwen/qwen-2.5-coder-32b-instruct:free": ModelInfo(
        id="qwen/qwen-2.5-coder-32b-instruct:free", name="Qwen 2.5 Coder 32B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large", notes="Coding specialist",
    ),
    "qwen/qwen3-next-80b-a3b-instruct:free": ModelInfo(
        id="qwen/qwen3-next-80b-a3b-instruct:free", name="Qwen 3 Next 80B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large",
    ),
    "qwen/qwen3-coder:free": ModelInfo(
        id="qwen/qwen3-coder:free", name="Qwen 3 Coder 480B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="slow", strength="large", notes="Coding specialist",
    ),

    # ── Mistral ──
    "mistralai/mistral-small-24b-instruct-2501:free": ModelInfo(
        id="mistralai/mistral-small-24b-instruct-2501:free", name="Mistral Small 24B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="medium",
    ),
    "mistralai/mistral-7b-instruct:free": ModelInfo(
        id="mistralai/mistral-7b-instruct:free", name="Mistral 7B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="small",
    ),

    # ── NousResearch ──
    "nousresearch/hermes-3-llama-3.1-405b:free": ModelInfo(
        id="nousresearch/hermes-3-llama-3.1-405b:free", name="Hermes 3 405B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="slow", strength="large",
    ),

    # ── Dolphin ──
    "cognitivecomputations/dolphin3.0-r1-mistral-24b:free": ModelInfo(
        id="cognitivecomputations/dolphin3.0-r1-mistral-24b:free", name="Dolphin 3.0 R1 24B",
        capabilities=ModelCapabilities(tools=True, reasoning=True, coding=True),
        speed="medium", strength="medium", notes="Uncensored",
    ),
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free": ModelInfo(
        id="cognitivecomputations/dolphin-mistral-24b-venice-edition:free", name="Dolphin Mistral 24B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="medium", notes="Uncensored",
    ),

    # ── Specialised / others ──
    "openchat/openchat-7b:free": ModelInfo(
        id="openchat/openchat-7b:free", name="OpenChat 7B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="fast", strength="small",
    ),
    "huggingfaceh4/zephyr-7b-beta:free": ModelInfo(
        id="huggingfaceh4/zephyr-7b-beta:free", name="Zephyr 7B",
        capabilities=ModelCapabilities(),
        speed="fast", strength="small",
    ),
    "openrouter/owl-alpha": ModelInfo(
        id="openrouter/owl-alpha", name="Owl Alpha",
        capabilities=ModelCapabilities(tools=True, vision=True, coding=True),
        speed="medium", strength="large", notes="Preview",
    ),

    # ── Poolside (coding) ──
    "poolside/laguna-xs.2:free": ModelInfo(
        id="poolside/laguna-xs.2:free", name="Laguna XS.2",
        capabilities=ModelCapabilities(coding=True),
        speed="fast", strength="small", notes="Coding",
    ),
    "poolside/laguna-m.1:free": ModelInfo(
        id="poolside/laguna-m.1:free", name="Laguna M.1",
        capabilities=ModelCapabilities(coding=True),
        speed="medium", strength="medium", notes="Coding",
    ),

    # ── Moonshot ──
    "moonshotai/kimi-k2.6:free": ModelInfo(
        id="moonshotai/kimi-k2.6:free", name="Kimi K2.6",
        capabilities=ModelCapabilities(tools=True, reasoning=True, coding=True),
        speed="medium", strength="large",
    ),

    # ── Liquid ──
    "liquid/lfm-2.5-1.2b-thinking:free": ModelInfo(
        id="liquid/lfm-2.5-1.2b-thinking:free", name="LFM 2.5 1.2B Think",
        capabilities=ModelCapabilities(reasoning=True),
        speed="fast", strength="small", notes="Tiny reasoning",
    ),
    "liquid/lfm-2.5-1.2b-instruct:free": ModelInfo(
        id="liquid/lfm-2.5-1.2b-instruct:free", name="LFM 2.5 1.2B",
        capabilities=ModelCapabilities(),
        speed="fast", strength="small",
    ),

    # ── OpenAI OSS ──
    "openai/gpt-oss-120b:free": ModelInfo(
        id="openai/gpt-oss-120b:free", name="GPT-OSS 120B",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="slow", strength="large",
    ),
    "openai/gpt-oss-20b:free": ModelInfo(
        id="openai/gpt-oss-20b:free", name="GPT-OSS 20B",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="medium",
    ),

    # ── Z.ai ──
    "z-ai/glm-4.5-air:free": ModelInfo(
        id="z-ai/glm-4.5-air:free", name="GLM 4.5 Air",
        capabilities=ModelCapabilities(tools=True),
        speed="fast", strength="medium",
    ),

    # ── Router ──
    "openrouter/free": ModelInfo(
        id="openrouter/free", name="Auto Router",
        capabilities=ModelCapabilities(tools=True, vision=True, coding=True),
        speed="medium", strength="large", notes="OpenRouter auto-routes",
    ),

    # ── MiniMax ──
    "minimax/minimax-m2.5:free": ModelInfo(
        id="minimax/minimax-m2.5:free", name="MiniMax M2.5",
        capabilities=ModelCapabilities(tools=True, coding=True),
        speed="medium", strength="large",
    ),
}

# Sort: models by priority category so rotation picks from a stable order
_INTENT_PRIORITY = {
    "vision":     [m for m in OPENROUTER_MODELS.values() if m.capabilities.vision],
    "reasoning":  [m for m in OPENROUTER_MODELS.values() if m.capabilities.reasoning],
    "coding":     [m for m in OPENROUTER_MODELS.values() if m.capabilities.coding],
    "general":    [m for m in OPENROUTER_MODELS.values()
                   if not m.capabilities.reasoning and not m.capabilities.vision
                   and m.capabilities.tools and m.strength != "small"],
    "fast":       [m for m in OPENROUTER_MODELS.values()
                   if m.speed == "fast" and m.strength == "medium"],
    "tiny":       [m for m in OPENROUTER_MODELS.values() if m.strength == "small"],
}


# ── Helper: badge for any model ID ──────────────────────────────────────────

def get_model_info(model_id: str) -> ModelInfo | None:
    """Look up ModelInfo by full model ID."""
    return OPENROUTER_MODELS.get(model_id)


def badged_name(model_id: str, fallback: str = "") -> str:
    """Return display name with capability badges for a model ID."""
    info = get_model_info(model_id)
    if info:
        return info.display_name()
    return fallback or model_id


def get_models_by_capability(*, tools=None, vision=None, reasoning=None, coding=None,
                              provider: str = "openrouter") -> list[ModelInfo]:
    """Filter the registry by capability flags."""
    results = []
    for m in OPENROUTER_MODELS.values():
        if m.provider != provider:
            continue
        if tools is not None and m.capabilities.tools != tools:
            continue
        if vision is not None and m.capabilities.vision != vision:
            continue
        if reasoning is not None and m.capabilities.reasoning != reasoning:
            continue
        if coding is not None and m.capabilities.coding != coding:
            continue
        results.append(m)
    return results
