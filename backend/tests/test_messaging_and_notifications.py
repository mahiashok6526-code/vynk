import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_messaging_authorization_and_lifecycle(client: AsyncClient):
    # 1. Register Entrepreneur and Sponsor
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "msg.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Messaging Founder",
        "role": "entrepreneur",
        "stage": "mvp",
        "industry": "AI & HealthTech",
    })
    assert ent_res.status_code == 201
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}
    me_ent = await client.get("/api/v1/auth/me", headers=ent_headers)
    ent_id = me_ent.json()["id"]

    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "msg.sponsor@vynk.io",
        "password": "Password123!",
        "full_name": "Messaging Sponsor",
        "role": "sponsor",
        "organization_name": "Apex Seed Fund",
        "sponsor_type": "venture_fund",
        "min_budget": 50000,
        "max_budget": 1000000,
    })
    assert spon_res.status_code == 201
    spon_token = spon_res.json()["access_token"]
    spon_headers = {"Authorization": f"Bearer {spon_token}"}
    me_spon = await client.get("/api/v1/auth/me", headers=spon_headers)
    spon_id = me_spon.json()["id"]

    # 2. Register a bystander/third-party
    other_res = await client.post("/api/v1/auth/register", json={
        "email": "bystander@vynk.io",
        "password": "Password123!",
        "full_name": "Bystander User",
        "role": "entrepreneur",
        "stage": "idea",
        "industry": "EdTech",
    })
    assert other_res.status_code == 201
    other_token = other_res.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # 3. Unauthorized conversation attempt (no relationship exists)
    unauth_conv = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id, "initial_message": "Hello sponsor"},
        headers=ent_headers,
    )
    assert unauth_conv.status_code == 403
    assert "Direct messaging requires an active platform relationship" in unauth_conv.json()["detail"]

    # 4. Self-messaging prevention
    self_conv = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": ent_id},
        headers=ent_headers,
    )
    assert self_conv.status_code == 400
    assert "Cannot start a conversation with yourself" in self_conv.json()["detail"]

    # 5. Create Project & Pending Sponsorship Request to establish relationship
    proj_res = await client.post(
        "/api/v1/projects/",
        json={
            "title": "BioScan AI",
            "tagline": "AI-guided medical diagnosis",
            "description": "Comprehensive diagnostics system using neural vision models.",
            "category": "AI",
            "stage": "mvp",
            "funding_goal": 500000.0,
            "currency": "INR",
        },
        headers=ent_headers,
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    req_res = await client.post(
        "/api/v1/sponsorship-requests/",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "message": "We would love Apex Seed Fund to back BioScan AI.",
            "requested_amount": 250000.0,
            "currency": "INR",
            "sponsorship_type": "Financial Funding",
        },
        headers=ent_headers,
    )
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # 6. Now conversation creation is authorized (PENDING relationship exists)
    conv_create = await client.post(
        "/api/v1/messages/conversations",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "sponsorship_request_id": req_id,
            "initial_message": "Thank you for reviewing our proposal!",
        },
        headers=ent_headers,
    )
    assert conv_create.status_code == 201
    conv_data = conv_create.json()
    conv_id = conv_data["id"]
    assert conv_data["project_id"] == project_id
    assert conv_data["project_title"] == "BioScan AI"
    assert len(conv_data["messages"]) == 1
    assert conv_data["messages"][0]["content"] == "Thank you for reviewing our proposal!"

    # 7. Duplicate conversation prevention (calling create again returns same conversation)
    dup_conv = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id},
        headers=ent_headers,
    )
    assert dup_conv.status_code == 201
    assert dup_conv.json()["id"] == conv_id

    # 8. Unread counts for recipient sponsor
    spon_unread = await client.get("/api/v1/messages/unread-count", headers=spon_headers)
    assert spon_unread.status_code == 200
    assert spon_unread.json()["unread_messages"] == 1

    # 9. Message validation: empty message
    empty_msg = await client.post(
        f"/api/v1/messages/conversations/{conv_id}/messages",
        json={"content": "   "},
        headers=spon_headers,
    )
    assert empty_msg.status_code == 422 or empty_msg.status_code == 400

    # 10. Message validation: oversized message (>5000 chars)
    big_msg = await client.post(
        f"/api/v1/messages/conversations/{conv_id}/messages",
        json={"content": "x" * 5001},
        headers=spon_headers,
    )
    assert big_msg.status_code == 422 or big_msg.status_code == 400

    # 11. Send valid reply from Sponsor
    reply_res = await client.post(
        f"/api/v1/messages/conversations/{conv_id}/messages",
        json={"content": "We reviewed your pitch and would like to discuss terms."},
        headers=spon_headers,
    )
    assert reply_res.status_code == 201
    reply_data = reply_res.json()
    assert reply_data["sender_id"] == spon_id
    assert reply_data["recipient_id"] == ent_id
    assert reply_data["is_read"] is False

    # 12. Unauthorized access protection (bystander cannot read or write to conversation)
    bystander_read = await client.get(
        f"/api/v1/messages/conversations/{conv_id}",
        headers=other_headers,
    )
    assert bystander_read.status_code == 403

    bystander_send = await client.post(
        f"/api/v1/messages/conversations/{conv_id}/messages",
        json={"content": "I should not be here"},
        headers=other_headers,
    )
    assert bystander_send.status_code == 403

    # 13. Chronological message ordering and automatic read marking
    ent_view = await client.get(
        f"/api/v1/messages/conversations/{conv_id}",
        headers=ent_headers,
    )
    assert ent_view.status_code == 200
    msgs = ent_view.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["sender_id"] == ent_id
    assert msgs[1]["sender_id"] == spon_id
    assert msgs[1]["is_read"] is True  # marked read upon viewing

    # 14. List conversations
    ent_list = await client.get("/api/v1/messages/conversations", headers=ent_headers)
    assert ent_list.status_code == 200
    assert len(ent_list.json()) == 1
    assert ent_list.json()[0]["id"] == conv_id
    assert ent_list.json()[0]["other_participant"]["id"] == spon_id


@pytest.mark.asyncio
async def test_rejected_and_cancelled_request_authorization(client: AsyncClient):
    # Register Entrepreneur R & Sponsor R
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "rejected.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Rejected Founder",
        "role": "entrepreneur",
        "stage": "mvp",
        "industry": "FinTech",
    })
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}
    ent_id = ent_res.json()["user"]["id"] if "user" in ent_res.json() else (await client.get("/api/v1/auth/me", headers=ent_headers)).json()["id"]

    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "declining.sponsor@vynk.io",
        "password": "Password123!",
        "full_name": "Declining Sponsor",
        "role": "sponsor",
        "organization_name": "Conservative Ventures",
        "sponsor_type": "corporate",
    })
    spon_token = spon_res.json()["access_token"]
    spon_headers = {"Authorization": f"Bearer {spon_token}"}
    spon_id = (await client.get("/api/v1/auth/me", headers=spon_headers)).json()["id"]

    # Create project
    proj_res = await client.post(
        "/api/v1/projects/",
        json={
            "title": "FinLend",
            "tagline": "Micro-lending platform",
            "description": "Peer to peer micro lending platform for local artisans.",
            "category": "FinTech",
            "stage": "prototype",
            "funding_goal": 100000.0,
            "currency": "INR",
        },
        headers=ent_headers,
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # Submit request
    req_res = await client.post(
        "/api/v1/sponsorship-requests/",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "message": "Would love your support.",
            "requested_amount": 50000.0,
            "sponsorship_type": "Financial Funding",
        },
        headers=ent_headers,
    )
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # Sponsor REJECTS request
    reject_res = await client.post(
        f"/api/v1/sponsorship-requests/{req_id}/respond",
        json={"action": "reject", "response_note": "Outside our investment thesis."},
        headers=spon_headers,
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"

    # CORRECTION RULE 5: REJECTED request alone CANNOT initiate a NEW conversation!
    new_conv_ent = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id, "initial_message": "Why did you reject?"},
        headers=ent_headers,
    )
    assert new_conv_ent.status_code == 403

    new_conv_spon = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": ent_id, "initial_message": "Sorry about rejecting."},
        headers=spon_headers,
    )
    assert new_conv_spon.status_code == 403

    # Now test CANCELLED request:
    # Submit second request
    req2_res = await client.post(
        "/api/v1/sponsorship-requests/",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "message": "Trying again with smaller amount.",
            "requested_amount": 25000.0,
            "sponsorship_type": "Financial Funding",
        },
        headers=ent_headers,
    )
    assert req2_res.status_code == 201
    req2_id = req2_res.json()["id"]

    # Entrepreneur CANCELS request
    cancel_res = await client.post(
        f"/api/v1/sponsorship-requests/{req2_id}/cancel",
        headers=ent_headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # CORRECTION RULE 6: CANCELLED request alone CANNOT initiate a NEW conversation!
    new_conv_cancel = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id, "initial_message": "Can we still talk?"},
        headers=ent_headers,
    )
    assert new_conv_cancel.status_code == 403

    # CORRECTION RULE 7: Historical preservation
    # If a conversation was established while relationship was valid (e.g. pending request 3),
    # and then the request is cancelled or rejected, historical messages remain accessible!
    req3_res = await client.post(
        "/api/v1/sponsorship-requests/",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "message": "Third valid request.",
            "requested_amount": 10000.0,
            "sponsorship_type": "Mentorship",
        },
        headers=ent_headers,
    )
    assert req3_res.status_code == 201
    req3_id = req3_res.json()["id"]

    # Create conversation while valid
    valid_conv = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id, "initial_message": "Discussing mentorship."},
        headers=ent_headers,
    )
    assert valid_conv.status_code == 201
    v_conv_id = valid_conv.json()["id"]

    # Now reject request 3
    await client.post(
        f"/api/v1/sponsorship-requests/{req3_id}/respond",
        json={"action": "reject", "response_note": "No capacity for mentorship."},
        headers=spon_headers,
    )

    # Historical conversation remains fully readable for audit purposes
    audit_view = await client.get(
        f"/api/v1/messages/conversations/{v_conv_id}",
        headers=ent_headers,
    )
    assert audit_view.status_code == 200
    assert len(audit_view.json()["messages"]) == 1
    assert audit_view.json()["messages"][0]["content"] == "Discussing mentorship."


@pytest.mark.asyncio
async def test_notifications_lifecycle_and_preferences(client: AsyncClient):
    # 1. Register users
    ent_res = await client.post("/api/v1/auth/register", json={
        "email": "notif.founder@vynk.io",
        "password": "Password123!",
        "full_name": "Notif Founder",
        "role": "entrepreneur",
        "stage": "prototype",
        "industry": "CleanTech",
    })
    ent_token = ent_res.json()["access_token"]
    ent_headers = {"Authorization": f"Bearer {ent_token}"}
    ent_id = (await client.get("/api/v1/auth/me", headers=ent_headers)).json()["id"]

    spon_res = await client.post("/api/v1/auth/register", json={
        "email": "notif.sponsor@vynk.io",
        "password": "Password123!",
        "full_name": "Notif Sponsor",
        "role": "sponsor",
        "organization_name": "Green Impact Partners",
        "sponsor_type": "impact_investor",
    })
    spon_token = spon_res.json()["access_token"]
    spon_headers = {"Authorization": f"Bearer {spon_token}"}
    spon_id = (await client.get("/api/v1/auth/me", headers=spon_headers)).json()["id"]

    # 2. Check default notification preferences
    pref_res = await client.get("/api/v1/notifications/preferences", headers=ent_headers)
    assert pref_res.status_code == 200
    pref_data = pref_res.json()
    assert pref_data["in_app_messages"] is True
    assert pref_data["in_app_sponsorship_requests"] is True
    assert pref_data["in_app_commitments"] is True
    assert pref_data["email_notifications"] is False

    # 3. Create project & request -> generates notification for Sponsor
    proj_res = await client.post(
        "/api/v1/projects/",
        json={
            "title": "SolarPurify",
            "tagline": "Solar water purification",
            "description": "Portable water purification systems powered by smart solar cells.",
            "category": "CleanTech",
            "stage": "prototype",
            "funding_goal": 300000.0,
            "currency": "INR",
        },
        headers=ent_headers,
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    req_res = await client.post(
        "/api/v1/sponsorship-requests/",
        json={
            "recipient_id": spon_id,
            "project_id": project_id,
            "message": "Let us partner for clean water impact.",
            "requested_amount": 150000.0,
            "sponsorship_type": "Financial Funding",
        },
        headers=ent_headers,
    )
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # Verify Sponsor received in-app notification
    spon_notifs = await client.get("/api/v1/notifications", headers=spon_headers)
    assert spon_notifs.status_code == 200
    items = spon_notifs.json()["items"]
    assert len(items) >= 1
    assert items[0]["type"] == "sponsorship_request"
    assert "SolarPurify" in items[0]["title"]
    notif_id = items[0]["id"]

    # 4. Mark single notification as read
    read_res = await client.patch(f"/api/v1/notifications/{notif_id}/read", headers=spon_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # 5. Sponsor accepts request -> creates commitment and notifies Entrepreneur
    accept_res = await client.post(
        f"/api/v1/sponsorship-requests/{req_id}/respond",
        json={"action": "accept", "commitment_amount": 150000.0, "response_note": "Excited to partner!"},
        headers=spon_headers,
    )
    assert accept_res.status_code == 200
    comm_id = accept_res.json()["commitment_id"]

    ent_notifs = await client.get("/api/v1/notifications", headers=ent_headers)
    assert ent_notifs.status_code == 200
    ent_items = ent_notifs.json()["items"]
    assert any("Accepted" in n["title"] for n in ent_items)

    # 6. Progress commitment through status lifecycle -> generates status change notification
    prog_res = await client.patch(
        f"/api/v1/commitments/{comm_id}/status",
        json={"new_status": "discussion", "note": "Moving to active discussion phase."},
        headers=ent_headers,
    )
    assert prog_res.status_code == 200

    # 7. Add milestone update -> generates milestone notification
    ms_res = await client.post(
        f"/api/v1/commitments/{comm_id}/updates",
        json={
            "update_type": "milestone",
            "title": "Solar filter membrane prototype verified",
            "note": "Lab testing completed with 99.8% filtration rate.",
            "evidence_reference": "https://solarpurify.io/lab-results-v1.pdf",
        },
        headers=ent_headers,
    )
    assert ms_res.status_code == 201

    # Check sponsor received milestone notification
    spon_notifs2 = await client.get("/api/v1/notifications", headers=spon_headers)
    assert any(n["type"] == "milestone" for n in spon_notifs2.json()["items"])

    # 8. Mark all notifications as read
    mark_all = await client.post("/api/v1/notifications/read-all", headers=spon_headers)
    assert mark_all.status_code == 200

    spon_unread_count = await client.get("/api/v1/notifications/unread-count", headers=spon_headers)
    assert spon_unread_count.json()["unread_notifications"] == 0

    # 9. Test unread summary endpoint
    summary = await client.get("/api/v1/notifications/unread-summary", headers=spon_headers)
    assert summary.status_code == 200
    assert "unread_messages" in summary.json()
    assert "unread_notifications" in summary.json()

    # 10. Preference suppression test: disable in_app_messages
    update_pref = await client.patch(
        "/api/v1/notifications/preferences",
        json={"in_app_messages": False},
        headers=spon_headers,
    )
    assert update_pref.status_code == 200
    assert update_pref.json()["in_app_messages"] is False

    # Send a message to sponsor
    # First get or create conversation
    conv_res = await client.post(
        "/api/v1/messages/conversations",
        json={"recipient_id": spon_id, "initial_message": "Hello sponsor!"},
        headers=ent_headers,
    )
    c_id = conv_res.json()["id"]

    # Sponsor should NOT get in_app notification for new message because preference is disabled
    spon_notifs_suppressed = await client.get("/api/v1/notifications?unread_only=true", headers=spon_headers)
    assert not any(n["type"] == "new_message" for n in spon_notifs_suppressed.json()["items"])

    # Re-enable in_app_messages
    await client.patch(
        "/api/v1/notifications/preferences",
        json={"in_app_messages": True},
        headers=spon_headers,
    )
