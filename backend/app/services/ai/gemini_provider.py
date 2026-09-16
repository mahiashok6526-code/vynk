import logging
from typing import List, Dict, Any, Optional
from app.services.ai.base import BaseAIService
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiAIService(BaseAIService):
    """Google Gemini AI Service Implementation for Vynk.

    Architected for Phase 2 integration using the official Google GenAI SDK.
    In Phase 1, it establishes the provider skeleton, parameter validation,
    and structured output definitions without making live calls or using fake responses.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self._is_ready = bool(self.api_key and self.api_key.strip())

    @property
    def is_configured(self) -> bool:
        """Returns True if the Gemini API key is configured."""
        return self._is_ready

    async def match_entrepreneur_and_sponsors(
        self,
        project: Dict[str, Any],
        sponsor_profiles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Phase 2 Hook: Uses Gemini multimodal/reasoning capabilities to evaluate

        deep semantic fit between founder pitch descriptions and investor theses.
        """
        if not self.is_configured:
            logger.info("Gemini API not configured for Phase 1. Deferring to deterministic engine.")
            from app.services.ai.compatibility_engine import CompatibilityEngine
            return await CompatibilityEngine().match_entrepreneur_and_sponsors(project, sponsor_profiles)

        # In Phase 2, this will execute the structured GenAI interaction call
        raise NotImplementedError("Live Gemini API calls will be activated in Phase 2 (AI Matching).")

    async def explain_match_compatibility(
        self,
        project: Dict[str, Any],
        sponsor_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 2 Hook: Generates natural language factor explanation via Gemini."""
        if not self.is_configured:
            from app.services.ai.compatibility_engine import CompatibilityEngine
            return await CompatibilityEngine().explain_match_compatibility(project, sponsor_profile)

        raise NotImplementedError("Live Gemini API calls will be activated in Phase 2 (AI Matching).")

    async def analyze_project_sponsorship_fit(
        self,
        project: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 2 Hook: Provides strategic critique and milestone breakdown via Gemini."""
        raise NotImplementedError("Live Gemini API calls will be activated in Phase 2.")
