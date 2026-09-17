import pytest
from httpx import AsyncClient


async def _register_entrepreneur(client: AsyncClient, email: str = "founder.trust@vynk.io"):
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Kavita Rao",
            "role": "entrepreneur",
            "stage": "mvp",
            "industry": "AgriTech",
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    return token, me_res.json()


async def _register_sponsor(client: AsyncClient, email: str = "sponsor.trust@vynk.io"):
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Rajiv Kapoor",
            "role": "sponsor",
            "organization_name": "Bharat Seed Ventures",
            "sponsor_type": "venture_fund",
            "min_budget": 500000,
            "max_budget": 10000000,
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    return token, me_res.json()


async def _create_project(client: AsyncClient, ent_token: str):
    res = await client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {ent_token}"},
        json={
            "title": "SmartKisan AI Irrigation",
            "tagline": "IoT-enabled precision water management",
            "description": "Smart precision water delivery saving 40% water",
            "category": "AgriTech",
            "stage": "mvp",
            "funding_goal": 2500000.0,
            "currency": "INR",
            "status": "draft",
        },
    )
    assert res.status_code == 201
    return res.json()


@pytest.mark.asyncio
async def test_initial_trust_score_and_breakdown(client: AsyncClient):
    token, user = await _register_entrepreneur(client, "initial.trust@vynk.io")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/trust/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 50
    assert data["score_version"] == 1
    assert data["verification_points"] == 0
    assert data["commitments_points"] == 20
    assert data["responsiveness_points"] == 15  # Milestone baseline
    assert data["activity_points"] == 15        # Activity baseline
    assert len(data["factors"]) == 4


@pytest.mark.asyncio
async def test_incremental_equals_recalculated_score(client: AsyncClient, db_session):
    from app.services.trust_service import TrustService
    token, user = await _register_entrepreneur(client, "recalc.trust@vynk.io")
    uid = user["id"]

    # 1. Base score
    ts_init = await TrustService.get_or_create_trust_score(db_session, uid)
    assert ts_init.score == 50

    # 2. Record an event incrementally
    ts_inc, is_new = await TrustService.record_event(
        db=db_session,
        user_id=uid,
        event_type="commitment_completed",
        impact=5,
        reason="Fulfillment test commitment",
        reference_type="commitment",
        reference_id=99991,
    )
    assert is_new is True
    score_after_event = ts_inc.score

    # 3. Explicitly recalculate
    ts_recalc = await TrustService.recalculate_trust_score(db_session, uid)
    
    # 4. ASSERT: incremental score == recalculated score
    assert score_after_event == ts_recalc.score
    assert ts_recalc.score == 55
    assert ts_recalc.commitments_points == 25


@pytest.mark.asyncio
async def test_idempotent_duplicate_event_prevention(client: AsyncClient, db_session):
    from app.services.trust_service import TrustService
    token, user = await _register_entrepreneur(client, "idempotent.trust@vynk.io")
    uid = user["id"]

    # First event
    ts1, is_new1 = await TrustService.record_event(
        db=db_session,
        user_id=uid,
        event_type="commitment_completed",
        impact=5,
        reason="Test event",
        reference_type="commitment",
        reference_id=88881,
    )
    assert is_new1 is True
    score1 = ts1.score

    # Second event with exact same reference
    ts2, is_new2 = await TrustService.record_event(
        db=db_session,
        user_id=uid,
        event_type="commitment_completed",
        impact=5,
        reason="Test event duplicate",
        reference_type="commitment",
        reference_id=88881,
    )
    assert is_new2 is False
    assert ts2.score == score1  # Did NOT increase again!


@pytest.mark.asyncio
async def test_symmetrical_completion_rewards_both_parties(client: AsyncClient):
    ent_token, ent_user = await _register_entrepreneur(client, "sym.ent@vynk.io")
    sp_token, sp_user = await _register_sponsor(client, "sym.sp@vynk.io")
    project = await _create_project(client, ent_token)

    sp_headers = {"Authorization": f"Bearer {sp_token}"}
    ent_headers = {"Authorization": f"Bearer {ent_token}"}

    # Initial scores
    sp_init = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    ent_init = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]

    # Sponsor creates commitment
    comm_res = await client.post(
        "/api/v1/commitments/",
        headers=sp_headers,
        json={
            "project_id": project["id"],
            "amount": 250000.0,
            "currency": "INR",
            "sponsorship_type": "grant",
            "status": "interested",
            "notes": "Full collaboration test",
        },
    )
    assert comm_res.status_code == 201
    cid = comm_res.json()["id"]

    # Progress through lifecycle
    await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "discussion", "note": "call"})
    await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "promised", "note": "terms"})
    await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "confirmed", "note": "confirm"})
    await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "agreement", "note": "contract"})
    await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "funded", "note": "transferred"})
    
    # Complete
    fin_res = await client.patch(f"/api/v1/commitments/{cid}/status", headers=sp_headers, json={"new_status": "completed", "note": "fulfilled"})
    assert fin_res.status_code == 200

    # Both parties must receive +5 points!
    sp_final = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    ent_final = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]

    assert sp_final == sp_init + 5
    assert ent_final == ent_init + 5


@pytest.mark.asyncio
async def test_milestone_points_and_anti_gaming_cap(client: AsyncClient):
    ent_token, ent_user = await _register_entrepreneur(client, "ms.ent@vynk.io")
    sp_token, sp_user = await _register_sponsor(client, "ms.sp@vynk.io")
    project = await _create_project(client, ent_token)

    sp_headers = {"Authorization": f"Bearer {sp_token}"}
    ent_headers = {"Authorization": f"Bearer {ent_token}"}

    # Create commitment
    comm_res = await client.post(
        "/api/v1/commitments/",
        headers=sp_headers,
        json={
            "project_id": project["id"],
            "amount": 100000.0,
            "sponsorship_type": "grant",
            "status": "interested",
            "notes": "Milestone testing",
        },
    )
    cid = comm_res.json()["id"]

    ent_init = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]

    # 1. Milestone 1 with evidence -> +2 pts
    m1 = await client.post(
        f"/api/v1/commitments/{cid}/updates",
        headers=ent_headers,
        json={
            "title": "Alpha prototype delivered",
            "note": "Delivered with working telemetry",
            "update_type": "milestone",
            "evidence_reference": "https://vynk.io/proof/m1",
        },
    )
    assert m1.status_code == 201
    ent_after_m1 = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]
    assert ent_after_m1 == ent_init + 2

    # 2. Milestone 2 with evidence -> +2 pts
    m2 = await client.post(
        f"/api/v1/commitments/{cid}/updates",
        headers=ent_headers,
        json={
            "title": "Beta telemetry tested",
            "note": "Stress test report uploaded",
            "update_type": "milestone",
            "evidence_reference": "https://vynk.io/proof/m2",
        },
    )
    assert m2.status_code == 201
    ent_after_m2 = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]
    assert ent_after_m2 == ent_init + 4

    # 3. Milestone 3 on SAME commitment -> CAP REACHED (Max 2 awards per commitment)
    m3 = await client.post(
        f"/api/v1/commitments/{cid}/updates",
        headers=ent_headers,
        json={
            "title": "Extra milestone",
            "note": "Should not award extra points beyond cap",
            "update_type": "milestone",
            "evidence_reference": "https://vynk.io/proof/m3",
        },
    )
    assert m3.status_code == 201
    ent_after_m3 = (await client.get("/api/v1/trust/me", headers=ent_headers)).json()["score"]
    assert ent_after_m3 == ent_after_m2  # Capped! No duplicate points!


@pytest.mark.asyncio
async def test_cancellation_rules_exploratory_vs_unilateral(client: AsyncClient):
    ent_token, ent_user = await _register_entrepreneur(client, "cancel.ent@vynk.io")
    sp_token, sp_user = await _register_sponsor(client, "cancel.sp@vynk.io")
    project = await _create_project(client, ent_token)
    sp_headers = {"Authorization": f"Bearer {sp_token}"}

    # 1. Exploratory cancellation from INTERESTED -> 0 penalty
    c1 = (await client.post(
        "/api/v1/commitments/",
        headers=sp_headers,
        json={"project_id": project["id"], "amount": 50000.0, "sponsorship_type": "grant", "notes": "exp"},
    )).json()["id"]

    score_before_exp = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    cancel_exp = await client.patch(
        f"/api/v1/commitments/{c1}/status",
        headers=sp_headers,
        json={"new_status": "cancelled", "note": "Decided not a fit", "cancellation_type": "mutual"},
    )
    assert cancel_exp.status_code == 200
    score_after_exp = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    assert score_after_exp == score_before_exp  # 0 penalty!

    # 2. Confirmed stage with MUTUAL cancellation -> 0 penalty
    c2 = (await client.post(
        "/api/v1/commitments/",
        headers=sp_headers,
        json={"project_id": project["id"], "amount": 75000.0, "sponsorship_type": "grant", "notes": "mut"},
    )).json()["id"]
    await client.patch(f"/api/v1/commitments/{c2}/status", headers=sp_headers, json={"new_status": "discussion", "note": "d"})
    await client.patch(f"/api/v1/commitments/{c2}/status", headers=sp_headers, json={"new_status": "promised", "note": "p"})
    await client.patch(f"/api/v1/commitments/{c2}/status", headers=sp_headers, json={"new_status": "confirmed", "note": "c"})
    
    cancel_mut = await client.patch(
        f"/api/v1/commitments/{c2}/status",
        headers=sp_headers,
        json={"new_status": "cancelled", "note": "Mutually agreed to terminate", "cancellation_type": "mutual"},
    )
    assert cancel_mut.status_code == 200
    score_after_mut = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    assert score_after_mut == score_before_exp  # Still 0 penalty!

    # 3. Confirmed stage with UNILATERAL cancellation -> -10 penalty to responsible party
    c3 = (await client.post(
        "/api/v1/commitments/",
        headers=sp_headers,
        json={"project_id": project["id"], "amount": 90000.0, "sponsorship_type": "grant", "notes": "uni"},
    )).json()["id"]
    await client.patch(f"/api/v1/commitments/{c3}/status", headers=sp_headers, json={"new_status": "discussion", "note": "d"})
    await client.patch(f"/api/v1/commitments/{c3}/status", headers=sp_headers, json={"new_status": "promised", "note": "p"})
    await client.patch(f"/api/v1/commitments/{c3}/status", headers=sp_headers, json={"new_status": "confirmed", "note": "c"})

    cancel_uni = await client.patch(
        f"/api/v1/commitments/{c3}/status",
        headers=sp_headers,
        json={"new_status": "cancelled", "note": "Unilaterally backed out without cause", "cancellation_type": "unilateral"},
    )
    assert cancel_uni.status_code == 200
    score_after_uni = (await client.get("/api/v1/trust/me", headers=sp_headers)).json()["score"]
    assert score_after_uni == score_before_exp - 10  # Penalized -10!


@pytest.mark.asyncio
async def test_public_trust_endpoint_strips_private_events(client: AsyncClient):
    ent_token, ent_user = await _register_entrepreneur(client, "priv.ent@vynk.io")
    sp_token, sp_user = await _register_sponsor(client, "priv.sp@vynk.io")
    ent_id = ent_user["id"]

    # 1. Private access (/me) contains events array
    me_res = await client.get("/api/v1/trust/me", headers={"Authorization": f"Bearer {ent_token}"})
    assert me_res.status_code == 200
    assert "events" in me_res.json()

    # 2. Public access (/users/{id}) strips events
    pub_res = await client.get(f"/api/v1/trust/users/{ent_id}")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert "events" not in pub_data
    assert "score" in pub_data
    assert "factors" in pub_data

    # 3. Authenticated other user accessing /users/{id} also receives stripped events
    other_res = await client.get(f"/api/v1/trust/users/{ent_id}", headers={"Authorization": f"Bearer {sp_token}"})
    assert other_res.status_code == 200
    assert "events" not in other_res.json()


@pytest.mark.asyncio
async def test_trust_score_history_pagination(client: AsyncClient):
    token, user = await _register_entrepreneur(client, "hist.ent@vynk.io")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.get("/api/v1/trust/history?limit=10&offset=0", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_events" in data
    assert "events" in data
    assert isinstance(data["events"], list)
