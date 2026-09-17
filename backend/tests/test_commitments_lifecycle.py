from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_commitment_lifecycle_state_machine_and_milestones(client: AsyncClient):
    # 1. Register Entrepreneur
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "aarav.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Aarav Mehta",
        "role": "entrepreneur",
        "stage": "mvp",
        "industry": "HealthTech",
    })
    assert ent_res.status_code == 201
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}

    # Register Third-Party Entrepreneur
    other_res = await client.post("/api/v1/auth/register", json={
        "email": "unauthorized.ent@vynk.io",
        "password": "Password123!",
        "full_name": "Unauthorized User",
        "role": "entrepreneur",
        "stage": "idea",
        "industry": "EdTech",
    })
    assert other_res.status_code == 201
    other_headers = {"Authorization": f"Bearer {other_res.json()['access_token']}"}

    # 2. Register Sponsor
    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "deepa.sponsor@vynk.io",
        "password": "SponsorPassword123!",
        "full_name": "Deepa Singhania",
        "role": "sponsor",
        "organization_name": "Healthcare Horizons Angel Fund",
        "sponsor_type": "angel_syndicate",
        "min_budget": 200000,
        "max_budget": 1500000,
    })
    assert spon_res.status_code == 201
    spon_token = spon_res.json()["access_token"]
    spon_headers = {"Authorization": f"Bearer {spon_token}"}

    # 3. Create Project
    proj_res = await client.post(
        "/api/v1/projects/",
        headers=ent_headers,
        json={
            "title": "OncoScan Portable Diagnostics",
            "tagline": "AI-guided point-of-care ultrasound screening",
            "description": "Ultra-low-cost handheld imaging wand paired with cloud diagnostic screening.",
            "category": "HealthTech",
            "stage": "mvp",
            "funding_goal": 3000000.0,
            "currency": "INR",
        }
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 4. Sponsor creates Commitment with follow-up date in the past to test overdue flag
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    comm_res = await client.post(
        "/api/v1/commitments/",
        headers=spon_headers,
        json={
            "project_id": project_id,
            "title": "Clinical Trials Tranche",
            "amount": 750000.0,
            "currency": "INR",
            "sponsorship_type": "Financial Funding",
            "status": "interested",
            "follow_up_date": past_date,
            "follow_up_reason": "Follow up with founder on IRB trial protocols",
            "notes": "Interested in backing multi-center validation study.",
        }
    )
    assert comm_res.status_code == 201
    comm = comm_res.json()
    comm_id = comm["id"]
    assert comm["status"] == "interested"
    assert comm["currency"] == "INR"
    assert comm["is_overdue"] is True
    assert comm["follow_up_reason"] == "Follow up with founder on IRB trial protocols"

    # 5. Verify security: unauthorized third party cannot view commitment details
    unauth_res = await client.get(f"/api/v1/commitments/{comm_id}", headers=other_headers)
    assert unauth_res.status_code == 404

    # 6. Test invalid transition: cannot skip stages (INTERESTED -> FUNDED)
    invalid_skip = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=spon_headers,
        json={"new_status": "funded", "note": "Illegal leap"}
    )
    assert invalid_skip.status_code == 400
    assert "Invalid transition" in invalid_skip.json()["detail"]

    # 7. Progress: INTERESTED -> DISCUSSION (Allowed for Entrepreneur or Sponsor)
    step1 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=ent_headers,
        json={"new_status": "discussion", "note": "Introductory sync call held."}
    )
    assert step1.status_code == 200
    assert step1.json()["status"] == "discussion"

    # 8. Test Role Guard: Entrepreneur CANNOT move DISCUSSION -> PROMISED (only Sponsor can promise terms)
    unauthorized_promise = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=ent_headers,
        json={"new_status": "promised", "note": "Founder trying to promise self."}
    )
    assert unauthorized_promise.status_code == 403
    assert "sponsor" in unauthorized_promise.json()["detail"].lower()

    # 9. Sponsor marks DISCUSSION -> PROMISED
    step2 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=spon_headers,
        json={"new_status": "promised", "note": "Term sheet offered for ₹7,50,000."}
    )
    assert step2.status_code == 200
    assert step2.json()["status"] == "promised"

    # 10. Progress: PROMISED -> CONFIRMED
    step3 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=ent_headers,
        json={"new_status": "confirmed", "note": "Term sheet countersigned by board."}
    )
    assert step3.status_code == 200
    assert step3.json()["status"] == "confirmed"

    # 11. Add Progress Milestone Update (without changing status)
    future_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    milestone_res = await client.post(
        f"/api/v1/commitments/{comm_id}/updates",
        headers=ent_headers,
        json={
            "title": "Hospital Ethics Committee Clearance Obtained",
            "note": "Ethics protocol ref #IRB-2026-992 signed off.",
            "update_type": "milestone",
            "evidence_reference": "https://vynk.io/docs/irb_approval.pdf",
        }
    )
    assert milestone_res.status_code == 201
    milestone = milestone_res.json()
    assert milestone["title"] == "Hospital Ethics Committee Clearance Obtained"
    assert milestone["update_type"] == "milestone"
    assert milestone["updater_name"] == "Aarav Mehta"

    # 12. Progress: CONFIRMED -> AGREEMENT
    step4 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=spon_headers,
        json={
            "new_status": "agreement",
            "note": "Formal Grant Agreement executed.",
            "agreement_reference": "VYNK-AGR-2026-0042",
            "follow_up_date": future_date,
            "follow_up_reason": "Verify bank escrow and transfer schedule",
        }
    )
    assert step4.status_code == 200
    assert step4.json()["status"] == "agreement"
    assert step4.json()["agreement_reference"] == "VYNK-AGR-2026-0042"
    assert step4.json()["is_overdue"] is False  # Future date is not overdue

    # 13. Progress: AGREEMENT -> FUNDED (Sponsor only)
    step5 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=spon_headers,
        json={
            "new_status": "funded",
            "note": "Wire transfer UTR# HDFC00998231 successfully processed for ₹7,50,000.",
        }
    )
    assert step5.status_code == 200
    assert step5.json()["status"] == "funded"

    # 14. Progress: FUNDED -> COMPLETED (Fulfills lifecycle)
    step6 = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=ent_headers,
        json={
            "new_status": "completed",
            "note": "Funds received in escrow account. Milestone verified and trial launched.",
        }
    )
    assert step6.status_code == 200
    assert step6.json()["status"] == "completed"

    # 15. Terminal State Check: Cannot transition out of COMPLETED
    terminal_res = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        headers=spon_headers,
        json={"new_status": "discussion", "note": "Trying to restart completed commitment."}
    )
    assert terminal_res.status_code == 400
    assert "Cannot transition commitment from terminal state" in terminal_res.json()["detail"]

    # 16. Test Updates timeline
    updates_res = await client.get(f"/api/v1/commitments/{comm_id}/updates", headers=spon_headers)
    assert updates_res.status_code == 200
    updates_list = updates_res.json()
    assert len(updates_list) >= 7  # Initial + 6 transitions + 1 custom milestone

    # 17. Non-Monetary Commitment Test (Mentorship / Credits)
    non_monetary_res = await client.post(
        "/api/v1/commitments/",
        headers=spon_headers,
        json={
            "project_id": project_id,
            "title": "Clinical Advisory & Mentorship",
            "amount": 0.0,
            "currency": "INR",
            "sponsorship_type": "Mentorship",
            "status": "interested",
            "notes": "10 hours of executive clinical advisory sessions.",
        }
    )
    assert non_monetary_res.status_code == 201
    nm_comm = non_monetary_res.json()
    assert nm_comm["amount"] == 0.0
    assert nm_comm["sponsorship_type"] == "Mentorship"

    # 18. Test Cancellation Flow from intermediate state
    cancel_step = await client.patch(
        f"/api/v1/commitments/{nm_comm['id']}/status",
        headers=ent_headers,
        json={"new_status": "cancelled", "note": "Founder elected alternative advisor."}
    )
    assert cancel_step.status_code == 200
    assert cancel_step.json()["status"] == "cancelled"

    # Cannot transition out of CANCELLED
    cancel_terminal = await client.patch(
        f"/api/v1/commitments/{nm_comm['id']}/status",
        headers=spon_headers,
        json={"new_status": "interested", "note": "Trying to revive cancelled commitment."}
    )
    assert cancel_terminal.status_code == 400
