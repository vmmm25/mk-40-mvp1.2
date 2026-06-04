"""Abstract engine interface."""
from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)

class JarvisEngine(ABC):
    def __init__(self, ui: Any, provider: Any):
        self.ui = ui
        self.provider = provider
    
    @abstractmethod
    async def run(self):
        """Main engine loop."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Graceful shutdown."""
        pass
