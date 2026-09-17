import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def entrepreneur_client(client: AsyncClient):
    """Registers and authenticates an entrepreneur."""
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test.entrepreneur@vynk.io",
            "password": "StrongPassword123!",
            "full_name": "Marcus Vance",
            "role": "entrepreneur",
            "stage": "mvp",
            "industry": "CleanTech",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest_asyncio.fixture
async def sponsor_client(client: AsyncClient):
    """Registers and authenticates a sponsor."""
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test.sponsor@vynk.io",
            "password": "StrongPassword123!",
            "full_name": "Sarah Chen",
            "role": "sponsor",
            "organization_name": "Horizon Capital",
            "sponsor_type": "venture_capital",
            "min_budget": 10000,
            "max_budget": 100000,
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    # Separate client with sponsor token
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.mark.asyncio
async def test_entrepreneur_can_create_project(entrepreneur_client: AsyncClient):
    """Scenario 1: Entrepreneur can create a complete published project."""
    res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "BioCarbon Sequestration Array",
            "tagline": "Autonomous algal photobioreactors for point-source emissions",
            "description": "High-efficiency microalgae panels capturing industrial CO2 and generating green biofuel.",
            "category": "CleanTech",
            "industry": "Climate & Energy",
            "stage": "prototype",
            "problem_statement": "Heavy industry lacks compact, cost-effective onsite carbon abatement hardware.",
            "proposed_solution": "Modular photobioreactors that connect directly to HVAC flue stacks with 92% capture rate.",
            "target_market": "Cement and steel processing plants across North America and Europe.",
            "value_proposition": "60% cheaper abatement cost per ton of CO2 with saleable protein and lipid byproducts.",
            "current_progress": "Completed 1000-hour continuous pilot test at regional manufacturing facility.",
            "funding_goal": 150000.0,
            "funding_received": 25000.0,
            "required_support": ["Capital", "Mentorship", "Compute Credits"],
            "required_resources": "Access to emissions testing lab and pilot facility space.",
            "skills_needed": ["Chemical Engineering", "Embedded Firmware", "Regulatory Compliance"],
            "tech_stack": ["Rust", "Python", "MQTT", "TimescaleDB"],
            "website_url": "https://biocarbon.example.com",
            "pitch_deck_url": "https://biocarbon.example.com/deck.pdf",
            "status": "published",
            "requirements": [
                {
                    "requirement_type": "capital",
                    "title": "Hardware Prototyping Grant",
                    "amount": 100000.0,
                    "description": "Direct funding for second generation pressure vessels.",
                }
            ],
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "BioCarbon Sequestration Array"
    assert data["status"] == "published"
    assert data["funding_goal"] == 150000.0
    assert len(data["requirements"]) == 1
    assert data["founder"]["full_name"] == "Marcus Vance"
    assert "Capital" in data["required_support"]


@pytest.mark.asyncio
async def test_sponsor_cannot_create_project(client: AsyncClient):
    """Scenario 2: Sponsor cannot create an entrepreneur project (403 Forbidden)."""
    # Register sponsor
    sp_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "sponsor.tester@vynk.io",
            "password": "Password123!",
            "full_name": "Sponsor Tester",
            "role": "sponsor",
            "organization_name": "Alpha Fund",
            "sponsor_type": "angel",
        },
    )
    assert sp_res.status_code == 201
    token = sp_res.json()["access_token"]

    res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Unauthorized Sponsor Project",
            "tagline": "Should be rejected immediately",
            "description": "This project should never be created.",
            "category": "FinTech",
        },
    )
    assert res.status_code == 403
    assert "Requires entrepreneur role" in res.json()["detail"]


@pytest.mark.asyncio
async def test_project_validation_on_publish(entrepreneur_client: AsyncClient):
    """Scenario 3: Validation prevents publishing an incomplete showcase."""
    # Attempt to publish without required problem_statement, proposed_solution, funding_goal, etc.
    res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Incomplete Showcase",
            "tagline": "Short",
            "description": "Too brief",
            "status": "published",
        },
    )
    assert res.status_code == 400
    detail = res.json()["detail"]
    assert "Cannot publish incomplete project showcase" in detail
    assert "Problem Statement" in detail
    assert "Funding Goal" in detail


@pytest.mark.asyncio
async def test_draft_creation_and_partial_data(entrepreneur_client: AsyncClient):
    """Scenario 4: Entrepreneur can save a draft project with partial information."""
    res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Draft Quantum Optics Sensor",
            "tagline": "Work in progress draft",
            "status": "draft",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Draft Quantum Optics Sensor"
    assert data["status"] == "draft"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_publish_draft_project(entrepreneur_client: AsyncClient):
    """Scenario 5: Publishing a draft project validates fields and transitions to published."""
    # 1. Create draft
    draft_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Hyperspectral Drone Scanner",
            "tagline": "Crop diagnostics via aerial hyperspectral imaging",
            "status": "draft",
        },
    )
    assert draft_res.status_code == 201
    proj_id = draft_res.json()["id"]

    # 2. Attempt to publish while incomplete -> 400
    fail_pub = await entrepreneur_client.post(f"/api/v1/projects/{proj_id}/publish")
    assert fail_pub.status_code == 400

    # 3. Update with complete showcase info
    update_res = await entrepreneur_client.put(
        f"/api/v1/projects/{proj_id}",
        json={
            "description": "High-altitude multi-band spectral sensing that spots crop fungal diseases days before visible symptoms appear.",
            "category": "AgTech",
            "industry": "Agriculture & Robotics",
            "stage": "mvp",
            "problem_statement": "Crop blight causes billions in lost yields because manual visual scouting detects damage too late.",
            "proposed_solution": "Lightweight hyperspectral camera payload with onboard edge AI for sub-millimeter leaf analysis.",
            "target_market": "Commercial grain farmers and agricultural co-ops across North America.",
            "value_proposition": "Detects leaf moisture stress and early pathogen infection with 95% accuracy 7 days early.",
            "funding_goal": 85000.0,
            "required_support": ["Capital", "Hardware", "Cloud Resources"],
        },
    )
    assert update_res.status_code == 200

    # 4. Now publish successfully
    pub_res = await entrepreneur_client.post(f"/api/v1/projects/{proj_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "published"


@pytest.mark.asyncio
async def test_project_retrieval_and_draft_protection(client: AsyncClient, entrepreneur_client: AsyncClient):
    """Scenario 6: Public can retrieve published projects; drafts are hidden from unauthorized visitors."""
    # 1. Create a published project and a draft project
    pub_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Public Visible Project",
            "tagline": "Public showcase tagline",
            "description": "Detailed description of publicly visible project showcase.",
            "category": "CleanTech",
            "stage": "mvp",
            "problem_statement": "Clear problem statement for public showcase testing.",
            "proposed_solution": "Clear proposed solution for public showcase testing.",
            "target_market": "Commercial enterprises worldwide.",
            "value_proposition": "Measurable efficiency gains and cost reductions.",
            "funding_goal": 50000.0,
            "required_support": ["Capital"],
            "status": "published",
        },
    )
    assert pub_res.status_code == 201
    pub_id = pub_res.json()["id"]

    draft_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Top Secret Draft Project",
            "tagline": "Unpublished experimental concepts",
            "status": "draft",
        },
    )
    assert draft_res.status_code == 201
    draft_id = draft_res.json()["id"]

    # 2. Public unauthenticated user accesses published project -> 200
    auth_header = client.headers.pop("Authorization", None)
    anon_pub = await client.get(f"/api/v1/projects/{pub_id}")
    assert anon_pub.status_code == 200
    assert anon_pub.json()["title"] == "Public Visible Project"

    # 3. Public unauthenticated user accesses draft project -> 404
    anon_draft = await client.get(f"/api/v1/projects/{draft_id}")
    assert anon_draft.status_code == 404

    # 4. Project owner accesses their own draft project -> 200
    if auth_header:
        client.headers["Authorization"] = auth_header
    owner_draft = await entrepreneur_client.get(f"/api/v1/projects/{draft_id}")
    assert owner_draft.status_code == 200
    assert owner_draft.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_project_editing_by_owner(entrepreneur_client: AsyncClient):
    """Scenario 7: Project owner can edit project metadata."""
    create_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Original Sensor Project",
            "tagline": "Initial project tagline",
            "status": "draft",
        },
    )
    proj_id = create_res.json()["id"]

    edit_res = await entrepreneur_client.put(
        f"/api/v1/projects/{proj_id}",
        json={
            "title": "Updated Sensor Array v2",
            "tagline": "Revised and improved tagline",
            "location": "Boston, MA",
            "timeline": "Q3 2026 Production",
        },
    )
    assert edit_res.status_code == 200
    edited = edit_res.json()
    assert edited["title"] == "Updated Sensor Array v2"
    assert edited["tagline"] == "Revised and improved tagline"
    assert edited["location"] == "Boston, MA"
    assert edited["timeline"] == "Q3 2026 Production"


@pytest.mark.asyncio
async def test_project_ownership_authorization(client: AsyncClient, entrepreneur_client: AsyncClient):
    """Scenario 8: Another entrepreneur cannot edit or archive someone else's project (403 Forbidden)."""
    # 1. First entrepreneur creates a project
    create_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Owner Project",
            "tagline": "Belongs to entrepreneur 1",
            "status": "draft",
        },
    )
    proj_id = create_res.json()["id"]

    # 2. Register second entrepreneur
    reg_res2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "intruder.founder@vynk.io",
            "password": "Password123!",
            "full_name": "Intruder Founder",
            "role": "entrepreneur",
        },
    )
    assert reg_res2.status_code == 201
    token2 = reg_res2.json()["access_token"]
    intruder_headers = {"Authorization": f"Bearer {token2}"}

    # 3. Second entrepreneur attempts to edit first entrepreneur's project -> 403 Forbidden
    hack_res = await client.put(
        f"/api/v1/projects/{proj_id}",
        headers=intruder_headers,
        json={"title": "Hacked Title"},
    )
    assert hack_res.status_code == 403
    assert "permission to edit" in hack_res.json()["detail"]

    # 4. Second entrepreneur attempts to archive first entrepreneur's project -> 403 Forbidden
    arch_res = await client.post(
        f"/api/v1/projects/{proj_id}/archive",
        headers=intruder_headers,
    )
    assert arch_res.status_code == 403


@pytest.mark.asyncio
async def test_project_archiving(entrepreneur_client: AsyncClient):
    """Scenario 9: Entrepreneur can archive their project."""
    create_res = await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Project To Archive",
            "tagline": "Will be archived soon",
            "status": "draft",
        },
    )
    proj_id = create_res.json()["id"]

    arch_res = await entrepreneur_client.post(f"/api/v1/projects/{proj_id}/archive")
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_published_project_discovery_feed(client: AsyncClient, entrepreneur_client: AsyncClient):
    """Scenario 10: Discovery feed lists published projects and strictly excludes drafts and archives."""
    # Create published project
    await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Discovery Alpha",
            "tagline": "Should appear in public discovery",
            "description": "Detailed description of discovery alpha startup showcase.",
            "category": "CleanTech",
            "stage": "launched",
            "problem_statement": "Energy efficiency problem in cloud servers.",
            "proposed_solution": "Direct-to-chip liquid cooling manifolds.",
            "target_market": "Hyperscale data center operators.",
            "value_proposition": "40% reduction in data center cooling electricity costs.",
            "funding_goal": 200000.0,
            "required_support": ["Capital", "Hardware"],
            "status": "published",
        },
    )

    # Create draft project
    await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "Hidden Draft Beta",
            "tagline": "Must not appear in public feed",
            "status": "draft",
        },
    )

    # Public user queries discovery feed
    feed_res = await client.get("/api/v1/projects/")
    assert feed_res.status_code == 200
    feed = feed_res.json()

    titles = [p["title"] for p in feed]
    assert "Discovery Alpha" in titles
    assert "Hidden Draft Beta" not in titles


@pytest.mark.asyncio
async def test_project_filtering(client: AsyncClient, entrepreneur_client: AsyncClient):
    """Scenario 11: Project filtering by category, stage, and required support."""
    await entrepreneur_client.post(
        "/api/v1/projects/",
        json={
            "title": "NeuroMed AI Scanner",
            "tagline": "Ultra-fast MRI reconstruction with deep learning",
            "description": "Reduces scan times by 75% using accelerated physics-informed neural networks.",
            "category": "HealthTech",
            "industry": "Healthcare AI",
            "stage": "scaling",
            "problem_statement": "Patients experience claustrophobia and delays during 45-minute MRI scans.",
            "proposed_solution": "Deep learning reconstruction algorithm that operates from 8x undersampled k-space.",
            "target_market": "Hospitals and radiology clinics.",
            "value_proposition": "4x patient throughput increase per MRI scanner.",
            "funding_goal": 300000.0,
            "required_support": ["Mentorship", "Compute Credits"],
            "status": "published",
        },
    )

    # Filter by category
    cat_res = await client.get("/api/v1/projects/?category=HealthTech")
    assert cat_res.status_code == 200
    assert any(p["category"] == "HealthTech" for p in cat_res.json())

    # Filter by stage
    stage_res = await client.get("/api/v1/projects/?stage=scaling")
    assert stage_res.status_code == 200
    assert any(p["stage"] == "scaling" for p in stage_res.json())

    # Filter by required_support
    supp_res = await client.get("/api/v1/projects/?required_support=Compute%20Credits")
    assert supp_res.status_code == 200
    assert any("Compute Credits" in p["required_support"] for p in supp_res.json())

    # Filter by search
    search_res = await client.get("/api/v1/projects/?search=NeuroMed")
    assert search_res.status_code == 200
    assert any(p["title"] == "NeuroMed AI Scanner" for p in search_res.json())


@pytest.mark.asyncio
async def test_nonexistent_project_handling(client: AsyncClient):
    """Scenario 12: Proper 404 handling for non-existent project IDs and slugs."""
    res = await client.get("/api/v1/projects/999999")
    assert res.status_code == 404
    assert "Project not found" in res.json()["detail"]

    slug_res = await client.get("/api/v1/projects/this-project-slug-does-not-exist")
    assert slug_res.status_code == 404
    assert "Project not found" in slug_res.json()["detail"]
