import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    import time
    ts = int(time.time() * 1000)
    email = f"p4_ent_{ts}@vynk.io"
    password = "SecurePassword123!"
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"P4 Entrepreneur {ts}",
            "role": "entrepreneur",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sponsor_client(client: AsyncClient):
    import time
    ts = int(time.time() * 1000)
    email = f"p4_sp_{ts}@vynk.io"
    password = "SecurePassword123!"
    username = f"p4_sponsor_{ts}"[:28]
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"P4 Angel Sponsor {ts}",
            "role": "sponsor",
            "organization_name": "Apex Frontier Ventures",
            "sponsor_type": "venture_capital",
            "industry": "DeepTech",
            "min_budget": 50000,
            "max_budget": 2000000,
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Set exact username and details via profile update
    prof_res = await client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "username": username,
            "organization_name": "Apex Frontier Ventures",
            "industry": "DeepTech",
            "sponsor_type": "venture_capital",
            "focus_industries": ["DeepTech", "AI & Robotics"],
            "min_budget": 50000,
            "max_budget": 2000000,
            "preferred_sponsorship_types": ["grant", "equity"],
            "areas_supported": ["capital", "compute_credits"],
        },
    )
    assert prof_res.status_code == 200, prof_res.text

    return {
        "headers": headers,
        "username": username,
        "email": email,
    }


@pytest.mark.asyncio
async def test_project_search_and_advanced_filters(client: AsyncClient, auth_headers: dict):
    import time
    ts = int(time.time() * 1000)

    # Create distinct projects
    p1 = await client.post(
        "/api/v1/projects/",
        headers=auth_headers,
        json={
            "title": f"QuantumGrid Power {ts}",
            "tagline": "Next-generation energy distribution using quantum sensors",
            "description": "Building hardware and software for autonomous electrical microgrids.",
            "category": "CleanTech",
            "industry": "Energy",
            "stage": "prototype",
            "problem_statement": "Grid congestion leads to 15% transmission loss across standard lines.",
            "proposed_solution": "Cryogenic sensors balance load dynamically across local storage banks.",
            "target_market": "Municipal utilities and high-power compute datacenters.",
            "value_proposition": "Reduces peak-load energy wastage by 80% with zero downtime.",
            "funding_goal": 500000.0,
            "funding_received": 100000.0,
            "currency": "INR",
            "required_support": ["Capital", "Hardware"],
            "location": "Bengaluru, India",
            "status": "published",
        },
    )
    assert p1.status_code == 201, p1.text
    p1_data = p1.json()
    assert p1_data["currency"] == "INR"

    p2 = await client.post(
        "/api/v1/projects/",
        headers=auth_headers,
        json={
            "title": f"NeuroScan Medical {ts}",
            "tagline": "AI non-invasive diagnostics for neurological conditions",
            "description": "High-throughput spectral analysis detecting micro-trauma in minutes.",
            "category": "HealthTech",
            "industry": "Healthcare",
            "stage": "mvp",
            "problem_statement": "Concussions and early neurological degradation take weeks to diagnose.",
            "proposed_solution": "Handheld infrared optical scanner powered by convolutional neural nets.",
            "target_market": "Hospital trauma wards and sports athletic facilities.",
            "value_proposition": "Instant 3-minute risk stratification with 98% laboratory accuracy.",
            "funding_goal": 2500000.0,
            "funding_received": 500000.0,
            "currency": "INR",
            "required_support": ["Compute Credits", "Mentorship"],
            "location": "Hyderabad, India",
            "status": "seeking_sponsorship",
        },
    )
    assert p2.status_code == 201, p2.text

    # 1. Search by keyword
    search_res = await client.get(f"/api/v1/projects/?search=QuantumGrid")
    assert search_res.status_code == 200
    search_items = search_res.json()
    assert any(p["id"] == p1_data["id"] for p in search_items)
    assert not any(p["id"] == p2.json()["id"] for p in search_items)

    # 2. Filter by category
    cat_res = await client.get(f"/api/v1/projects/?category=HealthTech")
    assert cat_res.status_code == 200
    cat_items = cat_res.json()
    assert any(p["id"] == p2.json()["id"] for p in cat_items)
    assert not any(p["id"] == p1_data["id"] for p in cat_items)

    # 3. Filter by stage
    stage_res = await client.get(f"/api/v1/projects/?stage=prototype")
    assert stage_res.status_code == 200
    stage_items = stage_res.json()
    assert any(p["id"] == p1_data["id"] for p in stage_items)

    # 4. Filter by required_support
    supp_res = await client.get(f"/api/v1/projects/?required_support=Hardware")
    assert supp_res.status_code == 200
    supp_items = supp_res.json()
    assert any(p["id"] == p1_data["id"] for p in supp_items)

    # 5. Filter by funding range
    range_res = await client.get(f"/api/v1/projects/?min_funding=1000000&max_funding=3000000")
    assert range_res.status_code == 200
    range_items = range_res.json()
    assert any(p["id"] == p2.json()["id"] for p in range_items)
    assert not any(p["id"] == p1_data["id"] for p in range_items)

    # 6. Filter by location
    loc_res = await client.get(f"/api/v1/projects/?location=Bengaluru")
    assert loc_res.status_code == 200
    loc_items = loc_res.json()
    assert any(p["id"] == p1_data["id"] for p in loc_items)


@pytest.mark.asyncio
async def test_project_sorting_and_pagination(client: AsyncClient):
    # Pagination query
    page_res = await client.get("/api/v1/projects/?page=1&limit=2&sort=funding_high")
    assert page_res.status_code == 200
    page_data = page_res.json()

    assert "results" in page_data
    assert "total" in page_data
    assert "page" in page_data
    assert "limit" in page_data
    assert "total_pages" in page_data
    assert page_data["page"] == 1
    assert page_data["limit"] == 2
    assert len(page_data["results"]) <= 2

    if len(page_data["results"]) >= 2:
        assert page_data["results"][0]["funding_goal"] >= page_data["results"][1]["funding_goal"]


@pytest.mark.asyncio
async def test_sponsor_discovery_and_privacy_protection(client: AsyncClient, sponsor_client: dict):
    # 1. Discover sponsors
    resp = await client.get("/api/v1/sponsors/")
    assert resp.status_code == 200
    sponsors = resp.json()
    assert isinstance(sponsors, list)
    assert len(sponsors) > 0

    # 2. Strict Privacy Verification: email and password must NEVER be exposed
    for sp in sponsors:
        assert "email" not in sp, "SECURITY VIOLATION: Sponsor email exposed in public discovery!"
        assert "password" not in sp, "SECURITY VIOLATION: Password exposed!"
        assert "hashed_password" not in sp, "SECURITY VIOLATION: Hashed password exposed!"
        assert "full_name" in sp
        assert "sponsor_type" in sp
        assert "currency" in sp
        assert sp["currency"] == "INR"

    # 3. Filter by sponsor type
    type_res = await client.get("/api/v1/sponsors/?sponsor_type=venture_capital")
    assert type_res.status_code == 200
    type_items = type_res.json()
    assert any(s["username"] == sponsor_client["username"] for s in type_items)

    # 4. Filter by budget range
    budget_res = await client.get("/api/v1/sponsors/?min_budget=1000000")
    assert budget_res.status_code == 200
    budget_items = budget_res.json()
    assert any(s["username"] == sponsor_client["username"] for s in budget_items)

    # 5. Search sponsor by organization or name
    s_search = await client.get("/api/v1/sponsors/?search=Apex+Frontier")
    assert s_search.status_code == 200
    search_items = s_search.json()
    assert any(s["username"] == sponsor_client["username"] for s in search_items)

    # 6. Pagination on sponsors
    p_resp = await client.get("/api/v1/sponsors/?page=1&limit=5&sort=budget_high")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert "results" in p_data
    assert "total" in p_data
    assert "page" in p_data
    assert "limit" in p_data
    assert "total_pages" in p_data

    # 7. Get single sponsor public profile by username
    single_res = await client.get(f"/api/v1/sponsors/{sponsor_client['username']}")
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["username"] == sponsor_client["username"]
    assert "email" not in single_data
    assert "hashed_password" not in single_data
