import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_authorization_guards(client: AsyncClient):
    # 1. Unauthenticated request to admin dashboard -> 401
    unauth_res = await client.get("/api/v1/admin/dashboard")
    assert unauth_res.status_code == 401

    # 2. Register normal entrepreneur -> 403
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "normal.founder@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Normal Founder",
        "role": "entrepreneur",
    })
    assert ent_res.status_code == 201
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}

    ent_admin_res = await client.get("/api/v1/admin/dashboard", headers=ent_headers)
    assert ent_admin_res.status_code == 403

    # 3. Register normal sponsor -> 403
    spo_res = await client.post("/api/v1/auth/register", json={
        "email": "normal.sponsor@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Normal Sponsor",
        "role": "sponsor",
    })
    assert spo_res.status_code == 201
    spo_token = spo_res.json()["access_token"]
    spo_headers = {"Authorization": f"Bearer {spo_token}"}

    spo_admin_res = await client.get("/api/v1/admin/dashboard", headers=spo_headers)
    assert spo_admin_res.status_code == 403

    # 4. Register admin user -> 200
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "super.admin@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Super Admin",
        "role": "admin",
    })
    assert admin_res.status_code == 201
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    admin_dash_res = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert admin_dash_res.status_code == 200
    dash_data = admin_dash_res.json()
    assert "users" in dash_data
    assert "projects" in dash_data
    assert "sponsorship" in dash_data
    assert "platform" in dash_data


@pytest.mark.asyncio
async def test_admin_user_management_and_suspension(client: AsyncClient):
    # Register Admin
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "admin.mgr@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Admin Manager",
        "role": "admin",
    })
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Register Target User (Entrepreneur)
    target_res = await client.post("/api/v1/auth/register", json={
        "email": "target.user@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Target Founder",
        "role": "entrepreneur",
    })
    target_user_id = target_res.json()["user_id"]
    target_token = target_res.json()["access_token"]
    target_headers = {"Authorization": f"Bearer {target_token}"}

    # 1. Admin lists users
    list_res = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 2

    # 2. Admin inspects user detail
    detail_res = await client.get(f"/api/v1/admin/users/{target_user_id}", headers=admin_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["is_verified"] is False
    assert detail_res.json()["is_suspended"] is False

    # 3. Admin verifies user
    verify_res = await client.post(
        f"/api/v1/admin/users/{target_user_id}/verify",
        json={"verification_type": "identity", "notes": "Passport verified"},
        headers=admin_headers,
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["is_verified"] is True
    assert verify_res.json()["trust_score"] == 65

    # 4. Target user received notification
    notif_res = await client.get("/api/v1/notifications", headers=target_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()["items"]
    assert any("Profile Verified" in n["title"] for n in notifs)

    # 5. Admin revokes verification
    revoke_res = await client.post(
        f"/api/v1/admin/users/{target_user_id}/revoke-verification",
        json={"notes": "Document expired"},
        headers=admin_headers,
    )
    assert revoke_res.status_code == 200
    assert revoke_res.json()["is_verified"] is False
    assert revoke_res.json()["trust_score"] == 50

    # 6. Admin suspends target user
    suspend_res = await client.post(
        f"/api/v1/admin/users/{target_user_id}/suspend",
        json={"reason": "Terms of Service violation - suspicious spam."},
        headers=admin_headers,
    )
    assert suspend_res.status_code == 200
    assert suspend_res.json()["is_suspended"] is True

    # 7. Suspended user cannot perform authenticated actions
    blocked_res = await client.get("/api/v1/auth/me", headers=target_headers)
    assert blocked_res.status_code == 403
    assert "suspended" in blocked_res.json()["detail"].lower()

    # 8. Non-admin cannot unsuspend user
    bystander_res = await client.post("/api/v1/auth/register", json={
        "email": "bystander@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Bystander",
        "role": "entrepreneur",
    })
    bystander_token = bystander_res.json()["access_token"]
    bystander_headers = {"Authorization": f"Bearer {bystander_token}"}

    unauth_unsuspend = await client.post(f"/api/v1/admin/users/{target_user_id}/unsuspend", headers=bystander_headers)
    assert unauth_unsuspend.status_code == 403

    # 9. Admin unsuspends user
    unsuspend_res = await client.post(f"/api/v1/admin/users/{target_user_id}/unsuspend", headers=admin_headers)
    assert unsuspend_res.status_code == 200
    assert unsuspend_res.json()["is_suspended"] is False

    # 10. User restored and can perform authenticated actions again
    restored_res = await client.get("/api/v1/auth/me", headers=target_headers)
    assert restored_res.status_code == 200


@pytest.mark.asyncio
async def test_project_moderation_workflow(client: AsyncClient):
    # Register Admin
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "mod.admin@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Moderation Admin",
        "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # Register Entrepreneur & Publish Project
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "project.mod.founder@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Venture Founder",
        "role": "entrepreneur",
    })
    ent_headers = {"Authorization": f"Bearer {ent_res.json()['access_token']}"}

    proj_res = await client.post("/api/v1/projects/", json={
        "title": "Quantum Sensor Shield",
        "tagline": "Next generation quantum sensors for navigation",
        "description": "Comprehensive quantum navigation system eliminating GPS dependencies for industrial systems.",
        "category": "DeepTech",
        "stage": "prototype",
        "funding_goal": 3500000.0,
        "currency": "INR",
        "required_support": ["Capital", "Mentorship"],
        "status": "draft",
    }, headers=ent_headers)
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 1. Admin lists projects
    p_list = await client.get("/api/v1/admin/projects", headers=admin_headers)
    assert p_list.status_code == 200
    assert any(p["id"] == proj_id for p in p_list.json()["items"])

    # 2. Admin rejects project (request changes)
    reject_res = await client.post(
        f"/api/v1/admin/projects/{proj_id}/reject",
        json={"moderation_status": "rejected", "reason": "Please provide more technical documentation on sensor accuracy."},
        headers=admin_headers,
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["moderation_status"] == "rejected"

    # Entrepreneur receives notification
    ent_notifs = await client.get("/api/v1/notifications", headers=ent_headers)
    assert any("Project Moderation Update" in n["title"] for n in ent_notifs.json()["items"])

    # 3. Admin approves project
    approve_res = await client.post(
        f"/api/v1/admin/projects/{proj_id}/approve",
        json={"moderation_status": "approved", "reason": "Revised specs look excellent."},
        headers=admin_headers,
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["moderation_status"] == "approved"


@pytest.mark.asyncio
async def test_reporting_and_dispute_workflows(client: AsyncClient):
    # Setup users
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "arb.admin@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Arbitration Admin",
        "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    u1_res = await client.post("/api/v1/auth/register", json={
        "email": "reporter.user@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Reporter User",
        "role": "entrepreneur",
    })
    u1_id = u1_res.json()["user_id"]
    u1_headers = {"Authorization": f"Bearer {u1_res.json()['access_token']}"}

    u2_res = await client.post("/api/v1/auth/register", json={
        "email": "reported.sponsor@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Reported Sponsor",
        "role": "sponsor",
    })
    u2_id = u2_res.json()["user_id"]

    # 1. User submits report against reported sponsor
    rep_res = await client.post("/api/v1/reports", json={
        "reported_user_id": u2_id,
        "category": "misrepresentation",
        "reason": "Claimed accreditation without proof",
        "details": "User stated they manage a $10M fund but has no registered entity.",
    }, headers=u1_headers)
    assert rep_res.status_code == 201
    report_id = rep_res.json()["id"]

    # 2. Self-report blocked
    self_rep = await client.post("/api/v1/reports", json={
        "reported_user_id": u1_id,
        "category": "spam",
        "reason": "Reporting myself",
    }, headers=u1_headers)
    assert self_rep.status_code == 400

    # 3. Admin lists and reviews report
    rep_list = await client.get("/api/v1/admin/reports", headers=admin_headers)
    assert rep_list.status_code == 200
    assert any(r["id"] == report_id for r in rep_list.json()["items"])

    review_res = await client.post(f"/api/v1/admin/reports/{report_id}/review", headers=admin_headers)
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "under_review"

    # 4. Admin resolves report
    resolve_res = await client.post(
        f"/api/v1/admin/reports/{report_id}/resolve",
        json={"resolution_note": "Target sponsor requested to upload verified accreditation."},
        headers=admin_headers,
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"

    # Reporter notified
    r_notifs = await client.get("/api/v1/notifications", headers=u1_headers)
    assert any("Report Resolved" in n["title"] for n in r_notifs.json()["items"])


@pytest.mark.asyncio
async def test_admin_audit_logs_immutability(client: AsyncClient):
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "audit.inspector@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Audit Inspector",
        "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # Perform an audited action
    u_res = await client.post("/api/v1/auth/register", json={
        "email": "audit.target@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Audit Target",
        "role": "entrepreneur",
    })
    target_id = u_res.json()["user_id"]
    await client.post(f"/api/v1/admin/users/{target_id}/verify", headers=admin_headers)

    # Retrieve audit logs
    audit_res = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()["items"]
    assert len(logs) > 0

    # Verify audit fields
    sample = logs[0]
    assert "action" in sample
    assert "entity_type" in sample
    assert "description" in sample
    assert "created_at" in sample

    # Verify non-admin cannot access audit logs
    user_res = await client.post("/api/v1/auth/register", json={
        "email": "nonadmin.audit@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Non Admin",
        "role": "entrepreneur",
    })
    user_headers = {"Authorization": f"Bearer {user_res.json()['access_token']}"}

    forbidden_audit = await client.get("/api/v1/admin/audit-logs", headers=user_headers)
    assert forbidden_audit.status_code == 403


@pytest.mark.asyncio
async def test_dispute_workflow_and_authorization(client: AsyncClient):
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "dispute.judge@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Dispute Judge",
        "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "dispute.founder@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Dispute Founder",
        "role": "entrepreneur",
    })
    ent_headers = {"Authorization": f"Bearer {ent_res.json()['access_token']}"}

    spo_res = await client.post("/api/v1/auth/register", json={
        "email": "dispute.sponsor@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Dispute Sponsor",
        "role": "sponsor",
    })
    spo_headers = {"Authorization": f"Bearer {spo_res.json()['access_token']}"}
    spo_user_id = spo_res.json()["user_id"]

    # Entrepreneur creates project & submits sponsorship request
    p_res = await client.post("/api/v1/projects/", json={
        "title": "BioDispute Array",
        "tagline": "Solar bio cells",
        "description": "Solar bio cells showcase",
        "category": "CleanTech",
        "stage": "idea",
        "status": "draft",
    }, headers=ent_headers)
    p_id = p_res.json()["id"]

    req_res = await client.post("/api/v1/sponsorship-requests/", json={
        "recipient_id": spo_user_id,
        "project_id": p_id,
        "message": "Interested in partnering",
        "requested_amount": 100000.0,
        "currency": "INR",
        "sponsorship_type": "financial",
    }, headers=ent_headers)
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # 1. Unrelated user attempts to dispute request -> 403
    unrelated_res = await client.post("/api/v1/auth/register", json={
        "email": "unrelated@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Unrelated",
        "role": "entrepreneur",
    })
    unrelated_headers = {"Authorization": f"Bearer {unrelated_res.json()['access_token']}"}

    unauth_disp = await client.post("/api/v1/disputes", json={
        "request_id": req_id,
        "reason": "commitment_disagreement",
        "description": "I want to dispute this third-party request",
    }, headers=unrelated_headers)
    assert unauth_disp.status_code == 403

    # 2. Legitimate participant initiates dispute
    disp_res = await client.post("/api/v1/disputes", json={
        "request_id": req_id,
        "reason": "commitment_disagreement",
        "description": "Counterparty failed to respond to agreed sponsorship terms.",
    }, headers=ent_headers)
    assert disp_res.status_code == 201
    disp_id = disp_res.json()["id"]

    # 3. Admin reviews and resolves dispute
    review_res = await client.post(f"/api/v1/admin/disputes/{disp_id}/review", headers=admin_headers)
    assert review_res.status_code == 200

    resolve_res = await client.post(f"/api/v1/admin/disputes/{disp_id}/resolve", json={
        "resolution": "Parties agreed to cancel pending request without penalty.",
    }, headers=admin_headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_trust_score_and_compatibility_protection(client: AsyncClient):
    admin_res = await client.post("/api/v1/auth/register", json={
        "email": "trust.guard.admin@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Trust Guard Admin",
        "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "trust.test.founder@vynk.io",
        "password": "StrongPassword123!",
        "full_name": "Trust Test Founder",
        "role": "entrepreneur",
    })
    ent_user_id = ent_res.json()["user_id"]
    ent_headers = {"Authorization": f"Bearer {ent_res.json()['access_token']}"}

    # Verify no direct Trust Score assignment endpoint exists (404/405)
    direct_score_res = await client.post(f"/api/v1/admin/users/{ent_user_id}/trust-score", json={"score": 99}, headers=admin_headers)
    assert direct_score_res.status_code in (404, 405)

    # Initial trust score is baseline 50
    me_trust = await client.get("/api/v1/trust/me", headers=ent_headers)
    assert me_trust.status_code == 200
    assert me_trust.json()["score"] == 50

    # Verification naturally yields 65 (50 + 15 verification points)
    v_res = await client.post(f"/api/v1/admin/users/{ent_user_id}/verify", headers=admin_headers)
    assert v_res.status_code == 200
    assert v_res.json()["trust_score"] == 65

    # Deterministic recalculation yields the exact same 65
    recalc = await client.post("/api/v1/trust/recalculate", headers=ent_headers)
    assert recalc.status_code == 200
    assert recalc.json()["score"] == 65
