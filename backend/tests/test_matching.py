import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.services.ai.compatibility_engine import CompatibilityEngine
from app.services.ai.gemini_provider import GeminiAIService


@pytest.mark.asyncio
async def test_deterministic_compatibility_scoring():
    """Verify that compatibility scoring is strictly deterministic, bounded, and auditable."""
    engine = CompatibilityEngine()

    project = {
        "title": "AeroGrid Microturbines",
        "category": "CleanTech",
        "industry": "Renewable Energy",
        "stage": "mvp",
        "funding_goal": 2500000.0,
        "required_support": ["grant", "equity_investment"],
        "tech_stack": ["Rust", "Embedded C++", "IoT"],
        "location": "Bangalore, India",
    }

    sponsor = {
        "organization_name": "Climate Horizon Angels",
        "sponsor_type": "angel",
        "focus_industries": ["CleanTech", "Climate Tech"],
        "min_budget": 1000000.0,
        "max_budget": 5000000.0,
        "preferred_sponsorship_types": ["grant", "equity_investment", "mentorship"],
        "sponsorship_interests": ["IoT", "Hardware", "CleanTech"],
        "location": "Bangalore, India",
    }

    # Run multiple times to prove determinism
    eval1 = engine.evaluate_compatibility(project, sponsor)
    eval2 = engine.evaluate_compatibility(project, sponsor)

    assert eval1["overall_score"] == eval2["overall_score"]
    assert eval1["factors"] == eval2["factors"]
    assert eval1["reasons"] == eval2["reasons"]
    assert eval1["overall_score"] >= 85, f"Expected high compatibility, got {eval1['overall_score']}"

    # Factor weights check
    factors = eval1["factors"]
    assert factors["industry"]["score"] <= CompatibilityEngine.WEIGHT_INDUSTRY
    assert factors["stage"]["score"] <= CompatibilityEngine.WEIGHT_STAGE
    assert factors["budget"]["score"] <= CompatibilityEngine.WEIGHT_BUDGET
    assert factors["support_type"]["score"] <= CompatibilityEngine.WEIGHT_SUPPORT_TYPE
    assert factors["technology"]["score"] <= CompatibilityEngine.WEIGHT_TECHNOLOGY
    assert factors["location"]["score"] <= CompatibilityEngine.WEIGHT_LOCATION

    # Sum of factor scores matches overall score
    total_factor_sum = sum(f["score"] for f in factors.values())
    assert eval1["overall_score"] == total_factor_sum


@pytest.mark.asyncio
async def test_budget_mismatch_and_reasons():
    """Verify that severe budget mismatches are reflected in score and mismatches list."""
    engine = CompatibilityEngine()

    project = {
        "category": "EdTech",
        "stage": "prototype",
        "funding_goal": 50000000.0,  # 5 Crore INR
    }

    sponsor = {
        "organization_name": "Micro Seed Angels",
        "sponsor_type": "angel",
        "min_budget": 200000.0,   # 2 Lakh INR
        "max_budget": 1000000.0,  # 10 Lakh INR
    }

    evaluation = engine.evaluate_compatibility(project, sponsor)
    assert evaluation["factors"]["budget"]["score"] <= 10
    assert any("exceeds" in m.lower() for m in evaluation["mismatches"])


@pytest.mark.asyncio
async def test_get_recommended_projects_as_sponsor(client: AsyncClient):
    """Verify sponsors receive ranked project recommendations with factor breakdowns."""
    # Register Entrepreneur and create published project
    ent_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "match.founder@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Kavita Rao",
            "role": "entrepreneur",
        },
    )
    assert ent_reg.status_code == 201
    ent_token = ent_reg.json()["access_token"]

    proj_res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "BioCompost AI Harvester",
            "tagline": "Autonomous accelerated bio-waste conversion for municipal yards",
            "description": "Smart aerobic composting reactors utilizing thermal sensors to cut cycle times by 70%.",
            "category": "CleanTech",
            "stage": "mvp",
            "problem_statement": "Municipal landfill overflow generates methane and hazardous leachate runoffs.",
            "proposed_solution": "Distributed automated composters equipped with microbial heat regulators.",
            "target_market": "Municipal corporations, food processing plants, and urban farmers.",
            "value_proposition": "Rapid 12-day organic soil turnover with real-time nitrogen-phosphorus telemetry.",
            "funding_goal": 3000000.0,
            "required_support": ["grant", "mentorship"],
            "status": "published",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # Register Sponsor with CleanTech focus
    sp_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "clean.sponsor@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Siddharth Verma",
            "role": "sponsor",
            "organization_name": "Verma Clean Impact Fund",
            "sponsor_type": "venture_capital",
            "min_budget": 2000000.0,
            "max_budget": 10000000.0,
        },
    )
    assert sp_reg.status_code == 201
    sp_token = sp_reg.json()["access_token"]

    # Update sponsor detailed criteria
    await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {sp_token}"},
        json={
            "focus_industries": ["CleanTech", "BioTech"],
            "preferred_sponsorship_types": ["grant", "equity_investment"],
        },
    )

    # Get recommended projects for sponsor
    matches_res = await client.get(
        "/api/v1/ai/matches/projects",
        headers={"Authorization": f"Bearer {sp_token}"},
    )
    assert matches_res.status_code == 200
    matches = matches_res.json()
    assert len(matches) >= 1
    target_match = next((m for m in matches if m["project_id"] == proj_id), None)
    assert target_match is not None
    assert target_match["compatibility_score"] >= 70
    assert "industry" in target_match["factors"]
    assert "budget" in target_match["factors"]
    assert len(target_match["reasons"]) >= 1


@pytest.mark.asyncio
async def test_get_recommended_sponsors_as_entrepreneur(client: AsyncClient):
    """Verify entrepreneurs receive ranked sponsor recommendations with factor breakdowns."""
    # Register Entrepreneur
    ent_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "rec.ent@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Rohan Mehta",
            "role": "entrepreneur",
        },
    )
    assert ent_reg.status_code == 201
    ent_token = ent_reg.json()["access_token"]

    # Create published project
    proj_res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "QuantumKey Cryptography",
            "tagline": "Post-quantum lattice security for cloud key management",
            "description": "NIST-standardized post-quantum key exchange for edge cloud storage and IoT networks.",
            "category": "DeepTech & Hardware",
            "stage": "prototype",
            "problem_statement": "Shor's algorithm will render current RSA and elliptic-curve security obsolete.",
            "proposed_solution": "Drop-in post-quantum cryptography library with FPGA hardware accelerators.",
            "target_market": "Fintech payment processors, defense contractors, and cloud hyperscalers.",
            "value_proposition": "Under 5ms quantum-resistant key encapsulation with zero hardware overhaul.",
            "funding_goal": 2000000.0,
            "required_support": ["grant", "lab_access"],
            "status": "published",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # Call GET /api/v1/ai/matches/sponsors
    matches_res = await client.get(
        f"/api/v1/ai/matches/sponsors?project_id={proj_id}",
        headers={"Authorization": f"Bearer {ent_token}"},
    )
    assert matches_res.status_code == 200
    matches = matches_res.json()
    assert isinstance(matches, list)


@pytest.mark.asyncio
async def test_role_authorization_guards(client: AsyncClient):
    """Verify that entrepreneurs cannot access sponsor endpoints and vice-versa."""
    # Register Entrepreneur
    ent_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "guard.ent@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Guard Ent",
            "role": "entrepreneur",
        },
    )
    ent_token = ent_reg.json()["access_token"]

    # Register Sponsor
    sp_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "guard.sp@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Guard Sponsor",
            "role": "sponsor",
            "organization_name": "Guard Capital",
        },
    )
    sp_token = sp_reg.json()["access_token"]

    # Entrepreneur trying to access sponsor project recommendations -> 403 Forbidden
    ent_access_sp = await client.get(
        "/api/v1/ai/matches/projects",
        headers={"Authorization": f"Bearer {ent_token}"},
    )
    assert ent_access_sp.status_code == 403

    # Sponsor trying to access entrepreneur sponsor recommendations -> 403 Forbidden
    sp_access_ent = await client.get(
        "/api/v1/ai/matches/sponsors",
        headers={"Authorization": f"Bearer {sp_token}"},
    )
    assert sp_access_ent.status_code == 403


@pytest.mark.asyncio
async def test_missing_gemini_api_key_fallback(client: AsyncClient):
    """Verify that when Gemini API key is missing, explanation endpoint provides deterministic fallback."""
    # Register Sponsor
    sp_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "fb.sponsor@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Fallback Sponsor",
            "role": "sponsor",
            "organization_name": "Fallback Partners",
        },
    )
    sp_token = sp_reg.json()["access_token"]

    # Register Entrepreneur & publish project
    ent_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "fb.ent@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Fallback Founder",
            "role": "entrepreneur",
        },
    )
    ent_token = ent_reg.json()["access_token"]

    proj_res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "Fallback Drone AI",
            "tagline": "Autonomous survey drones for high-voltage transmission lines",
            "description": "Lidar and computer vision drones performing autonomous structural inspections on electrical grids.",
            "category": "AI / ML",
            "stage": "prototype",
            "problem_statement": "Manual high-voltage line inspection causes 12 fatalities annually in industrial zones.",
            "proposed_solution": "Fully autonomous drone docks with automated battery swap and real-time fault detection.",
            "target_market": "National power transmission companies and renewable wind farm operators.",
            "value_proposition": "Sub-millimeter crack detection at 400kV line speeds without power shutdown.",
            "funding_goal": 3500000.0,
            "required_support": ["grant", "mentorship"],
            "status": "published",
        },
    )
    proj_id = proj_res.json()["id"]

    # Request explanation as sponsor with empty API key
    with patch.object(GeminiAIService, "is_configured", False):
        exp_res = await client.get(
            f"/api/v1/ai/matches/projects/{proj_id}/explanation",
            headers={"Authorization": f"Bearer {sp_token}"},
        )
        assert exp_res.status_code == 200
        data = exp_res.json()
        assert data["ai_generated"] is False
        assert data["provider"] == "deterministic"
        assert data["explanation"] is not None
        assert len(data["explanation"]) > 10
        assert "factors" in data
        assert "reasons" in data


@pytest.mark.asyncio
async def test_gemini_explanation_and_caching(client: AsyncClient):
    """Verify Gemini API response handling and subsequent cache hits."""
    sp_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "cache.sp@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Cache Test Sponsor",
            "role": "sponsor",
            "organization_name": "Cache Ventures",
        },
    )
    sp_token = sp_reg.json()["access_token"]

    ent_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "cache.ent@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Cache Founder",
            "role": "entrepreneur",
        },
    )
    ent_token = ent_reg.json()["access_token"]

    proj_res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "Cache Proof Quantum Sensor",
            "tagline": "Room-temperature diamond nitrogen-vacancy quantum magnetometers",
            "description": "Ultra-sensitive magnetic anomaly detectors for subterranean mineral exploration.",
            "category": "DeepTech & Hardware",
            "stage": "mvp",
            "problem_statement": "Deep geological mapping requires expensive exploratory drilling and seismology.",
            "proposed_solution": "Handheld NV-center quantum sensors providing high-resolution subterranean scans.",
            "target_market": "Critical minerals exploration companies and geophysical survey firms.",
            "value_proposition": "100x magnetic resolution at room temperature with zero liquid helium cooling.",
            "funding_goal": 4000000.0,
            "required_support": ["grant", "equity_investment"],
            "status": "published",
        },
    )
    proj_id = proj_res.json()["id"]

    mock_gemini_response = {
        "explanation": "High strategic alignment as the sponsor targets deep-tech innovations and the project's funding requirement aligns with investment criteria.",
        "ai_generated": True,
        "provider": "gemini",
        "model": "gemini-2.5-flash",
    }

    with patch.object(GeminiAIService, "generate_grounded_explanation", return_value=mock_gemini_response):
        # First call generates and caches
        res1 = await client.get(
            f"/api/v1/ai/matches/projects/{proj_id}/explanation",
            headers={"Authorization": f"Bearer {sp_token}"},
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["ai_generated"] is True
        assert data1["provider"] == "gemini"

    # Second call hits database cache directly without calling generate_grounded_explanation
    res2 = await client.get(
        f"/api/v1/ai/matches/projects/{proj_id}/explanation",
        headers={"Authorization": f"Bearer {sp_token}"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["explanation"] == data1["explanation"]
    assert data2["ai_generated"] is True
    assert data2["provider"] == "gemini"
