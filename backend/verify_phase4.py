import asyncio
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 4: Discovery, Search & Opportunity Exploration Live Verification ===")
    ts = int(time.time())

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Health check
        res = await client.get(f"{BACKEND_URL}/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register Entrepreneur and create distinct published projects
        ent_email = f"founder.p4.{ts}@vynk.io"
        reg_ent = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Devi Raman",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "CleanTech & Renewable Energy",
            },
        )
        assert reg_ent.status_code == 201, f"Entrepreneur registration failed: {reg_ent.text}"
        ent_token = reg_ent.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        print(f"[PASS] 2. Entrepreneur registered: {ent_email}")

        # Create Project Alpha (CleanTech, MVP, ₹5,000,000, Bangalore)
        p_alpha = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"SolarGrid Quantum {ts}",
                "tagline": "Next-generation distributed solar microgrids for rural clusters",
                "description": "High-efficiency microinverters with mesh battery load management for tier-2/3 Indian communities.",
                "category": "CleanTech",
                "industry": "CleanTech & Renewable Energy",
                "stage": "mvp",
                "problem_statement": "Grid instability causes 40% outage times in semi-rural agro processing centers.",
                "proposed_solution": "Mesh solar batteries with real-time autonomous load balancing.",
                "target_market": "Rural agro cooperatives and micro-cold storage facilities in India.",
                "value_proposition": "99.8% uptime with 35% lower unit power cost.",
                "currency": "INR",
                "funding_goal": 5000000.0,
                "current_funding": 1000000.0,
                "location": "Bangalore, India",
                "required_support": ["grant", "equity_investment", "mentorship"],
                "tech_stack": ["Rust", "IoT", "React", "FastAPI"],
                "status": "published",
            },
        )
        assert p_alpha.status_code == 201, f"Project Alpha creation failed: {p_alpha.text}"
        alpha_id = p_alpha.json()["id"]

        # Create Project Beta (AI / ML, Prototype, ₹1,500,000, Hyderabad)
        p_beta = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"NeuroVision Diagnostics {ts}",
                "tagline": "Edge-computed retinal scans for early diabetic retinopathy detection",
                "description": "Affordable optical handheld scanners powered by localized ONNX neural networks.",
                "category": "AI / ML",
                "industry": "Healthcare & Biotech",
                "stage": "prototype",
                "problem_statement": "Screening backlogs lead to irreversible vision loss among diabetic patients.",
                "proposed_solution": "Handheld 45-second screening camera running on device without internet.",
                "target_market": "Primary health clinics, optometrists, and regional diagnostic labs.",
                "value_proposition": "Instant 98.4% sensitivity reading without cloud dependency.",
                "currency": "INR",
                "funding_goal": 1500000.0,
                "current_funding": 300000.0,
                "location": "Hyderabad, India",
                "required_support": ["grant", "lab_access"],
                "tech_stack": ["PyTorch", "C++", "Flutter"],
                "status": "published",
            },
        )
        assert p_beta.status_code == 201, f"Project Beta creation failed: {p_beta.text}"
        beta_id = p_beta.json()["id"]

        # Create Project Gamma (Fintech, Growth, ₹10,000,000, Mumbai)
        p_gamma = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"KisanCredit Neo {ts}",
                "tagline": "Automated collateral-free microcredit underwriting for smallholder farmers",
                "description": "Satellite imagery and UPI cash flow telemetry to underwrite small farm loans in under 3 minutes.",
                "category": "Fintech",
                "industry": "FinTech & Web3",
                "stage": "scaling",
                "problem_statement": "Informal money lenders charge 36%+ APR due to lack of formal credit footprints.",
                "proposed_solution": "Direct satellite crop yield index scored against local grain mandate payments.",
                "target_market": "120M smallholder farming families across India.",
                "value_proposition": "Under 3-minute disbursement with 1.4% NPA rate.",
                "currency": "INR",
                "funding_goal": 10000000.0,
                "current_funding": 7500000.0,
                "location": "Mumbai, India",
                "required_support": ["debt_financing", "regulatory_advisory"],
                "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
                "status": "published",
            },
        )
        assert p_gamma.status_code == 201, f"Project Gamma creation failed: {p_gamma.text}"
        gamma_id = p_gamma.json()["id"]
        print(f"[PASS] 3. Published 3 diverse projects in INR: Alpha ({alpha_id}), Beta ({beta_id}), Gamma ({gamma_id})")

        # 3. Register Multiple Sponsors
        # Sponsor 1: Venture Capital
        sp1_email = f"vc.partner.{ts}@matrixcapital.in"
        reg_sp1 = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp1_email,
                "password": "SecurePassword123!",
                "full_name": "Vikram Singhania",
                "role": "sponsor",
                "organization_name": "Matrix Horizon Ventures",
                "sponsor_type": "venture_capital",
                "min_budget": 2500000.0,
                "max_budget": 20000000.0,
            },
        )
        assert reg_sp1.status_code == 201, f"Sponsor 1 registration failed: {reg_sp1.text}"
        sp1_token = reg_sp1.json()["access_token"]
        sp1_headers = {"Authorization": f"Bearer {sp1_token}"}
        sp1_id = reg_sp1.json()["user_id"]

        # Update Sponsor 1 detailed profile
        await client.put(
            f"{BACKEND_URL}/profiles/me",
            headers=sp1_headers,
            json={
                "bio": "Early and growth stage venture firm backing climate-tech and deep-tech pioneers.",
                "location": "Bangalore, India",
                "organization_name": "Matrix Horizon Ventures",
                "sponsor_type": "venture_capital",
                "min_budget": 2500000,
                "max_budget": 20000000,
                "focus_industries": ["CleanTech & Renewable Energy", "DeepTech & Hardware"],
                "preferred_sponsorship_types": ["equity_investment", "mentorship"],
            },
        )

        # Sponsor 2: Angel Investor
        sp2_email = f"angel.{ts}@indiainnovates.org"
        reg_sp2 = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp2_email,
                "password": "SecurePassword123!",
                "full_name": "Ananya Deshmukh",
                "role": "sponsor",
                "organization_name": "Deshmukh Angel Office",
                "sponsor_type": "angel",
                "min_budget": 500000.0,
                "max_budget": 2500000.0,
            },
        )
        assert reg_sp2.status_code == 201, f"Sponsor 2 registration failed: {reg_sp2.text}"
        sp2_token = reg_sp2.json()["access_token"]
        sp2_headers = {"Authorization": f"Bearer {sp2_token}"}
        sp2_id = reg_sp2.json()["user_id"]

        # Update Sponsor 2 detailed profile
        await client.put(
            f"{BACKEND_URL}/profiles/me",
            headers=sp2_headers,
            json={
                "bio": "Physician turned health-tech angel investor providing seed grants and clinical trials access.",
                "location": "Hyderabad, India",
                "organization_name": "Deshmukh Angel Office",
                "sponsor_type": "angel",
                "min_budget": 500000,
                "max_budget": 2500000,
                "focus_industries": ["Healthcare & Biotech", "AI / ML"],
                "preferred_sponsorship_types": ["grant", "lab_access"],
            },
        )
        print(f"[PASS] 4. Registered 2 diverse sponsors: Matrix Horizon ({sp1_id}) & Deshmukh Angel ({sp2_id})")

        # 4. Project Discovery Tests
        # 4a. Keyword Search
        srch_res = await client.get(f"{BACKEND_URL}/projects/?search=SolarGrid&page=1&limit=10")
        assert srch_res.status_code == 200
        data = srch_res.json()
        assert data["total"] >= 1
        assert any(p["id"] == alpha_id for p in data["results"])
        print("[PASS] 4a. Keyword search matches project title correctly")

        # 4b. Category and Stage Filtering
        cat_res = await client.get(f"{BACKEND_URL}/projects/?category=Fintech&stage=scaling&page=1&limit=10")
        assert cat_res.status_code == 200
        data = cat_res.json()
        assert any(p["id"] == gamma_id for p in data["results"])
        assert not any(p["id"] == alpha_id for p in data["results"])
        print("[PASS] 4b. Multi-criteria filtering (Category: Fintech, Stage: scaling) works")

        # 4c. Funding Range Filtering
        fund_res = await client.get(f"{BACKEND_URL}/projects/?min_funding=2000000&max_funding=6000000&page=1&limit=10")
        assert fund_res.status_code == 200
        data = fund_res.json()
        item_ids = [p["id"] for p in data["results"]]
        assert alpha_id in item_ids
        assert beta_id not in item_ids  # Beta is 1.5M < 2M
        assert gamma_id not in item_ids  # Gamma is 10M > 6M
        print("[PASS] 4c. Funding range filtering (₹2M - ₹6M) correctly isolates Project Alpha")

        # 4d. Location Filtering
        loc_res = await client.get(f"{BACKEND_URL}/projects/?location=Hyderabad&page=1&limit=10")
        assert loc_res.status_code == 200
        data = loc_res.json()
        assert any(p["id"] == beta_id for p in data["results"])
        print("[PASS] 4d. Location filtering (Hyderabad) returns correct projects")

        # 4e. Required Support Filtering
        supp_res = await client.get(f"{BACKEND_URL}/projects/?required_support=lab_access&page=1&limit=10")
        assert supp_res.status_code == 200
        data = supp_res.json()
        assert any(p["id"] == beta_id for p in data["results"])
        print("[PASS] 4e. Required support filtering ('lab_access') works")

        # 4f. Sorting
        sort_res = await client.get(f"{BACKEND_URL}/projects/?sort=funding_high&page=1&limit=10")
        assert sort_res.status_code == 200
        items = sort_res.json()["results"]
        for i in range(len(items) - 1):
            assert items[i]["funding_goal"] >= items[i + 1]["funding_goal"]
        print("[PASS] 4f. Sorting by funding_high works properly")

        # 4g. Pagination
        page1 = await client.get(f"{BACKEND_URL}/projects/?page=1&limit=2")
        assert page1.status_code == 200
        p1_data = page1.json()
        assert len(p1_data["results"]) <= 2
        assert p1_data["page"] == 1
        assert p1_data["limit"] == 2
        assert "total" in p1_data
        assert "total_pages" in p1_data
        print(f"[PASS] 4g. Project pagination works: Total {p1_data['total']} projects, {p1_data['total_pages']} pages")

        # 4h. Backward Compatibility (omitting page parameter returns flat list)
        flat_res = await client.get(f"{BACKEND_URL}/projects/?limit=5")
        assert flat_res.status_code == 200
        flat_data = flat_res.json()
        assert isinstance(flat_data, list), "Expected flat list when page param is omitted"
        print("[PASS] 4h. Backward compatibility preserved (flat list returned when page parameter omitted)")

        # 5. Sponsor Discovery Tests
        # 5a. Sponsor Search
        sp_srch = await client.get(f"{BACKEND_URL}/sponsors/?search=Matrix&page=1&limit=10")
        assert sp_srch.status_code == 200
        sp_data = sp_srch.json()
        assert sp_data["total"] >= 1
        assert any(s["user_id"] == sp1_id for s in sp_data["results"])
        print("[PASS] 5a. Sponsor search by organization name works")

        # 5b. Sponsor Type Filtering
        sp_type = await client.get(f"{BACKEND_URL}/sponsors/?sponsor_type=angel&page=1&limit=10")
        assert sp_type.status_code == 200
        sp_data = sp_type.json()
        assert any(s["user_id"] == sp2_id for s in sp_data["results"])
        assert not any(s["user_id"] == sp1_id for s in sp_data["results"])
        print("[PASS] 5b. Sponsor type filtering ('angel') isolates angel investor")

        # 5c. Sponsor Budget Range Filtering
        sp_budget = await client.get(f"{BACKEND_URL}/sponsors/?min_budget=5000000&page=1&limit=10")
        assert sp_budget.status_code == 200
        sp_data = sp_budget.json()
        assert any(s["user_id"] == sp1_id for s in sp_data["results"])
        assert not any(s["user_id"] == sp2_id for s in sp_data["results"])
        print("[PASS] 5c. Sponsor budget range filtering (min_budget >= ₹5,000,000) works")

        # 5d. Sponsor Location & Area Filtering
        sp_area = await client.get(f"{BACKEND_URL}/sponsors/?sponsorship_type=lab_access&location=Hyderabad&page=1&limit=10")
        assert sp_area.status_code == 200
        sp_data = sp_area.json()
        assert any(s["user_id"] == sp2_id for s in sp_data["results"])
        print("[PASS] 5d. Sponsor compound filtering (sponsorship_type & location) works")

        # 5e. Sponsor Sorting
        sp_sort = await client.get(f"{BACKEND_URL}/sponsors/?sort=budget_high&page=1&limit=10")
        assert sp_sort.status_code == 200
        sp_items = sp_sort.json()["results"]
        for i in range(len(sp_items) - 1):
            assert sp_items[i]["max_budget"] >= sp_items[i + 1]["max_budget"]
        print("[PASS] 5e. Sponsor sorting by budget_high works")

        # 5f. Sponsor Pagination
        sp_page1 = await client.get(f"{BACKEND_URL}/sponsors/?page=1&limit=1")
        assert sp_page1.status_code == 200
        sp_p1 = sp_page1.json()
        assert len(sp_p1["results"]) == 1
        assert sp_p1["total_pages"] >= 2
        print(f"[PASS] 5f. Sponsor pagination works (page 1, limit 1, total_pages={sp_p1['total_pages']})")

        # 6. Privacy & Security Assertions
        # 6a. Public sponsor list MUST NOT leak email, hashed_password, or raw user objects
        for item in sp_data["results"]:
            assert "email" not in item, f"LEAK: email found in sponsor public item {item}"
            assert "password" not in item, f"LEAK: password found in sponsor item {item}"
            assert "hashed_password" not in item, f"LEAK: hashed_password found in sponsor item {item}"
        print("[PASS] 6a. Sponsor public discovery strictly prevents email & password leaks")

        # 6b. Single sponsor public profile endpoint privacy
        single_sp = await client.get(f"{BACKEND_URL}/sponsors/{sp1_id}")
        assert single_sp.status_code == 200
        s_data = single_sp.json()
        assert "email" not in s_data, "LEAK: email found in single sponsor endpoint"
        assert "hashed_password" not in s_data, "LEAK: hashed_password found in single sponsor endpoint"
        print("[PASS] 6b. Single sponsor profile endpoint maintains complete privacy protection")

        # 7. Proposal Commitment in INR & Sponsor Interaction Flow
        prop_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=sp1_headers,
            json={
                "project_id": alpha_id,
                "amount": 3500000.0,
                "sponsorship_type": "equity_investment",
                "notes": "Interested in leading your Series Seed round for Karnataka expansion.",
            },
        )
        assert prop_res.status_code == 201, f"Proposal creation failed: {prop_res.text}"
        prop_data = prop_res.json()
        assert prop_data["amount"] == 3500000.0
        print("[PASS] 7. Sponsorship proposal in INR (₹3,500,000) successfully submitted and linked")

        # 8. Frontend Discovery Pages Accessibility
        p_page_res = await client.get(f"{FRONTEND_URL}/projects")
        assert p_page_res.status_code == 200, f"Frontend /projects unreachable: {p_page_res.status_code}"
        sp_page_res = await client.get(f"{FRONTEND_URL}/sponsors")
        assert sp_page_res.status_code == 200, f"Frontend /sponsors unreachable: {sp_page_res.status_code}"
        print("[PASS] 8. Frontend routes (/projects, /sponsors) are healthy and serving 200 OK")

    print("\n==========================================================================")
    print("ALL PHASE 4 LIVE VERIFICATION TESTS PASSED SUCCESSFULLY! (8/8 CHECKPOINTS)")
    print("==========================================================================")


if __name__ == "__main__":
    asyncio.run(main())
