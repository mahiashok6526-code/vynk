from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseAIService(ABC):
    """Abstract Base Class defining the Vynk AI service interface.

    This interface decouples platform features from specific LLM vendors,
    allowing Google Gemini or multi-model routing to be plugged in seamlessly.
    """

    @abstractmethod
    async def match_entrepreneur_and_sponsors(
        self,
        project: Dict[str, Any],
        sponsor_profiles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank and return suitable sponsors for a given project with compatibility scores."""
        pass

    @abstractmethod
    async def explain_match_compatibility(
        self,
        project: Dict[str, Any],
        sponsor_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce an explainable breakdown of why a match was recommended."""
        pass

    @abstractmethod
    async def analyze_project_sponsorship_fit(
        self,
        project: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze project positioning and suggest optimal sponsorship structures."""
        pass
