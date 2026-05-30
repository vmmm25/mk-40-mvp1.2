# MARK XL — Multi-Provider System
from .base import BaseProvider, ProviderConfig, Message, ToolCall, ToolResult

PROVIDER_REGISTRY: dict[str, type["BaseProvider"]] = {}

def register_provider(name: str, cls: type[BaseProvider]):
    PROVIDER_REGISTRY[name] = cls

def get_provider(name: str) -> type[BaseProvider] | None:
    return PROVIDER_REGISTRY.get(name)

def list_providers() -> list[str]:
    return list(PROVIDER_REGISTRY.keys())

def create_provider(name: str, config: ProviderConfig) -> "BaseProvider":
    cls = get_provider(name)
    if not cls:
        raise ValueError(f"Unknown provider: {name}. Available: {list_providers()}")
    return cls(config)

# Import providers to register them
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openrouter_provider import OpenRouterProvider
from .lmstudio_provider import LMStudioProvider
