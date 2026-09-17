import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_entrepreneur_profile_flow(client: AsyncClient):
    # 1. Register an entrepreneur
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "sarah.founder@vynk.io",
            "password": "SecurePassword123!",
            "full_name": "Sarah Innovator",
            "role": "entrepreneur",
            "stage": "mvp",
            "industry": "AI/DeepTech",
            "headline": "Building next-gen AI diagnostics",
            "location": "San Francisco, CA",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial profile
    profile_res = await client.get("/api/v1/profiles/me", headers=headers)
    assert profile_res.status_code == 200
    pdata = profile_res.json()
    assert pdata["full_name"] == "Sarah Innovator"
    assert pdata["role"] == "entrepreneur"
    assert pdata["is_own_profile"] is True
    assert pdata["username"] is not None
    assert "completion" in pdata
    initial_pct = pdata["completion"]["percentage"]
    assert initial_pct > 0

    # 3. Update entrepreneur profile with rich experience, education, achievements, and custom username
    update_res = await client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "username": "sarah_ai",
            "bio": "Passionate founder with 8+ years experience in biomedical imaging and neural networks.",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
            "skills": ["PyTorch", "Computer Vision", "Medical Devices", "Regulatory Strategy"],
            "experience": [
                {
                    "title": "Lead Computer Vision Engineer",
                    "company": "BioScan Dynamics",
                    "duration": "2021 - 2024",
                    "description": "Led team of 6 engineers developing real-time MRI anomaly detection.",
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "degree": "M.S. in Computer Science (AI Track)",
                    "year": "2020",
                }
            ],
            "achievements": [
                {
                    "title": "NIH Research Grant Winner ($150k)",
                    "year": "2023",
                    "description": "Competitive grant awarded for micro-ultrasound neural reconstruction.",
                }
            ],
            "website_url": "https://sarahdiagnostics.ai",
            "linkedin_url": "https://linkedin.com/in/sarah-ai-founder",
        },
    )
    assert update_res.status_code == 200
    updated_pdata = update_res.json()
    assert updated_pdata["username"] == "sarah_ai"
    assert len(updated_pdata["entrepreneur_profile"]["skills"]) == 4
    assert len(updated_pdata["entrepreneur_profile"]["experience"]) == 1
    assert len(updated_pdata["entrepreneur_profile"]["education"]) == 1
    assert len(updated_pdata["entrepreneur_profile"]["achievements"]) == 1

    # Profile completion should have increased
    assert updated_pdata["completion"]["percentage"] > initial_pct
    assert updated_pdata["completion"]["percentage"] == 100

    # 4. Access public profile by custom username without authentication
    pub_res = await client.get("/api/v1/profiles/sarah_ai")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["username"] == "sarah_ai"
    assert pub_data["full_name"] == "Sarah Innovator"
    assert pub_data["is_own_profile"] is False


@pytest.mark.asyncio
async def test_sponsor_profile_flow(client: AsyncClient):
    # 1. Register a sponsor
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "marcus.partner@vynkfunds.com",
            "password": "SecurePassword123!",
            "full_name": "Marcus Vance",
            "role": "sponsor",
            "organization_name": "Horizon Frontier Ventures",
            "sponsor_type": "venture_capital",
            "min_budget": 25000,
            "max_budget": 250000,
            "location": "New York, NY",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update sponsor profile with Phase 2 fields
    update_res = await client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "username": "horizon_frontier",
            "logo_url": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400",
            "about": "Early-stage deeptech and clean energy fund backing founders with unfair scientific advantages.",
            "industry": "DeepTech & Climate",
            "focus_industries": ["DeepTech", "ClimateTech", "AI Infrastructure"],
            "sponsorship_interests": ["Seed", "Pre-Seed", "Hardware Prototypes"],
            "areas_supported": ["Non-dilutive Grants", "Compute Credits ($50k AWS)", "Foundry Access", "GTM Mentorship"],
            "previous_collaborations": [
                {
                    "partner_name": "Aether Carbon Capture",
                    "year": "2023",
                    "description": "$100k catalytic grant and bench testing equipment sponsorship.",
                    "outcome": "Achieved pilot scale and secured Series A.",
                }
            ],
        },
    )
    assert update_res.status_code == 200
    sdata = update_res.json()
    assert sdata["username"] == "horizon_frontier"
    assert sdata["sponsor_profile"]["organization_name"] == "Horizon Frontier Ventures"
    assert len(sdata["sponsor_profile"]["areas_supported"]) == 4
    assert len(sdata["sponsor_profile"]["previous_collaborations"]) == 1
    assert sdata["completion"]["percentage"] == 100

    # 3. Public view by username
    pub_res = await client.get("/api/v1/profiles/horizon_frontier")
    assert pub_res.status_code == 200
    assert pub_res.json()["sponsor_profile"]["organization_name"] == "Horizon Frontier Ventures"


@pytest.mark.asyncio
async def test_username_validation_and_uniqueness(client: AsyncClient):
    # Register user 1
    res1 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@vynk.io",
            "password": "Password123!",
            "full_name": "User One",
            "role": "entrepreneur",
        },
    )
    t1 = res1.json()["access_token"]

    # Register user 2
    res2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@vynk.io",
            "password": "Password123!",
            "full_name": "User Two",
            "role": "entrepreneur",
        },
    )
    t2 = res2.json()["access_token"]

    # User 1 sets username 'quantum_tech'
    u1_update = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {t1}"},
        json={"username": "quantum_tech"},
    )
    assert u1_update.status_code == 200

    # User 2 tries to take 'quantum_tech'
    u2_collision = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {t2}"},
        json={"username": "quantum_tech"},
    )
    assert u2_collision.status_code == 400
    assert "already taken" in u2_collision.json()["detail"]

    # Invalid username format (special characters or too short)
    u2_invalid = await client.put(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {t2}"},
        json={"username": "hi!"},
    )
    assert u2_invalid.status_code == 400
