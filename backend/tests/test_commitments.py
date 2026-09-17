import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_commitment_lifecycle(client: AsyncClient):
    # 1. Register Entrepreneur
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "elon.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Elon Founder",
        "role": "entrepreneur",
        "stage": "mvp",
        "industry": "Aerospace & AI",
    })
    assert ent_res.status_code == 201
    ent_token = ent_res.json()["access_token"]

    # 2. Entrepreneur creates Project
    proj_res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "HyperLink Autonomous Transit",
            "tagline": "Next generation sustainable high-speed regional logistics",
            "description": "Zero-emission pneumatic vacuum transport network connecting regional cargo hubs.",
            "category": "CleanTech",
            "stage": "mvp",
            "funding_goal": 250000.0,
            "requirements": [
                {
                    "requirement_type": "capital",
                    "title": "Initial prototype field trial",
                    "amount": 100000.0
                },
                {
                    "requirement_type": "mentorship",
                    "title": "Regulatory compliance guidance"
                }
            ]
        }
    )
    assert proj_res.status_code == 201
    project = proj_res.json()
    project_id = project["id"]
    assert project["title"] == "HyperLink Autonomous Transit"

    # 3. Register Sponsor
    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "warren.sponsor@vynk.io",
        "password": "SponsorPassword123!",
        "full_name": "Warren Sponsor",
        "role": "sponsor",
        "organization_name": "Green Frontier Capital",
        "sponsor_type": "venture_fund",
        "min_budget": 50000,
        "max_budget": 500000,
    })
    assert spon_res.status_code == 201
    spon_token = spon_res.json()["access_token"]

    # 4. Sponsor creates Commitment (Interested status)
    comm_res = await client.post(
        "/api/v1/commitments/",
        headers={"Authorization": f"Bearer {spon_token}"},
        json={
            "project_id": project_id,
            "amount": 75000.0,
            "sponsorship_type": "grant",
            "status": "interested",
            "notes": "Interested in evaluating autonomous sensor telemetry."
        }
    )
    assert comm_res.status_code == 201
    commitment = comm_res.json()
    commitment_id = commitment["id"]
    assert commitment["status"] == "interested"
    assert len(commitment["updates"]) == 1

    # 5. Progress commitment: Interested -> Discussion
    step1_res = await client.patch(
        f"/api/v1/commitments/{commitment_id}/status",
        headers={"Authorization": f"Bearer {spon_token}"},
        json={
            "new_status": "discussion",
            "note": "Initial technical evaluation call completed with founder."
        }
    )
    assert step1_res.status_code == 200
    assert step1_res.json()["status"] == "discussion"

    # 6. Progress commitment through lifecycle: Discussion -> Promised -> Confirmed -> Agreement -> Funded -> Completed
    for next_st, note_msg in [
        ("promised", "Sponsor promised term sheet."),
        ("confirmed", "Entrepreneur and sponsor confirmed terms."),
        ("agreement", "Formal agreement drafted and signed."),
        ("funded", "Disbursement tranche funded."),
        ("completed", "Tranche funds disbursed and verified on milestone delivery."),
    ]:
        step_res = await client.patch(
            f"/api/v1/commitments/{commitment_id}/status",
            headers={"Authorization": f"Bearer {spon_token}"},
            json={
                "new_status": next_st,
                "note": note_msg,
            }
        )
        assert step_res.status_code == 200, f"Failed transitioning to {next_st}: {step_res.text}"
        assert step_res.json()["status"] == next_st


    # 7. Verify Sponsor's Trust Score gained completed commitment point
    trust_res = await client.get(
        "/api/v1/trust/me",
        headers={"Authorization": f"Bearer {spon_token}"}
    )
    assert trust_res.status_code == 200
    trust_data = trust_res.json()
    assert trust_data["completed_commitments_count"] >= 1
    assert trust_data["score"] >= 50
