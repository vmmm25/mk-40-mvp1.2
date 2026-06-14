"""MARK XL — Smart Router: per-turn model selection by intent.

Classifies each user message into an intent category, then selects the
best-fitting model for that turn while rotating between equally capable
models to distribute load.

Conversation continuity is preserved because the provider and message
history remain unchanged — only the model ID changes between turns.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from core.model_registry import (
    OPENROUTER_MODELS,
    _INTENT_PRIORITY,
    get_model_info,
)

logger = logging.getLogger(__name__)


# ── Intent classification keywords ──────────────────────────────────────────
# Ordered by specificity: more specific patterns checked first.

_VISION_PATTERNS = [
    # Spanish
    r'\bmir[aeá]\b', r'\bveo\b', r'\bves\b', r'\bimagen\b', r'\bfoto\b',
    r'\bcaptur[ae]\b', r'\bpantalla[sz]?\b', r'\bscreenshot\b',
    r'\bmostr[aeá]me\b', r'\benseñ[aeá]me\b', r'\bqué hay en\b',
    r'\bdescrib[ií]me\b', r'\bqué ves\b',
    # English
    r'\bimage\b', r'\bpicture\b', r'\bphoto\b', r'\bscreen\b',
    r'\bvision\b', r'\bsee\b', r'\blook at\b', r'\bwhat.?s in\b',
    r'\bdescribe this\b', r'\bcamera\b',
]

_REASONING_PATTERNS = [
    # Spanish
    r'\bpor qué\b', r'\banali[záa]\b', r'\bcompar[áa]\b', r'\brazon[áa]\b',
    r'\bpi[ée]ns[ae]\b', r'\bproblema\b', r'\bl[óo]gic[ao]\b',
    r'\bexplic[áa]\b', r'\bcómo funciona\b', r'\bcu[aá]l es la diferenc',
    r'\bqué pasaría si\b', r'\bdemostr[áa]\b',
    # English
    r'\bwhy\b', r'\banalyz[ei]\b', r'\bcompare\b', r'\breason\b',
    r'\bthink\b', r'\bproblem\b', r'\blogic\b', r'\bexplain\b',
    r'\bhow does\b', r'\bwhat.?s the difference\b', r'\bwhat if\b',
    r'\bprove\b', r'\bhypothes[ei]\b', r'\bdeduce\b', r'\binfer\b',
    r'\bconclu[ds]i[oó]n\b',
]

_CODING_PATTERNS = [
    # Spanish
    r'\bc[oó]digo\b', r'\bprogram[áa]\b', r'\bfunci[oó]n\b', r'\bclase\b',
    r'\bbug\b', r'\berror\b', r'\bdebug\b', r'\bdesarroll[áa]\b',
    r'\bimplement[áa]\b', r'\bscript\b', r'\bcomando\b', r'\bterminal\b',
    r'\brefactoriz[áa]\b', r'\bcompil[aa]\b', r'\bejecut[aa]\b',
    r'\.py\b', r'\.js\b', r'\.ts\b', r'\.java\b', r'\.go\b',
    r'\.rs\b', r'\.cpp\b', r'\.cs\b', r'\.rb\b',
    # English
    r'\bcode\b', r'\bfunction\b', r'\bclass\b', r'\bimplement\b',
    r'\brefactor\b', r'\bcompile\b', r'\bexecute\b', r'\bscript\b',
    r'\bcommand\b', r'\brewrite\b', r'\bfix\b', r'\btest\b',
    r'\brefactor\b', r'\bapi\b', r'\bendpoint\b', r'\bsql\b',
    r'\bregex\b', r'\bdeploy\b', r'\bCI\b', r'\bCD\b',
]

_SIMPLE_PATTERNS = [
    # Short greetings / confirmations that don't need heavy models
    r'^(hola|ok|okay|si|s[ií]|no|gracias|dale|listo|bien|sale|perfecto|thanks|yes|no|bye|chau|hell[oó])\W*$',
    r'^(hey|ey|oye|eh)\W*$',
]


# ── SmartRouter ─────────────────────────────────────────────────────────────

class SmartRouter:
    """Per-turn model selector with load-aware rotation.

    Usage
    -----
    router = SmartRouter()
    model_id = router.select(user_message, "openrouter", current_model)
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        # Round-robin counters per intent category
        self._counters: dict[str, int] = {}
        self._last_intent: str | None = None
        self._last_model: str | None = None

    # ── Public API ─────────────────────────────────────────────────────

    def select(self, user_message: str, provider: str,
               current_model: str) -> str:
        """Return the best model ID for *user_message*.

        Parameters
        ----------
        user_message : str
            The user's latest text input.
        provider : str
            Active provider name (``"openrouter"``, ``"gemini"``, …).
        current_model : str
            Currently selected model ID.

        Returns
        -------
        str
            Model ID to use for this turn.
        """
        if not self.enabled or provider != "openrouter":
            return current_model

        intent = self._classify(user_message)
        candidates = self._get_candidates(intent)

        if not candidates:
            return current_model

        selected = self._rotate(candidates, intent, current_model)
        self._last_intent = intent
        self._last_model = selected

        if selected != current_model:
            logger.info(
                "SmartRouter: %s → %s (%s intent)",
                current_model.split("/")[-1].split(":")[0],
                selected.split("/")[-1].split(":")[0],
                intent,
            )
        return selected

    def classify_intent(self, user_message: str) -> str:
        """Classify a message without selecting a model (public helper)."""
        return self._classify(user_message)

    @property
    def current_intent(self) -> str | None:
        """Intent of the most recently routed message."""
        return self._last_intent

    @property
    def current_model(self) -> str | None:
        """Model selected for the most recently routed message."""
        return self._last_model

    # ── Intent classification ──────────────────────────────────────────

    def _classify(self, text: str) -> str:
        """Return one of ``"vision"``, ``"reasoning"``, ``"coding"``,
        ``"simple"``, or ``"general"``."""
        lower = text.lower().strip()

        # Simple greetings / quick confirmations → fast small model
        if any(re.search(p, lower) for p in _SIMPLE_PATTERNS):
            return "simple"

        # Vision requests need multimodal models
        if any(re.search(p, lower) for p in _VISION_PATTERNS):
            return "vision"

        # Hard reasoning
        if any(re.search(p, lower) for p in _REASONING_PATTERNS):
            return "reasoning"

        # Coding / development
        if any(re.search(p, lower) for p in _CODING_PATTERNS):
            return "coding"

        return "general"

    # ── Candidate selection ────────────────────────────────────────────

    def _get_candidates(self, intent: str) -> list[str]:
        """Return a list of model IDs suitable for *intent*, ordered by
        preference."""
        # Direct category match
        if intent in _INTENT_PRIORITY and _INTENT_PRIORITY[intent]:
            return [m.id for m in _INTENT_PRIORITY[intent]]

        # Fallback: general
        if intent == "simple":
            # Tiny / fast models
            tiny = [m.id for m in _INTENT_PRIORITY.get("tiny", [])]
            fast = [m.id for m in _INTENT_PRIORITY.get("fast", [])]
            return tiny + fast

        if intent == "vision":
            # No vision model → fallback to general with tools
            return [m.id for m in _INTENT_PRIORITY.get("general", [])]

        # Ultimate fallback: every registered model
        return list(OPENROUTER_MODELS.keys())

    # ── Rotation ───────────────────────────────────────────────────────

    def _rotate(self, candidates: list[str], intent: str,
                current: str) -> str:
        """Pick a candidate with round-robin fairness.

        - If *current* is suitable for *intent*, stays on it (avoid
          unnecessary switches).
        - Otherwise advances the round-robin counter for *intent*.
        """
        if not candidates:
            return current

        # If the current model is in the candidate list AND is still
        # the user's saved preference, keep it — stability wins
        if current in candidates:
            return current

        # Rotate: advance counter for this intent category
        c = self._counters.get(intent, 0)
        idx = c % len(candidates)
        self._counters[intent] = c + 1
        return candidates[idx]

    def reset(self):
        """Reset all rotation counters (e.g. on provider switch)."""
        self._counters.clear()
        self._last_intent = None
        self._last_model = None
