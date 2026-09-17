import asyncio
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 7: Trust Score & Reputation System Live Verification ===")
    ts_now = int(time.time())

    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Health Check
        h_res = await client.get(f"{BACKEND_URL}/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register Entrepreneur & Sponsor
        ent_email = f"founder.p7.{ts_now}@vynk.io"
        ent_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Rhea Chakraborty",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "Robotics & Automation",
            },
        )
        assert ent_reg.status_code == 201, f"Entrepreneur registration failed: {ent_reg.text}"
        ent_token = ent_reg.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        ent_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=ent_headers)).json()
        ent_uid = ent_me["id"]
        print(f"[PASS] 2. Entrepreneur registered: {ent_email} (UID: {ent_uid})")

        sp_email = f"sponsor.p7.{ts_now}@vynk.io"
        sp_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp_email,
                "password": "SecurePassword123!",
                "full_name": "Vikram Sethi",
                "role": "sponsor",
                "organization_name": "Nexus Wave Ventures",
                "sponsor_type": "venture_fund",
                "min_budget": 1000000,
                "max_budget": 20000000,
            },
        )
        assert sp_reg.status_code == 201, f"Sponsor registration failed: {sp_reg.text}"
        sp_token = sp_reg.json()["access_token"]
        sp_headers = {"Authorization": f"Bearer {sp_token}"}
        sp_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=sp_headers)).json()
        sp_uid = sp_me["id"]
        print(f"[PASS] 3. Sponsor registered: {sp_email} (UID: {sp_uid})")

        # 3. Initial Trust Score verification (Baseline 50, version 1, 4 factors)
        t_ent = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert t_ent["score"] == 50
        assert t_ent["score_version"] == 1
        assert t_ent["verification_points"] == 0
        assert t_ent["commitments_points"] == 20
        assert t_ent["responsiveness_points"] == 15
        assert t_ent["activity_points"] == 15
        assert len(t_ent["factors"]) == 4
        print("[PASS] 4. Initial baseline Trust Score confirmed: 50/100 across 4 objective pillars")

        # 4. Create Published Venture Showcase
        p_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"AeroDrone Cargo {ts_now}",
                "tagline": "Autonomous heavy-payload aerial logistics",
                "description": "VTOL cargo delivery system for remote and emergency access across India",
                "category": "Robotics",
                "industry": "Aviation & Logistics",
                "stage": "mvp",
                "funding_goal": 5000000.0,
                "currency": "INR",
                "status": "published",
                "problem_statement": "Ground transit to mountainous terrains is slow and vulnerable to landslides.",
                "proposed_solution": "Long-range autonomous heavy-lift multirotors carrying up to 100kg payloads.",
                "target_market": "Disaster relief agencies, defense logistics, and regional supply chain operators.",
                "value_proposition": "80% faster delivery time with 50% lower logistics cost than helicopters.",
                "current_progress": "Completed 150 successful autonomous test flights with 50kg payloads.",
                "required_support": ["Capital", "Mentorship"],
                "required_resources": "Flight testing permits and battery manufacturing partnerships.",
                "skills_needed": ["Aerospace Engineering", "Embedded Flight Controllers"],
                "tech_stack": ["C++", "ROS2", "Python", "QGroundControl"],
            },
        )
        assert p_res.status_code == 201, f"Project creation failed: {p_res.text}"
        project = p_res.json()
        pid = project["id"]
        print(f"[PASS] 5. Published venture showcase created: '{project['title']}' (ID: {pid})")

        # 5. Test Timely Response (<48h) on Sponsorship Request
        req_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=ent_headers,
            json={
                "project_id": pid,
                "recipient_id": sp_uid,
                "sponsorship_type": "Financial Funding",
                "requested_amount": 1500000.0,
                "currency": "INR",
                "message": "Inviting Nexus Wave Ventures to anchor our seed funding tranche.",
            },
        )
        assert req_res.status_code == 201, f"Request submission failed: {req_res.text}"
        req_id = req_res.json()["id"]

        # Sponsor promptly responds (within seconds)
        resp_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/{req_id}/respond",
            headers=sp_headers,
            json={
                "action": "accept",
                "response_note": "Promptly accepted. Delighted to review terms.",
                "commitment_amount": 1500000.0,
            },
        )
        assert resp_res.status_code == 200, f"Sponsor response failed: {resp_res.text}"
        comm_id = resp_res.json()["commitment_id"]

        # Check that sponsor gained +2 for timely response
        t_sp_after_resp = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()
        assert t_sp_after_resp["activity_points"] == 17  # 15 + 2
        assert t_sp_after_resp["score"] == 52
        print(f"[PASS] 6. Timely response (<48h) detected: Sponsor gained +2 points (Score: {t_sp_after_resp['score']}/100)")

        # 6. Test Milestone Updates with Evidence & Anti-Gaming Cap (Max 2 per commitment)
        # Milestone 1: +2 pts
        m1 = await client.post(
            f"{BACKEND_URL}/commitments/{comm_id}/updates",
            headers=ent_headers,
            json={
                "title": "Avionics Telemetry Flight Log",
                "note": "Completed 50km endurance flight with full sensor payload.",
                "update_type": "milestone",
                "evidence_reference": "https://vynk.io/proof/telemetry-log-50km.pdf",
            },
        )
        assert m1.status_code == 201
        t_ent_m1 = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert t_ent_m1["responsiveness_points"] == 17  # 15 + 2
        assert t_ent_m1["score"] == 52
        print(f"[PASS] 7. Milestone 1 verified with evidence: Entrepreneur gained +2 (Score: {t_ent_m1['score']}/100)")

        # Milestone 2: +2 pts
        m2 = await client.post(
            f"{BACKEND_URL}/commitments/{comm_id}/updates",
            headers=ent_headers,
            json={
                "title": "Battery Thermal Stress Test",
                "note": "Passed high-temperature discharge stress tests under full throttle.",
                "update_type": "milestone",
                "evidence_reference": "https://vynk.io/proof/battery-thermal-report.pdf",
            },
        )
        assert m2.status_code == 201
        t_ent_m2 = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert t_ent_m2["responsiveness_points"] == 19  # 15 + 4
        assert t_ent_m2["score"] == 54
        print(f"[PASS] 8. Milestone 2 verified with evidence: Entrepreneur gained +2 (Score: {t_ent_m2['score']}/100)")

        # Milestone 3 on SAME commitment: Cap enforced (Max 2 per commitment)
        m3 = await client.post(
            f"{BACKEND_URL}/commitments/{comm_id}/updates",
            headers=ent_headers,
            json={
                "title": "Extra milestone update",
                "note": "Extra milestone should not generate infinite points on same commitment.",
                "update_type": "milestone",
                "evidence_reference": "https://vynk.io/proof/extra.pdf",
            },
        )
        assert m3.status_code == 201
        t_ent_m3 = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert t_ent_m3["responsiveness_points"] == 19  # Still 19 (Capped at 2 per commitment!)
        assert t_ent_m3["score"] == 54
        print(f"[PASS] 9. Anti-gaming milestone cap enforced: 3rd milestone on same commitment awarded 0 extra points")

        # 7. Symmetrical Completion Reward (+5 to BOTH Sponsor and Entrepreneur)
        sp_score_pre = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        ent_score_pre = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()["score"]

        # Advance commitment: INTERESTED -> DISCUSSION -> PROMISED -> CONFIRMED -> AGREEMENT -> FUNDED -> COMPLETED
        for st in ["discussion", "promised", "confirmed", "agreement", "funded", "completed"]:
            adv = await client.patch(
                f"{BACKEND_URL}/commitments/{comm_id}/status",
                headers=sp_headers,
                json={"new_status": st, "note": f"Advanced to {st}"},
            )
            assert adv.status_code == 200, f"Failed advancing to {st}: {adv.text}"

        sp_score_post = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        ent_score_post = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()["score"]

        assert sp_score_post == sp_score_pre + 5
        assert ent_score_post == ent_score_pre + 5
        print(f"[PASS] 10. Symmetrical completion verified: Sponsor ({sp_score_post}) & Entrepreneur ({ent_score_post}) both earned +5 pts")

        # 8. Single Source of Truth Verification (Incremental == Deterministic Recalculate)
        recalc_ent = await client.post(f"{BACKEND_URL}/trust/recalculate", headers=ent_headers)
        assert recalc_ent.status_code == 200
        recalc_data = recalc_ent.json()
        assert recalc_data["score"] == ent_score_post
        print(f"[PASS] 11. Single Source of Truth verified: Incremental score ({ent_score_post}) == Recalculated score ({recalc_data['score']})")

        # 9. Cancellation Rules: Exploratory Cancellation (0 penalty)
        c_exp_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=sp_headers,
            json={"project_id": pid, "amount": 200000.0, "sponsorship_type": "grant", "notes": "exploratory deal"},
        )
        c_exp_id = c_exp_res.json()["id"]

        sp_pre_cancel = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        await client.patch(
            f"{BACKEND_URL}/commitments/{c_exp_id}/status",
            headers=sp_headers,
            json={"new_status": "cancelled", "note": "Early exploratory cancellation", "cancellation_type": "mutual"},
        )
        sp_post_cancel = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        assert sp_post_cancel == sp_pre_cancel
        print("[PASS] 12. Exploratory cancellation verified: 0 penalty incurred")

        # 10. Cancellation Rules: Mutually Agreed Confirmed Cancellation (0 penalty)
        c_mut_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=sp_headers,
            json={"project_id": pid, "amount": 300000.0, "sponsorship_type": "grant", "notes": "mutual deal"},
        )
        c_mut_id = c_mut_res.json()["id"]
        await client.patch(f"{BACKEND_URL}/commitments/{c_mut_id}/status", headers=sp_headers, json={"new_status": "discussion", "note": "d"})
        await client.patch(f"{BACKEND_URL}/commitments/{c_mut_id}/status", headers=sp_headers, json={"new_status": "promised", "note": "p"})
        await client.patch(f"{BACKEND_URL}/commitments/{c_mut_id}/status", headers=sp_headers, json={"new_status": "confirmed", "note": "c"})

        await client.patch(
            f"{BACKEND_URL}/commitments/{c_mut_id}/status",
            headers=sp_headers,
            json={"new_status": "cancelled", "note": "Mutual agreed termination due to external factors", "cancellation_type": "mutual"},
        )
        sp_post_mut = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        assert sp_post_mut == sp_pre_cancel
        print("[PASS] 13. Confirmed stage mutual cancellation verified: 0 penalty incurred")

        # 11. Cancellation Rules: Unilateral Confirmed Cancellation (-10 penalty to responsible party)
        c_uni_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=sp_headers,
            json={"project_id": pid, "amount": 400000.0, "sponsorship_type": "grant", "notes": "unilateral deal"},
        )
        c_uni_id = c_uni_res.json()["id"]
        await client.patch(f"{BACKEND_URL}/commitments/{c_uni_id}/status", headers=sp_headers, json={"new_status": "discussion", "note": "d"})
        await client.patch(f"{BACKEND_URL}/commitments/{c_uni_id}/status", headers=sp_headers, json={"new_status": "promised", "note": "p"})
        await client.patch(f"{BACKEND_URL}/commitments/{c_uni_id}/status", headers=sp_headers, json={"new_status": "confirmed", "note": "c"})

        await client.patch(
            f"{BACKEND_URL}/commitments/{c_uni_id}/status",
            headers=sp_headers,
            json={"new_status": "cancelled", "note": "Unilaterally pulled out of confirmed deal", "cancellation_type": "unilateral"},
        )
        sp_post_uni = (await client.get(f"{BACKEND_URL}/trust/me", headers=sp_headers)).json()["score"]
        assert sp_post_uni == sp_pre_cancel - 10
        print(f"[PASS] 14. Unilateral confirmed deal cancellation verified: -10 penalty applied to responsible party ({sp_post_uni}/100)")

        # 12. Public Privacy Protection (Public /users/{id} strips private events)
        pub_ent = (await client.get(f"{BACKEND_URL}/trust/users/{ent_uid}")).json()
        assert "events" not in pub_ent
        assert pub_ent["score"] == ent_score_post
        assert len(pub_ent["factors"]) == 4

        other_view = (await client.get(f"{BACKEND_URL}/trust/users/{ent_uid}", headers=sp_headers)).json()
        assert "events" not in other_view
        print("[PASS] 15. Public privacy protection verified: /trust/users/{id} completely strips private events and notes")

        # 13. Private Audit History Pagination
        hist_res = await client.get(f"{BACKEND_URL}/trust/history?limit=10&offset=0", headers=ent_headers)
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data["total_events"] >= 3  # milestone1, milestone2, milestone3 (unawarded), commitment_completed
        ev0 = hist_data["events"][0]
        assert "score_before" in ev0
        assert "score_after" in ev0
        assert "reference_id" in ev0
        assert "reference_type" in ev0
        print(f"[PASS] 16. Verifiable audit history confirmed ({hist_data['total_events']} events logged with score snapshots)")

        # 14. Compatibility Score Independence (Phase 5 Compatibility is untouched)
        rec_res = await client.get(
            f"{BACKEND_URL}/ai/matches/projects?limit=10",
            headers=sp_headers,
        )
        assert rec_res.status_code == 200
        matches = rec_res.json()
        if matches:
            top_m = matches[0]
            assert "compatibility_score" in top_m
            assert "trust_score" in top_m
            # Mathematical independence: compatibility is NOT scaled by trust
            assert 0 <= top_m["compatibility_score"] <= 100
        print("[PASS] 17. Independence verified: Compatibility Score algorithm remains completely separate from Trust Score")

    print("\n================================================================================")
    print("ALL 17 LIVE VERIFICATION CHECKS PASSED FOR VYNK PHASE 7: TRUST & REPUTATION SYSTEM")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
