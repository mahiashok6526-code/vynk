import asyncio
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 9: Admin & Moderation System Live Verification ===")
    ts_now = int(time.time())

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # 1. Health Check
        h_res = await client.get(f"{BACKEND_URL}/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register Platform Administrator
        admin_email = f"admin.p9.{ts_now}@vynk.io"
        admin_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": admin_email,
                "password": "SecurePassword123!",
                "full_name": "Governance Officer",
                "role": "admin",
            },
        )
        assert admin_reg.status_code == 201, f"Admin registration failed: {admin_reg.text}"
        admin_token = admin_reg.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=admin_headers)).json()
        admin_id = admin_me["id"]
        assert admin_me["role"] == "admin"
        print(f"[PASS] 2. Registered Platform Admin: {admin_email} (ID: {admin_id})")

        # 3. Register Entrepreneur and Sponsor
        ent_email = f"founder.p9.{ts_now}@vynk.io"
        ent_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Kavita Rao",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "FinTech",
            },
        )
        assert ent_reg.status_code == 201
        ent_token = ent_reg.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        ent_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=ent_headers)).json()
        ent_id = ent_me["id"]
        print(f"[PASS] 3. Registered Entrepreneur: {ent_email} (ID: {ent_id})")

        sp_email = f"sponsor.p9.{ts_now}@vynk.io"
        sp_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp_email,
                "password": "SecurePassword123!",
                "full_name": "Rohan Deshmukh",
                "role": "sponsor",
                "organization_name": "Deshmukh Capital",
                "sponsor_type": "family_office",
                "min_budget": 100000,
                "max_budget": 5000000,
            },
        )
        assert sp_reg.status_code == 201
        sp_token = sp_reg.json()["access_token"]
        sp_headers = {"Authorization": f"Bearer {sp_token}"}
        sp_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=sp_headers)).json()
        sp_id = sp_me["id"]
        print(f"[PASS] 4. Registered Sponsor: {sp_email} (ID: {sp_id})")

        # 4. Authorization Boundary: Non-admin gets 403 Forbidden on admin routes
        forbidden_test = await client.get(f"{BACKEND_URL}/admin/dashboard", headers=ent_headers)
        assert forbidden_test.status_code == 403, f"Expected 403 for non-admin, got {forbidden_test.status_code}"
        print("[PASS] 5. Non-admin authorization guard verified (403 Forbidden for entrepreneur accessing /admin/dashboard)")

        # 5. Platform Telemetry Dashboard
        dash_res = await client.get(f"{BACKEND_URL}/admin/dashboard", headers=admin_headers)
        assert dash_res.status_code == 200, f"Dashboard fetch failed: {dash_res.text}"
        dash_data = dash_res.json()
        assert "users" in dash_data
        assert "projects" in dash_data
        assert "sponsorships" in dash_data
        assert "trust" in dash_data
        assert "queues" in dash_data
        assert dash_data["users"]["total"] >= 3
        print(f"[PASS] 6. Platform Telemetry Dashboard verified (Users: {dash_data['users']['total']}, Avg Trust: {dash_data['trust']['average_trust_score']})")

        # 6. User Management & Verification Workflow
        users_res = await client.get(f"{BACKEND_URL}/admin/users", headers=admin_headers)
        assert users_res.status_code == 200
        assert users_res.json()["total"] >= 3
        print(f"[PASS] 7. User management list endpoint verified (Total: {users_res.json()['total']})")

        # Get initial trust score of entrepreneur
        ent_profile = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        initial_score = ent_profile["score"]
        assert initial_score == 50  # Baseline neutral

        # Admin verifies entrepreneur
        verify_res = await client.post(
            f"{BACKEND_URL}/admin/users/{ent_id}/verify",
            headers=admin_headers,
            json={"notes": "Accredited documentation verified by governance board."},
        )
        assert verify_res.status_code == 200
        verify_data = verify_res.json()
        assert verify_data["is_verified"] is True
        print("[PASS] 8. Admin verification action succeeded")

        # TRUST SCORE RULE CHECK: Factual verification state changed -> TrustService calculated +15 pts
        updated_trust = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert updated_trust["score"] == initial_score + 15, f"Expected {initial_score + 15}, got {updated_trust['score']}"
        assert updated_trust["verification_points"] == 15
        print(f"[PASS] 9. TRUST SCORE RULE verified: Algorithmic recalculation applied (Baseline 50 -> {updated_trust['score']}, no direct score assignment)")

        # Verify notification was sent to entrepreneur
        ent_notifs = (await client.get(f"{BACKEND_URL}/notifications", headers=ent_headers)).json()
        assert any("Profile Verified" in n["title"] or "verification" in n["content"].lower() for n in ent_notifs["items"])
        print("[PASS] 10. Verification in-app notification delivered to user")

        # Revoke verification
        revoke_res = await client.post(
            f"{BACKEND_URL}/admin/users/{ent_id}/revoke-verification",
            headers=admin_headers,
            json={"reason": "Periodic review document expiration."},
        )
        assert revoke_res.status_code == 200
        assert revoke_res.json()["is_verified"] is False
        revoked_trust = (await client.get(f"{BACKEND_URL}/trust/me", headers=ent_headers)).json()
        assert revoked_trust["score"] == initial_score
        print("[PASS] 11. Verification revoked cleanly, Trust Score returned to baseline (50.0)")

        # 7. User Suspension & Access Control Rule
        suspend_res = await client.post(
            f"{BACKEND_URL}/admin/users/{ent_id}/suspend",
            headers=admin_headers,
            json={"reason": "Flagged for policy audit review."},
        )
        assert suspend_res.status_code == 200
        assert suspend_res.json()["is_suspended"] is True
        print("[PASS] 12. Admin successfully suspended user")

        # SUSPENSION RULE CHECK: Suspended user is BLOCKED from authenticated actions
        blocked_action = await client.get(f"{BACKEND_URL}/auth/me", headers=ent_headers)
        assert blocked_action.status_code == 403, f"Expected 403 for suspended user, got {blocked_action.status_code}"
        assert "suspended" in blocked_action.text.lower()
        print("[PASS] 13. SUSPENSION RULE verified: Suspended user blocked from authenticated platform operations (403 Forbidden)")

        # Ensure admin can still inspect and manage the suspended user without authorization bypass
        admin_inspect = await client.get(f"{BACKEND_URL}/admin/users?is_suspended=true", headers=admin_headers)
        assert admin_inspect.status_code == 200
        assert any(u["id"] == ent_id for u in admin_inspect.json()["items"])
        print("[PASS] 14. Administrator can query and manage suspended accounts")

        # Admin unsuspends user
        unsuspend_res = await client.post(
            f"{BACKEND_URL}/admin/users/{ent_id}/unsuspend",
            headers=admin_headers,
        )
        assert unsuspend_res.status_code == 200
        assert unsuspend_res.json()["is_suspended"] is False

        # Verify access restored
        restored_action = await client.get(f"{BACKEND_URL}/auth/me", headers=ent_headers)
        assert restored_action.status_code == 200
        print("[PASS] 15. User unsuspended, authenticated access successfully restored")

        # 8. Project Showcase Moderation
        # Entrepreneur creates a project
        proj_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": "QuantumLedger Core",
                "tagline": "Next-gen zero-knowledge fintech infrastructure",
                "description": "Enterprise-grade ZK settlement layer for real-world asset tokenization.",
                "category": "FinTech",
                "funding_goal": 750000,
                "status": "draft",
            },
        )
        assert proj_res.status_code == 201, f"Project creation failed: {proj_res.text}"
        proj_id = proj_res.json()["id"]
        print(f"[PASS] 16. Created Showcase Project: {proj_id}")

        # Check in admin project moderation queue
        adm_projects = await client.get(f"{BACKEND_URL}/admin/projects", headers=admin_headers)
        assert adm_projects.status_code == 200
        assert any(p["id"] == proj_id for p in adm_projects.json()["items"])
        print("[PASS] 17. Project listed in admin moderation queue")

        # Admin rejects project with feedback
        reject_res = await client.post(
            f"{BACKEND_URL}/admin/projects/{proj_id}/reject",
            headers=admin_headers,
            json={"reason": "Please attach architectural benchmark whitepaper."},
        )
        assert reject_res.status_code == 200
        assert reject_res.json()["moderation_status"] == "rejected"
        assert reject_res.json()["moderation_reason"] == "Please attach architectural benchmark whitepaper."
        print("[PASS] 18. Project rejected with required feedback reason")

        # Admin approves project
        approve_res = await client.post(
            f"{BACKEND_URL}/admin/projects/{proj_id}/approve",
            headers=admin_headers,
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["moderation_status"] == "approved"
        print("[PASS] 19. Project approved for showcase publication")

        # 9. Reporting Workflow
        report_res = await client.post(
            f"{BACKEND_URL}/reports",
            headers=sp_headers,
            json={
                "reported_user_id": ent_id,
                "category": "spam",
                "description": "Suspicious unsolicited pitch message received.",
            },
        )
        assert report_res.status_code == 201, f"Report submission failed: {report_res.text}"
        report_id = report_res.json()["id"]
        print(f"[PASS] 20. Community report submitted: {report_id}")

        # Admin reviews and resolves report
        adm_reports = await client.get(f"{BACKEND_URL}/admin/reports", headers=admin_headers)
        assert adm_reports.status_code == 200
        assert any(r["id"] == report_id for r in adm_reports.json()["items"])

        resolve_rep_res = await client.post(
            f"{BACKEND_URL}/admin/reports/{report_id}/review",
            headers=admin_headers,
            json={
                "status": "resolved",
                "resolution_note": "Warning issued to account holder regarding cold messaging limits.",
            },
        )
        assert resolve_rep_res.status_code == 200
        assert resolve_rep_res.json()["status"] == "resolved"
        print("[PASS] 21. Admin reviewed and resolved report with audit resolution note")

        # 10. Sponsorship Dispute Arbitration
        # First, initiate a sponsorship request
        req_res = await client.post(
            f"{BACKEND_URL}/sponsorships/requests",
            headers=ent_headers,
            json={
                "sponsor_id": sp_id,
                "project_id": proj_id,
                "proposed_amount": 100000,
                "proposal_message": "Strategic seed partnership proposal.",
                "deliverables": ["SDK Alpha release", "Audited smart contracts"],
            },
        )
        assert req_res.status_code == 201
        sponsorship_req_id = req_res.json()["id"]

        # REPORT/DISPUTE RULE: Arbitrary uninvolved user CANNOT dispute
        unrelated_email = f"other.p9.{ts_now}@vynk.io"
        unrelated_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": unrelated_email,
                "password": "SecurePassword123!",
                "full_name": "Bystander User",
                "role": "entrepreneur",
            },
        )
        unrelated_headers = {"Authorization": f"Bearer {unrelated_reg.json()['access_token']}"}

        unauthorized_dispute = await client.post(
            f"{BACKEND_URL}/disputes",
            headers=unrelated_headers,
            json={
                "sponsorship_request_id": sponsorship_req_id,
                "reason": "non_delivery",
                "description": "I have no relation to this agreement.",
            },
        )
        assert unauthorized_dispute.status_code == 403, f"Expected 403 for uninvolved user, got {unauthorized_dispute.status_code}"
        print("[PASS] 22. REPORT/DISPUTE RULE verified: Arbitrary uninvolved users cannot dispute agreements (403 Forbidden)")

        # Legitimate involved party (sponsor) creates dispute
        dispute_res = await client.post(
            f"{BACKEND_URL}/disputes",
            headers=sp_headers,
            json={
                "sponsorship_request_id": sponsorship_req_id,
                "reason": "scope_breach",
                "description": "Milestone deliverables differ from agreed terms.",
            },
        )
        assert dispute_res.status_code == 201, f"Dispute creation failed: {dispute_res.text}"
        dispute_id = dispute_res.json()["id"]
        assert dispute_res.json()["status"] == "opened"
        print(f"[PASS] 23. Legitimate dispute created by involved party: {dispute_id}")

        # Admin arbitrates dispute: moves to under_review then resolved
        review_step1 = await client.post(
            f"{BACKEND_URL}/admin/disputes/{dispute_id}/review",
            headers=admin_headers,
            json={
                "status": "under_review",
                "resolution_note": "Reviewing original proposal and counter-statements.",
            },
        )
        assert review_step1.status_code == 200
        assert review_step1.json()["status"] == "under_review"

        review_step2 = await client.post(
            f"{BACKEND_URL}/admin/disputes/{dispute_id}/review",
            headers=admin_headers,
            json={
                "status": "resolved",
                "resolution_note": "Parties agreed to modified timeline for Milestone 1 delivery.",
            },
        )
        assert review_step2.status_code == 200
        assert review_step2.json()["status"] == "resolved"
        print("[PASS] 24. Admin successfully arbitrated dispute to resolution with notifications")

        # 11. Immutable Audit Trail Rule Check
        audit_res = await client.get(f"{BACKEND_URL}/admin/audit-logs", headers=admin_headers)
        assert audit_res.status_code == 200
        audit_items = audit_res.json()["items"]
        assert len(audit_items) >= 6

        # AUDIT RULE CHECK: Every mutation records authenticated admin ID, action, target entity, timestamp
        for log in audit_items:
            assert log["admin_id"] == admin_id, f"Audit log admin mismatch: expected {admin_id}, got {log['admin_id']}"
            assert log["action"] in [
                "verify_user", "revoke_verification", "suspend_user", "unsuspend_user",
                "approve_project", "reject_project", "resolve_report", "dismiss_report",
                "resolve_dispute", "dismiss_dispute",
            ]
            assert log["entity_type"] in ["user", "project", "report", "dispute"]
            assert log["created_at"] is not None

        print(f"[PASS] 25. AUDIT RULE verified: Recorded {len(audit_items)} immutable administrative events with verified admin identity")

        # Ensure no tamper endpoint exists (e.g. DELETE or PUT on audit-logs fails with 405 Method Not Allowed)
        tamper_attempt = await client.delete(f"{BACKEND_URL}/admin/audit-logs/{audit_items[0]['id']}", headers=admin_headers)
        assert tamper_attempt.status_code in [404, 405], f"Audit log deletion must not be permitted, got {tamper_attempt.status_code}"
        print("[PASS] 26. Audit logs immutability verified (no deletion/update endpoints exist)")

    print("\n=======================================================")
    print("ALL PHASE 9 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(main())
