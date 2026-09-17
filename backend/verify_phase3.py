import asyncio
import time
import httpx

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 3: Project & Startup Showcase Live Verification ===")
    ts = int(time.time())

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Health check
        res = await client.get(f"{BACKEND_URL}/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register new Entrepreneur
        ent_email = f"founder.phase3.{ts}@vynk.io"
        reg_res = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Aria Thorne",
                "role": "entrepreneur",
                "stage": "prototype",
                "industry": "CleanTech & Carbon",
            },
        )
        assert reg_res.status_code == 201, f"Entrepreneur registration failed: {reg_res.text}"
        ent_token = reg_res.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        print(f"[PASS] 2. Entrepreneur registered successfully: {ent_email}")

        # 3. Test Validation: publishing incomplete showcase rejected
        invalid_pub_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": "Incomplete Showcase",
                "status": "published",
            },
        )
        assert invalid_pub_res.status_code == 400, f"Expected 400 validation error, got {invalid_pub_res.status_code}"
        assert "Cannot publish incomplete project showcase" in invalid_pub_res.json()["detail"]
        print("[PASS] 3. Project validation correctly prevented publishing incomplete showcase (400 Bad Request)")

        # 4. Save Project as Draft with partial information
        draft_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"TerraCapture Algal Bio-Matrix {ts % 10000}",
                "tagline": "Initial draft of our outdoor point-source carbon abatement project",
                "status": "draft",
            },
        )
        assert draft_res.status_code == 201, f"Draft creation failed: {draft_res.text}"
        draft_data = draft_res.json()
        proj_id = draft_data["id"]
        assert draft_data["status"] == "draft"
        print(f"[PASS] 4. Project saved as Draft successfully (Project ID: {proj_id}, Status: draft)")

        # 5. Verify draft appears in Entrepreneur's /my-projects
        my_proj_res = await client.get(f"{BACKEND_URL}/projects/my-projects", headers=ent_headers)
        assert my_proj_res.status_code == 200
        my_projects = my_proj_res.json()
        assert any(p["id"] == proj_id and p["status"] == "draft" for p in my_projects)
        print(f"[PASS] 5. Draft project retrieved in Entrepreneur /my-projects feed ({len(my_projects)} total projects)")

        # 6. Register Sponsor
        sp_email = f"sponsor.phase3.{ts}@frontierfund.com"
        sp_reg_res = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp_email,
                "password": "SecurePassword123!",
                "full_name": "Marcus Sterling",
                "role": "sponsor",
                "organization_name": "Frontier Climate Ventures",
                "sponsor_type": "venture_capital",
                "min_budget": 50000,
                "max_budget": 500000,
            },
        )
        assert sp_reg_res.status_code == 201
        sp_token = sp_reg_res.json()["access_token"]
        sp_headers = {"Authorization": f"Bearer {sp_token}"}
        print(f"[PASS] 6. Sponsor registered successfully: {sp_email}")

        # 7. Verify Sponsor cannot create project (Role Authorization Check)
        unauth_proj = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=sp_headers,
            json={
                "title": "Illicit Sponsor Project",
                "tagline": "Should be rejected",
                "description": "Not allowed",
            },
        )
        assert unauth_proj.status_code == 403, f"Expected 403 Forbidden, got {unauth_proj.status_code}"
        print("[PASS] 7. Security check: Sponsor correctly forbidden from creating projects (403 Forbidden)")

        # 8. Verify Sponsor cannot see draft in public discovery feed
        public_feed_res = await client.get(f"{BACKEND_URL}/projects/")
        assert public_feed_res.status_code == 200
        feed_projects = public_feed_res.json()
        assert not any(p["id"] == proj_id for p in feed_projects), "Draft project leaked into public feed!"
        print("[PASS] 8. Discovery Feed Security: Draft project is hidden from public sponsor discovery feed")

        # 9. Verify Sponsor cannot directly access draft via ID
        direct_draft_res = await client.get(f"{BACKEND_URL}/projects/{proj_id}", headers=sp_headers)
        assert direct_draft_res.status_code == 404, "Sponsor was able to access unlisted draft project!"
        print("[PASS] 9. Privacy check: Unauthorized visitor cannot view draft project (404 Not Found)")

        # 10. Entrepreneur updates project with all 22 showcase fields
        update_res = await client.put(
            f"{BACKEND_URL}/projects/{proj_id}",
            headers=ent_headers,
            json={
                "title": "TerraCapture Point-Source Algal Abatement",
                "tagline": "Scalable photobioreactors capturing 90% of flue-stack CO2 with bioplastic byproducts",
                "description": "TerraCapture builds high-surface-area vertical photobioreactor cassettes directly plumbed into industrial flue exhausts, using engineered microalgae to capture point-source carbon emissions while synthesizing valuable biomass.",
                "category": "CleanTech",
                "industry": "Carbon Capture & Industrial Decarbonization",
                "stage": "prototype",
                "problem_statement": "Heavy industrial manufacturing emits over 8 billion tons of CO2 annually. Current carbon capture solutions cost upwards of $120/ton and require massive energy footprints.",
                "proposed_solution": "Our proprietary thin-film photobioreactor cassettes utilize ambient waste heat and flue CO2 directly, lowering capture costs to $45/ton while producing sellable polyhydroxyalkanoate (PHA) bioplastics.",
                "target_market": "Cement kilns, steel mills, and chemical manufacturing plants across North America and Europe.",
                "value_proposition": "60% cheaper capture cost than amine scrubbers with a carbon-negative biopolymer revenue stream.",
                "current_progress": "Completed 1,200 hours of continuous test-bed operation at regional cement pilot facility.",
                "funding_goal": 250000.0,
                "funding_received": 50000.0,
                "required_support": ["Capital", "Hardware", "Cloud Resources", "Mentorship"],
                "required_resources": "Access to high-flow industrial flue testing facilities and EPA compliance mentorship.",
                "skills_needed": ["Bioprocess Engineering", "CFD Fluid Dynamics", "Industrial Automation"],
                "tech_stack": ["Python", "Rust", "MQTT", "TimescaleDB", "InfluxDB"],
                "website_url": "https://terracapture.vynk.example",
                "pitch_deck_url": "https://terracapture.vynk.example/deck.pdf",
                "video_url": "https://youtube.com/watch?v=terracapture_demo",
                "cover_image_url": "https://images.unsplash.com/photo-1509391365360-2e959784a276?w=800",
                "location": "Boulder, CO, USA",
                "timeline": "Q4 2026: Commercial multi-cassette deployment at 2 industrial partner sites.",
            },
        )
        assert update_res.status_code == 200, f"Project update failed: {update_res.text}"
        print("[PASS] 10. Entrepreneur successfully updated project with all 22 showcase metadata fields")

        # 11. Entrepreneur publishes the project
        publish_res = await client.post(f"{BACKEND_URL}/projects/{proj_id}/publish", headers=ent_headers)
        assert publish_res.status_code == 200, f"Publish failed: {publish_res.text}"
        published_data = publish_res.json()
        assert published_data["status"] == "published"
        print(f"[PASS] 11. Project successfully validated and published (Status: {published_data['status']})")

        # 12. Sponsor discovers published project in feed
        pub_feed = await client.get(f"{BACKEND_URL}/projects/", headers=sp_headers)
        assert pub_feed.status_code == 200
        found_in_feed = next((p for p in pub_feed.json() if p["id"] == proj_id), None)
        assert found_in_feed is not None, "Published project not found in discovery feed!"
        assert found_in_feed["title"] == "TerraCapture Point-Source Algal Abatement"
        assert found_in_feed["founder"]["full_name"] == "Aria Thorne"
        assert found_in_feed["founder"]["trust_score"] >= 50
        print(f"[PASS] 12. Sponsor discovers published project in feed with founder verification & trust score preview")

        # 13. Search and filtering verification
        cat_filter = await client.get(f"{BACKEND_URL}/projects/?category=CleanTech")
        assert any(p["id"] == proj_id for p in cat_filter.json()), "Category filter failed!"

        stage_filter = await client.get(f"{BACKEND_URL}/projects/?stage=prototype")
        assert any(p["id"] == proj_id for p in stage_filter.json()), "Stage filter failed!"

        supp_filter = await client.get(f"{BACKEND_URL}/projects/?required_support=Hardware")
        assert any(p["id"] == proj_id for p in supp_filter.json()), "Required support filter failed!"

        search_filter = await client.get(f"{BACKEND_URL}/projects/?search=TerraCapture")
        assert any(p["id"] == proj_id for p in search_filter.json()), "Search filter failed!"
        print("[PASS] 13. Project filtering by Category, Stage, Required Support, and Search validated")

        # 14. Sponsor views full project detail page
        detail_res = await client.get(f"{BACKEND_URL}/projects/{proj_id}", headers=sp_headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["problem_statement"] is not None
        assert detail["proposed_solution"] is not None
        assert detail["target_market"] is not None
        assert detail["value_proposition"] is not None
        assert len(detail["tech_stack"]) == 5
        assert len(detail["required_support"]) == 4
        assert detail["funding_goal"] == 250000.0
        print(f"[PASS] 14. Sponsor retrieves full 12-tier project showcase specification (Goal: ${detail['funding_goal']:,.2f})")

        # 15. Sponsor initiates sponsorship interest / commitment
        comm_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=sp_headers,
            json={
                "project_id": proj_id,
                "amount": 75000.0,
                "sponsorship_type": "grant",
                "status": "interested",
                "notes": "Frontier Climate Ventures initial evaluation for pilot tranche.",
            },
        )
        assert comm_res.status_code == 201, f"Commitment failed: {comm_res.text}"
        comm = comm_res.json()
        print(f"[PASS] 15. Sponsor initiated sponsorship commitment: ID={comm['id']}, Amount=${comm['amount']:,.2f}, Status={comm['status']}")

        # 16. Security test: Another entrepreneur cannot edit or hijack this project
        other_ent_res = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": f"intruder.{ts}@vynk.io",
                "password": "Password123!",
                "full_name": "Intruder User",
                "role": "entrepreneur",
            },
        )
        intruder_headers = {"Authorization": f"Bearer {other_ent_res.json()['access_token']}"}
        hijack_res = await client.put(
            f"{BACKEND_URL}/projects/{proj_id}",
            headers=intruder_headers,
            json={"title": "Hijacked Title"},
        )
        assert hijack_res.status_code == 403, "Ownership authorization failed: non-owner was allowed to edit!"
        print("[PASS] 16. Ownership authorization security verified (Non-owner receives 403 Forbidden)")

        # 17. Project Archiving by Owner
        arch_res = await client.post(f"{BACKEND_URL}/projects/{proj_id}/archive", headers=ent_headers)
        assert arch_res.status_code == 200
        assert arch_res.json()["status"] == "archived"
        print(f"[PASS] 17. Entrepreneur successfully archived project showcase")

        # 18. Verify archived project is removed from public discovery
        post_arch_feed = await client.get(f"{BACKEND_URL}/projects/")
        assert not any(p["id"] == proj_id for p in post_arch_feed.json()), "Archived project still in public feed!"
        print("[PASS] 18. Archived project correctly excluded from public sponsor discovery feed")

    print("\nSUCCESS: ALL 18 LIVE PHASE 3 SHOWCASE VERIFICATION CHECKS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
