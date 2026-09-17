import asyncio
import sys
import time
from datetime import datetime, timezone, timedelta
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 6: Sponsorship & Commitment Management Live Verification ===")
    ts = int(time.time())

    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Health check
        res = await client.get(f"{BACKEND_URL}/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register Entrepreneur & create venture showcase
        ent_email = f"founder.p6.{ts}@vynk.io"
        reg_ent = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Arjun Singhal",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "CleanTech & Autonomous Systems",
            },
        )
        assert reg_ent.status_code == 201, f"Entrepreneur registration failed: {reg_ent.text}"
        ent_token = reg_ent.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        print(f"[PASS] 2. Entrepreneur registered successfully: {ent_email}")

        p_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"AeroKite Energy {ts}",
                "tagline": "Tethered airborne wind turbine systems for high-altitude wind capture",
                "description": "Autonomous carbon-composite kite wing generating continuous megawatt-scale power from tropospheric jet streams.",
                "category": "CleanTech",
                "industry": "CleanTech & Autonomous Systems",
                "stage": "mvp",
                "funding_goal": 5000000.0,
                "currency": "INR",
                "required_support": ["Capital", "Hardware", "Testing / Facilities"],
            },
        )
        assert p_res.status_code == 201, f"Project creation failed: {p_res.text}"
        project_id = p_res.json()["id"]
        print(f"[PASS] 3. Venture showcase published: AeroKite Energy (ID: {project_id}) in INR (₹)")

        # 3. Register Sponsor
        spon_email = f"sponsor.p6.{ts}@vynk.io"
        reg_spon = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": spon_email,
                "password": "SponsorPassword123!",
                "full_name": "Radhika Mehra",
                "role": "sponsor",
                "organization_name": "KiteVentures Impact Fund",
                "sponsor_type": "venture_fund",
                "min_budget": 500000,
                "max_budget": 5000000,
                "currency": "INR",
            },
        )
        assert reg_spon.status_code == 201, f"Sponsor registration failed: {reg_spon.text}"
        spon_token = reg_spon.json()["access_token"]
        spon_headers = {"Authorization": f"Bearer {spon_token}"}

        # Fetch sponsor user id
        me_spon = await client.get(f"{BACKEND_URL}/auth/me", headers=spon_headers)
        assert me_spon.status_code == 200
        sponsor_user_id = me_spon.json()["id"]
        print(f"[PASS] 4. Sponsor registered successfully: {spon_email} (User ID: {sponsor_user_id})")

        # 4. Entrepreneur submits a monetary Sponsorship Request
        req_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=ent_headers,
            json={
                "project_id": project_id,
                "recipient_id": sponsor_user_id,
                "sponsorship_type": "Financial Funding",
                "requested_amount": 1250000.0,
                "currency": "INR",
                "message": "We would love KiteVentures to lead our initial flight testing tranche.",
            },
        )
        assert req_res.status_code == 201, f"Request creation failed: {req_res.text}"
        req_data = req_res.json()
        req_id = req_data["id"]
        assert req_data["status"] == "pending"
        assert req_data["currency"] == "INR"
        assert req_data["requested_amount"] == 1250000.0
        print(f"[PASS] 5. Monetary sponsorship request submitted (ID #{req_id}, ₹12,50,000)")

        # 5. Duplicate request prevention check
        dup_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=ent_headers,
            json={
                "project_id": project_id,
                "recipient_id": sponsor_user_id,
                "sponsorship_type": "Financial Funding",
                "requested_amount": 1000000.0,
                "message": "Duplicate attempt should be rejected.",
            },
        )
        assert dup_res.status_code == 400, "Duplicate request was not rejected"
        print("[PASS] 6. Duplicate pending request safely prevented with 400 Bad Request")

        # 6. Sponsor lists incoming requests
        spon_reqs = await client.get(f"{BACKEND_URL}/sponsorship-requests/", headers=spon_headers)
        assert spon_reqs.status_code == 200
        assert any(r["id"] == req_id for r in spon_reqs.json())
        print("[PASS] 7. Sponsor successfully retrieved incoming request queue")

        # 7. Sponsor ACCEPTS the request
        # User Correction #2: must initialize commitment in INTERESTED status
        accept_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/{req_id}/respond",
            headers=spon_headers,
            json={
                "action": "accept",
                "response_note": "Impressive aerodynamics telemetry. Accepted for mutual discussion.",
                "commitment_amount": 1250000.0,
            },
        )
        assert accept_res.status_code == 200, f"Accept failed: {accept_res.text}"
        accepted_req = accept_res.json()
        assert accepted_req["status"] == "accepted"
        commitment_id = accepted_req["commitment_id"]
        assert commitment_id is not None, "Commitment ID not linked to accepted request"
        print(f"[PASS] 8. Sponsor accepted request, spawning Commitment #{commitment_id}")

        # 8. Verify initial commitment status is INTERESTED
        comm_res = await client.get(f"{BACKEND_URL}/commitments/{commitment_id}", headers=spon_headers)
        assert comm_res.status_code == 200
        comm_data = comm_res.json()
        assert comm_data["status"] == "interested", f"Expected 'interested', got {comm_data['status']}"
        assert comm_data["amount"] == 1250000.0
        assert comm_data["currency"] == "INR"
        assert len(comm_data["updates"]) >= 1
        print("[PASS] 9. Commitment verified in INTERESTED status with INR (₹) allocation")

        # 9. Progress through Controlled Status Lifecycle:
        # INTERESTED -> DISCUSSION
        step1 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=spon_headers,
            json={
                "new_status": "discussion",
                "note": "Initial technical scoping and flight safety parameters agreed.",
            },
        )
        assert step1.status_code == 200 and step1.json()["status"] == "discussion"
        print("[PASS] 10. Status advanced: INTERESTED → DISCUSSION")

        # DISCUSSION -> PROMISED (Sponsor only)
        step2 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=spon_headers,
            json={
                "new_status": "promised",
                "note": "Sponsor pledged formal term sheet for ₹12,50,000.",
            },
        )
        assert step2.status_code == 200 and step2.json()["status"] == "promised"
        print("[PASS] 11. Status advanced: DISCUSSION → PROMISED")

        # PROMISED -> CONFIRMED
        step3 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=ent_headers,
            json={
                "new_status": "confirmed",
                "note": "Founder and Board confirmed terms.",
            },
        )
        assert step3.status_code == 200 and step3.json()["status"] == "confirmed"
        print("[PASS] 12. Status advanced: PROMISED → CONFIRMED")

        # 10. Add Progress Milestone Update (without changing status)
        m_res = await client.post(
            f"{BACKEND_URL}/commitments/{commitment_id}/updates",
            headers=ent_headers,
            json={
                "title": "Aviation Directorate Airspace Clearance Filed",
                "note": "Flight corridor clearance document filed under dossier #DGCA-2026-88.",
                "update_type": "milestone",
                "evidence_reference": "https://vynk.io/evidence/dgca_filing.pdf",
            },
        )
        assert m_res.status_code == 201
        print("[PASS] 13. Progress milestone update recorded with audit evidence reference")

        # 11. CONFIRMED -> AGREEMENT
        future_follow_up = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
        step4 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=spon_headers,
            json={
                "new_status": "agreement",
                "note": "Formal Sponsorship & IP agreement executed.",
                "agreement_reference": "VYNK-AGR-KITE-2026",
                "follow_up_date": future_follow_up,
                "follow_up_reason": "Verify bank escrow and transfer schedule",
            },
        )
        assert step4.status_code == 200 and step4.json()["status"] == "agreement"
        assert step4.json()["agreement_reference"] == "VYNK-AGR-KITE-2026"
        print("[PASS] 14. Status advanced: CONFIRMED → AGREEMENT (with contract reference & follow-up date)")

        # 12. AGREEMENT -> FUNDED (Sponsor only)
        step5 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=spon_headers,
            json={
                "new_status": "funded",
                "note": "Initial tranche ₹12,50,000 wired via NEFT/RTGS UTR# KITE9981245.",
            },
        )
        assert step5.status_code == 200 and step5.json()["status"] == "funded"
        print("[PASS] 15. Status advanced: AGREEMENT → FUNDED")

        # 13. FUNDED -> COMPLETED
        step6 = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=ent_headers,
            json={
                "new_status": "completed",
                "note": "Disbursed funds received and deployment milestone validated.",
            },
        )
        assert step6.status_code == 200 and step6.json()["status"] == "completed"
        print("[PASS] 16. Status advanced: FUNDED → COMPLETED (Lifecycle complete)")

        # 14. Terminal state immutability check
        terminal_res = await client.patch(
            f"{BACKEND_URL}/commitments/{commitment_id}/status",
            headers=spon_headers,
            json={"new_status": "discussion", "note": "Illegal restart attempt."},
        )
        assert terminal_res.status_code == 400
        print("[PASS] 17. Immutability enforced: cannot transition out of COMPLETED terminal state")

        # 15. Non-monetary commitment test
        nm_res = await client.post(
            f"{BACKEND_URL}/commitments/",
            headers=spon_headers,
            json={
                "project_id": project_id,
                "title": "Aerodynamic Wind Tunnel Access",
                "amount": 0.0,
                "currency": "INR",
                "sponsorship_type": "Testing / Facilities",
                "status": "interested",
                "notes": "20 hours of subsonic wind tunnel testing access at Bangalore campus.",
            },
        )
        assert nm_res.status_code == 201
        nm_data = nm_res.json()
        assert nm_data["amount"] == 0.0
        assert nm_data["sponsorship_type"] == "Testing / Facilities"
        print("[PASS] 18. Non-monetary commitment successfully created and logged")

        # 16. Cancellation test from intermediate state
        cancel_res = await client.patch(
            f"{BACKEND_URL}/commitments/{nm_data['id']}/status",
            headers=ent_headers,
            json={"new_status": "cancelled", "note": "Elected to use on-site CFD cluster instead."},
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "cancelled"
        print("[PASS] 19. Cancellation from pre-completed state safely executed with audit note")

        # 17. Check updates audit log
        updates_res = await client.get(f"{BACKEND_URL}/commitments/{commitment_id}/updates", headers=spon_headers)
        assert updates_res.status_code == 200
        assert len(updates_res.json()) >= 7
        print(f"[PASS] 20. Commitment audit log verified ({len(updates_res.json())} history events)")

        # 18. Check follow-ups query
        follow_res = await client.get(f"{BACKEND_URL}/commitments/follow-ups", headers=spon_headers)
        assert follow_res.status_code == 200
        print("[PASS] 21. Follow-ups schedule endpoint verified (200 OK)")

    print("\n🎉 ALL PHASE 6 LIVE VERIFICATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(main())
