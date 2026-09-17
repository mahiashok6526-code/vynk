import logging
from typing import List, Dict, Any, Optional
import httpx

from app.services.ai.base import BaseAIService
from app.services.ai.compatibility_engine import CompatibilityEngine
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiAIService(BaseAIService):
    """Google Gemini AI Service Implementation for Vynk.

    Generates grounded, explainable natural-language syntheses using Google Gemini.
    Features graceful, seamless fallback to the deterministic engine when GEMINI_API_KEY
    is unconfigured, invalid, or experiencing network latency.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or settings.GEMINI_API_KEY or "").strip()
        self.model_name = "gemini-2.5-flash"
        self.deterministic_engine = CompatibilityEngine()

    @property
    def is_configured(self) -> bool:
        """Returns True if the Gemini API key is configured."""
        return bool(self.api_key)

    async def match_entrepreneur_and_sponsors(
        self,
        project: Dict[str, Any],
        sponsor_profiles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Candidate ranking uses the deterministic compatibility engine to guarantee

        consistent, fast, and quota-efficient scoring without per-row LLM latency.
        """
        return await self.deterministic_engine.match_entrepreneur_and_sponsors(project, sponsor_profiles)

    async def generate_grounded_explanation(
        self,
        project: Dict[str, Any],
        sponsor: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesizes an explainable narrative via Google Gemini or deterministic fallback."""
        if not self.is_configured:
            logger.info("Gemini API key not configured. Using deterministic fallback explanation.")
            return {
                "explanation": analysis.get("summary") or "High compatibility based on sector and funding fit.",
                "ai_generated": False,
                "provider": "deterministic",
                "model": "compatibility_v1",
            }

        # Build strictly grounded prompt
        p_title = project.get("title", "Project")
        p_cat = project.get("category", "Technology")
        p_stage = (project.get("stage") or "prototype").upper()
        p_goal = float(project.get("funding_goal") or 0)
        p_support = ", ".join(project.get("required_support") or ["growth capital"])

        s_org = sponsor.get("organization_name") or sponsor.get("full_name") or "Sponsor"
        s_type = (sponsor.get("sponsor_type") or "investor").replace("_", " ").title()
        s_focus = ", ".join(sponsor.get("focus_industries") or ["Cross-industry"])
        s_min = float(sponsor.get("min_budget") or 1000)
        s_max = float(sponsor.get("max_budget") or 1000000)

        score = analysis.get("overall_score", 75)
        reasons_text = "; ".join(analysis.get("reasons") or ["Sector and milestone alignment"])
        mismatches_text = "; ".join(analysis.get("mismatches") or ["None identified"])

        system_instruction = (
            "You are Vynk's AI Strategic Match Analyst. "
            "Synthesize a concise 2-3 sentence strategic rationale explaining why this startup project "
            "and capital sponsor are compatible, and note any potential considerations. "
            "CRITICAL: Base your analysis STRICTLY AND EXCLUSIVELY on the factual data provided below. "
            "Do NOT invent past investments, commitments, outside awards, or non-provided details."
        )

        user_content = (
            f"STARTUP PROJECT:\n"
            f"- Name: {p_title}\n"
            f"- Category / Industry: {p_cat}\n"
            f"- Maturity Stage: {p_stage}\n"
            f"- Funding Requirement: ₹{p_goal:,.0f} INR\n"
            f"- Required Support Types: {p_support}\n\n"
            f"SPONSOR PROFILE:\n"
            f"- Partner: {s_org} ({s_type})\n"
            f"- Sector Focus: {s_focus}\n"
            f"- Ticket Range: ₹{s_min:,.0f} – ₹{s_max:,.0f} INR\n\n"
            f"COMPATIBILITY ANALYSIS:\n"
            f"- Score: {score}/100\n"
            f"- Strong Points: {reasons_text}\n"
            f"- Potential Gaps: {mismatches_text}\n\n"
            f"Provide your concise, professional 2-3 sentence assessment:"
        )

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_content}"}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 250,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(endpoint, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if content_parts:
                            text = content_parts[0].get("text", "").strip()
                            if text:
                                return {
                                    "explanation": text,
                                    "ai_generated": True,
                                    "provider": "gemini",
                                    "model": self.model_name,
                                }
                logger.warning(f"Gemini API returned non-200 status {res.status_code}: {res.text}. Falling back.")
        except Exception as err:
            logger.warning(f"Gemini API call encountered error: {err}. Falling back to deterministic engine.")

        # Graceful fallback
        return {
            "explanation": analysis.get("summary") or "Strategic match based on sector alignment and capital parameters.",
            "ai_generated": False,
            "provider": "deterministic",
            "model": "compatibility_v1",
        }

    async def explain_match_compatibility(
        self,
        project: Dict[str, Any],
        sponsor_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluates compatibility factors and generates explainable narrative."""
        analysis = self.deterministic_engine.evaluate_compatibility(project, sponsor_profile)
        ai_exp = await self.generate_grounded_explanation(project, sponsor_profile, analysis)
        analysis["explanation"] = ai_exp["explanation"]
        analysis["ai_generated"] = ai_exp["ai_generated"]
        analysis["provider"] = ai_exp["provider"]
        analysis["model"] = ai_exp["model"]
        return analysis

    async def analyze_project_sponsorship_fit(
        self,
        project: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Provides positioning guidance for project sponsorship."""
        return await self.deterministic_engine.analyze_project_sponsorship_fit(project)
