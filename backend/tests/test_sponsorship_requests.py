import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sponsorship_requests_comprehensive(client: AsyncClient):
    # 1. Register Entrepreneur A & B
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "priya.ai@vynk.io",
        "password": "Password123!",
        "full_name": "Priya Sharma",
        "role": "entrepreneur",
        "stage": "mvp",
        "industry": "AI & Robotics",
    })
    assert ent_res.status_code == 201
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}

    ent2_res = await client.post("/api/v1/auth/register", json={
        "email": "other.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Other Founder",
        "role": "entrepreneur",
        "stage": "idea",
        "industry": "FinTech",
    })
    assert ent2_res.status_code == 201
    ent2_token = ent2_res.json()["access_token"]
    ent2_headers = {"Authorization": f"Bearer {ent2_token}"}

    # 2. Register Sponsor A & B
    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "vikram.sponsor@vynk.io",
        "password": "SponsorPassword123!",
        "full_name": "Vikram Malhotra",
        "role": "sponsor",
        "organization_name": "Nexus Spark Capital",
        "sponsor_type": "venture_fund",
        "min_budget": 100000,
        "max_budget": 2000000,
    })
    assert spon_res.status_code == 201
    spon_data = spon_res.json()
    spon_token = spon_data["access_token"]
    spon_headers = {"Authorization": f"Bearer {spon_token}"}
    me_spon = await client.get("/api/v1/auth/me", headers=spon_headers)
    spon_id = me_spon.json()["id"]

    spon2_res = await client.post("/api/v1/auth/register", json={
        "email": "ananya.angel@vynk.io",
        "password": "SponsorPassword123!",
        "full_name": "Ananya Roy",
        "role": "sponsor",
        "organization_name": "Indus Angel Network",
        "sponsor_type": "individual_angel",
        "min_budget": 50000,
        "max_budget": 500000,
    })
    assert spon2_res.status_code == 201
    spon2_token = spon2_res.json()["access_token"]
    spon2_headers = {"Authorization": f"Bearer {spon2_token}"}
    me_spon2 = await client.get("/api/v1/auth/me", headers=spon2_headers)
    spon2_id = me_spon2.json()["id"]

    # 3. Entrepreneur A creates project
    proj_res = await client.post(
        "/api/v1/projects/",
        headers=ent_headers,
        json={
            "title": "AeroNav AI Navigation",
            "tagline": "Autonomous UAV navigation in GPS-denied environments",
            "description": "Visual-inertial odometry paired with onboard edge neural inference for delivery drones.",
            "category": "AI",
            "stage": "mvp",
            "funding_goal": 1500000.0,
            "currency": "INR",
        }
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 4. Entrepreneur A submits monetary sponsorship request to Sponsor A
    req1_res = await client.post(
        "/api/v1/sponsorship-requests/",
        headers=ent_headers,
        json={
            "project_id": proj_id,
            "recipient_id": spon_id,
            "sponsorship_type": "Financial Funding",
            "requested_amount": 500000.0,
            "currency": "INR",
            "message": "We would love Nexus Spark Capital to lead our seed tranche.",
        }
    )
    assert req1_res.status_code == 201, req1_res.text
    req1 = req1_res.json()
    assert req1["status"] == "pending"
    assert req1["currency"] == "INR"
    assert req1["requested_amount"] == 500000.0
    assert req1["project"]["title"] == "AeroNav AI Navigation"
    req1_id = req1["id"]

    # 5. Duplicate prevention: Trying to submit another pending request for same project & sponsor
    dup_res = await client.post(
        "/api/v1/sponsorship-requests/",
        headers=ent_headers,
        json={
            "project_id": proj_id,
            "recipient_id": spon_id,
            "sponsorship_type": "Financial Funding",
            "requested_amount": 250000.0,
            "message": "Second attempt should be rejected.",
        }
    )
    assert dup_res.status_code == 400
    assert "pending sponsorship request already exists" in dup_res.json()["detail"]

    # 6. Non-monetary request: Entrepreneur A creates request for Hardware/Cloud Credits with amount=None
    req2_res = await client.post(
        "/api/v1/sponsorship-requests/",
        headers=ent_headers,
        json={
            "project_id": proj_id,
            "recipient_id": spon2_id,
            "sponsorship_type": "Hardware",
            "requested_amount": None,
            "requested_resources": "5x Jetson Orin Nano development kits and sensor test rigs",
            "currency": "INR",
            "message": "Seeking hardware evaluation units for flight validation trials.",
        }
    )

    assert req2_res.status_code == 201
    req2 = req2_res.json()
    assert req2["status"] == "pending"
    assert req2["requested_amount"] is None
    assert "Jetson Orin" in req2["requested_resources"]

    # 7. Authorization: Sponsor cannot create sponsorship request (only entrepreneur)
    spon_create_res = await client.post(
        "/api/v1/sponsorship-requests/",
        headers=spon_headers,
        json={
            "project_id": proj_id,
            "recipient_id": spon_id,
            "message": "Should fail with 403.",
        }
    )
    assert spon_create_res.status_code == 403

    # 8. Authorization: Entrepreneur B cannot request sponsorship for Entrepreneur A's project
    other_ent_res = await client.post(
        "/api/v1/sponsorship-requests/",
        headers=ent2_headers,
        json={
            "project_id": proj_id,
            "recipient_id": spon_id,
            "message": "Should fail with 404.",
        }
    )
    assert other_ent_res.status_code == 404

    # 9. List requests:
    # - Entrepreneur A sees their 2 sent requests
    ent_list_res = await client.get("/api/v1/sponsorship-requests/", headers=ent_headers)
    assert ent_list_res.status_code == 200
    assert len(ent_list_res.json()) >= 2

    # - Sponsor A sees 1 incoming request (req1)
    spon_list_res = await client.get("/api/v1/sponsorship-requests/", headers=spon_headers)
    assert spon_list_res.status_code == 200
    assert len(spon_list_res.json()) == 1
    assert spon_list_res.json()[0]["id"] == req1_id

    # 10. Privacy / Security: Entrepreneur B cannot view req1 details
    private_res = await client.get(f"/api/v1/sponsorship-requests/{req1_id}", headers=ent2_headers)
    assert private_res.status_code == 404

    # 11. Sponsor A accepts req1:
    # Per User Correction #2: must create commitment in INTERESTED status!
    accept_res = await client.post(
        f"/api/v1/sponsorship-requests/{req1_id}/respond",
        headers=spon_headers,
        json={
            "action": "accept",
            "response_note": "Thrilled by your autonomous UAV progress. Let us explore terms.",
            "commitment_amount": 500000.0,
        }
    )
    assert accept_res.status_code == 200
    accepted_req = accept_res.json()
    assert accepted_req["status"] == "accepted"
    assert accepted_req["commitment_id"] is not None
    comm_id = accepted_req["commitment_id"]

    # Verify commitment was created in INTERESTED status!
    comm_res = await client.get(f"/api/v1/commitments/{comm_id}", headers=spon_headers)
    assert comm_res.status_code == 200
    comm_data = comm_res.json()
    assert comm_data["status"] == "interested"
    assert comm_data["amount"] == 500000.0
    assert comm_data["currency"] == "INR"

    # 12. Entrepreneur A cancels req2 (pending hardware request to Sponsor 2)
    cancel_res = await client.post(
        f"/api/v1/sponsorship-requests/{req2['id']}/cancel",
        headers=ent_headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # 13. Sponsor 2 cannot respond to an already cancelled request
    spon2_resp_res = await client.post(
        f"/api/v1/sponsorship-requests/{req2['id']}/respond",
        headers=spon2_headers,
        json={"action": "accept"}
    )
    assert spon2_resp_res.status_code == 400
