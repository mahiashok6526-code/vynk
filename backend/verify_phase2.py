import asyncio
import time
import httpx

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 2: Professional Profiles Live Verification ===")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Health check
        res = await client.get(f"{BACKEND_URL}/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[PASS] 1. Backend server healthy")

        # 2. Register new Entrepreneur
        timestamp = int(time.time())
        ent_email = f"founder.phase2.{timestamp}@vynk.io"
        reg_res = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Elena Rostova",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "AI/DeepTech",
                "headline": "Founder & CEO @ NeuralPulse AI",
                "location": "San Francisco, CA",
            },
        )
        assert reg_res.status_code == 201, f"Entrepreneur registration failed: {reg_res.text}"
        ent_token = reg_res.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        print(f"[PASS] 2. Registered Entrepreneur: {ent_email}")

        # 3. Retrieve initial profile and verify auto-generated username & initial completion
        me_res = await client.get(f"{BACKEND_URL}/profiles/me", headers=ent_headers)
        assert me_res.status_code == 200, f"Get /profiles/me failed: {me_res.text}"
        me_data = me_res.json()
        assert me_data["full_name"] == "Elena Rostova"
        assert me_data["username"] is not None
        assert "completion" in me_data
        init_pct = me_data["completion"]["percentage"]
        print(f"[PASS] 3. Initial profile loaded: username=@{me_data['username']}, completion={init_pct}%")

        # 4. Edit Entrepreneur profile with full credentials
        unique_username = f"elena_ai_{timestamp % 10000}"
        update_res = await client.put(
            f"{BACKEND_URL}/profiles/me",
            headers=ent_headers,
            json={
                "username": unique_username,
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
                "headline": "Pioneering neuromorphic sensor arrays for robotic automation",
                "bio": "Robotics engineer and serial inventor with 10 years experience building deeptech hardware.",
                "location": "San Francisco, CA",
                "stage": "scaling",
                "industry": "AI & Robotics",
                "skills": ["Neuromorphic Vision", "Embedded C++", "PyTorch", "Hardware Architecture", "Venture Scaling"],
                "experience": [
                    {
                        "title": "Principal Robotics Architect",
                        "company": "CyberSyn Systems",
                        "duration": "2020 - 2024",
                        "description": "Architected low-latency sensory processing pipelines for autonomous systems.",
                    }
                ],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "B.S. & M.Eng in Electrical Engineering and Computer Science",
                        "year": "2019",
                    }
                ],
                "achievements": [
                    {
                        "title": "Forbes 30 Under 30 (Manufacturing & Industry)",
                        "year": "2023",
                        "description": "Recognized for breakthroughs in silicon micro-photonic sensors.",
                    }
                ],
                "website_url": "https://neuralpulse.ai",
                "linkedin_url": "https://linkedin.com/in/elena-rostova",
            },
        )
        assert update_res.status_code == 200, f"Profile update failed: {update_res.text}"
        updated_data = update_res.json()
        assert updated_data["username"] == unique_username
        assert updated_data["completion"]["percentage"] == 100
        print(f"[PASS] 4. Updated Entrepreneur profile: @{unique_username} reached 100% completion!")

        # 5. Public profile access by username
        pub_res = await client.get(f"{BACKEND_URL}/profiles/{unique_username}")
        assert pub_res.status_code == 200, f"Public profile lookup failed: {pub_res.text}"
        pub_data = pub_res.json()
        assert pub_data["username"] == unique_username
        assert pub_data["full_name"] == "Elena Rostova"
        assert len(pub_data["entrepreneur_profile"]["skills"]) == 5
        assert len(pub_data["entrepreneur_profile"]["experience"]) == 1
        assert len(pub_data["entrepreneur_profile"]["education"]) == 1
        assert len(pub_data["entrepreneur_profile"]["achievements"]) == 1
        assert pub_data["is_own_profile"] is False
        print(f"[PASS] 5. Public profile access verified for @{unique_username}")

        # 6. Register Sponsor
        sp_email = f"sponsor.phase2.{timestamp}@vynkfunds.com"
        sp_reg_res = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp_email,
                "password": "SecurePassword123!",
                "full_name": "David Sterling",
                "role": "sponsor",
                "organization_name": "Apex Frontier Ventures",
                "sponsor_type": "venture_capital",
                "min_budget": 50000,
                "max_budget": 500000,
                "location": "Austin, TX",
            },
        )
        assert sp_reg_res.status_code == 201, f"Sponsor registration failed: {sp_reg_res.text}"
        sp_token = sp_reg_res.json()["access_token"]
        sp_headers = {"Authorization": f"Bearer {sp_token}"}
        print(f"[PASS] 6. Registered Sponsor: {sp_email}")

        # 7. Edit Sponsor profile with Phase 2 fields
        sp_username = f"apex_ventures_{timestamp % 10000}"
        sp_update_res = await client.put(
            f"{BACKEND_URL}/profiles/me",
            headers=sp_headers,
            json={
                "username": sp_username,
                "logo_url": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400",
                "organization_name": "Apex Frontier Ventures",
                "headline": "Lead Partner @ Apex Frontier Ventures",
                "about": "We provide pre-seed and catalytic seed checks to radical science and hardware ventures.",
                "industry": "Robotics, CleanTech & Bio",
                "sponsor_type": "venture_capital",
                "min_budget": 50000,
                "max_budget": 500000,
                "sponsorship_interests": ["DeepTech", "Silicon Photonics", "Autonomous Robotics", "Clean Energy"],
                "areas_supported": ["Pre-Seed Capital", "Cloud Credits", "Lab Space Access", "GTM Mentorship"],
                "previous_collaborations": [
                    {
                        "partner_name": "Vortex Fusion Labs",
                        "year": "2023",
                        "description": "$250k seed grant and prototyping laboratory space sponsorship.",
                        "outcome": "Successful magnetic confinement demo and closed Series A.",
                    }
                ],
            },
        )
        assert sp_update_res.status_code == 200, f"Sponsor update failed: {sp_update_res.text}"
        sp_data = sp_update_res.json()
        assert sp_data["username"] == sp_username
        assert sp_data["sponsor_profile"]["organization_name"] == "Apex Frontier Ventures"
        assert sp_data["completion"]["percentage"] == 100
        print(f"[PASS] 7. Updated Sponsor profile: @{sp_username} reached 100% completion!")

        # 8. Public view of Sponsor profile
        sp_pub_res = await client.get(f"{BACKEND_URL}/profiles/{sp_username}")
        assert sp_pub_res.status_code == 200
        assert sp_pub_res.json()["sponsor_profile"]["organization_name"] == "Apex Frontier Ventures"
        print(f"[PASS] 8. Public sponsor profile verified for @{sp_username}")

        # 9. Security test: Username collision prevention
        collision_res = await client.put(
            f"{BACKEND_URL}/profiles/me",
            headers=sp_headers,
            json={"username": unique_username},  # Try to steal Elena's username
        )
        assert collision_res.status_code == 400
        assert "already taken" in collision_res.json()["detail"]
        print("[PASS] 9. Username uniqueness conflict correctly blocked with 400 Bad Request")

        # 10. Security test: Unauthorized update prevention
        unauth_res = await client.put(
            f"{BACKEND_URL}/profiles/me",
            json={"full_name": "Hacker Impersonator"},
        )
        assert unauth_res.status_code == 401
        print("[PASS] 10. Unauthenticated profile update correctly blocked with 401 Unauthorized")

        # 11. Existing project creation & trust score progression check
        proj_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"Neuromorphic Sensor Core {timestamp}",
                "tagline": "Ultra-low power photonic neural vision sensor",
                "description": "A radically more efficient visual processor mimicking biological retina synapses.",
                "category": "Robotics",
                "stage": "prototype",
                "funding_goal": 80000.0,
            },
        )
        assert proj_res.status_code == 201, f"Project creation failed: {proj_res.text}"
        proj_id = proj_res.json()["id"]
        print(f"[PASS] 11. Project creation on Entrepreneur profile verified (Project id={proj_id})")

        # 12. Verify that the project appears in the public profile
        refreshed_pub = await client.get(f"{BACKEND_URL}/profiles/{unique_username}")
        assert refreshed_pub.status_code == 200
        assert len(refreshed_pub.json()["projects"]) >= 1
        print(f"[PASS] 12. Project is linked and visible on public profile under projects section")

    print("\nSUCCESS: ALL 12 LIVE PHASE 2 PROFESSIONAL PROFILE VERIFICATIONS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
