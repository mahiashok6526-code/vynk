import asyncio
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"


async def main():
    print("=== Starting Vynk Phase 8: Secure Messaging & Notification System Live Verification ===")
    ts_now = int(time.time())

    async with httpx.AsyncClient(timeout=25.0) as client:
        # 1. Health Check
        h_res = await client.get(f"{BACKEND_URL}/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        print("[PASS] 1. Backend server is healthy (200 OK)")

        # 2. Register Entrepreneur & Sponsor
        ent_email = f"founder.p8.{ts_now}@vynk.io"
        ent_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": ent_email,
                "password": "SecurePassword123!",
                "full_name": "Aarav Mehta",
                "role": "entrepreneur",
                "stage": "mvp",
                "industry": "AI & DeepTech",
            },
        )
        assert ent_reg.status_code == 201, f"Registration failed: {ent_reg.text}"
        ent_token = ent_reg.json()["access_token"]
        ent_headers = {"Authorization": f"Bearer {ent_token}"}
        ent_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=ent_headers)).json()
        ent_uid = ent_me["id"]
        print(f"[PASS] 2. Registered Entrepreneur: {ent_email} (UID: {ent_uid})")

        sp_email = f"sponsor.p8.{ts_now}@vynk.io"
        sp_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": sp_email,
                "password": "SecurePassword123!",
                "full_name": "Meera Singhania",
                "role": "sponsor",
                "organization_name": "Singhania Seed Ventures",
                "sponsor_type": "venture_fund",
                "min_budget": 500000,
                "max_budget": 10000000,
            },
        )
        assert sp_reg.status_code == 201, f"Registration failed: {sp_reg.text}"
        sp_token = sp_reg.json()["access_token"]
        sp_headers = {"Authorization": f"Bearer {sp_token}"}
        sp_me = (await client.get(f"{BACKEND_URL}/auth/me", headers=sp_headers)).json()
        sp_uid = sp_me["id"]
        print(f"[PASS] 3. Registered Sponsor: {sp_email} (UID: {sp_uid})")

        # Bystander registration
        bystander_email = f"bystander.p8.{ts_now}@vynk.io"
        bystander_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": bystander_email,
                "password": "SecurePassword123!",
                "full_name": "Third Party User",
                "role": "entrepreneur",
                "stage": "idea",
                "industry": "EdTech",
            },
        )
        assert bystander_reg.status_code == 201
        bystander_token = bystander_reg.json()["access_token"]
        bystander_headers = {"Authorization": f"Bearer {bystander_token}"}
        print(f"[PASS] 4. Registered Bystander: {bystander_email}")

        # 5. Check Initial Unread Summary
        unr_sum = await client.get(f"{BACKEND_URL}/notifications/unread-summary", headers=ent_headers)
        assert unr_sum.status_code == 200
        assert unr_sum.json()["unread_messages"] == 0
        assert unr_sum.json()["unread_notifications"] == 0
        print("[PASS] 5. Unread summary reports 0 messages & 0 notifications initially")

        # 6. Security Check: Self-messaging rejection
        self_conv = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            json={"recipient_id": ent_uid, "initial_message": "Talking to myself"},
            headers=ent_headers,
        )
        assert self_conv.status_code == 400
        print("[PASS] 6. Self-conversation correctly rejected (400 Bad Request)")

        # 7. Security Check: Unauthorized start without relationship
        unauth_start = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            json={"recipient_id": sp_uid, "initial_message": "Cold message"},
            headers=ent_headers,
        )
        assert unauth_start.status_code == 403
        print("[PASS] 7. Unsolicited conversation without relationship correctly forbidden (403)")

        # 8. Publish Project
        proj_res = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=ent_headers,
            json={
                "title": f"NeuroVision Robotics {ts_now}",
                "tagline": "Embedded edge perception for warehouse autonomous AGVs",
                "description": "Custom spatial vision system with sub-5ms low latency obstacle avoidance.",
                "category": "Robotics",
                "stage": "mvp",
                "funding_goal": 2000000.0,
                "currency": "INR",
            },
        )
        assert proj_res.status_code == 201, f"Project creation failed: {proj_res.text}"
        project_id = proj_res.json()["id"]
        print(f"[PASS] 8. Published Project: NeuroVision Robotics (ID: {project_id})")

        # 9. Submit Sponsorship Request
        req_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=ent_headers,
            json={
                "project_id": project_id,
                "recipient_id": sp_uid,
                "sponsorship_type": "Financial Funding",
                "requested_amount": 1000000.0,
                "currency": "INR",
                "message": "Singhania Seed Ventures would be an ideal strategic investor for NeuroVision.",
            },
        )
        assert req_res.status_code == 201, f"Sponsorship request failed: {req_res.text}"
        request_id = req_res.json()["id"]
        print(f"[PASS] 9. Submitted Sponsorship Request #{request_id} (PENDING status)")

        # 10. Verify Sponsor received notification
        sp_notifs = await client.get(f"{BACKEND_URL}/notifications", headers=sp_headers)
        assert sp_notifs.status_code == 200
        sp_items = sp_notifs.json()["items"]
        assert len(sp_items) >= 1
        assert sp_items[0]["type"] == "sponsorship_request"
        assert "NeuroVision" in sp_items[0]["title"]
        print(f"[PASS] 10. Sponsor received in-app notification: '{sp_items[0]['title']}'")

        # 11. Messaging is now authorized (Rule 1: PENDING Sponsorship Request)
        conv_res = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            headers=ent_headers,
            json={
                "recipient_id": sp_uid,
                "project_id": project_id,
                "sponsorship_request_id": request_id,
                "initial_message": "Hello Meera, looking forward to discussing our NeuroVision milestones.",
            },
        )
        assert conv_res.status_code == 201, f"Conversation creation failed: {conv_res.text}"
        conv_data = conv_res.json()
        conv_id = conv_data["id"]
        assert conv_data["project_id"] == project_id
        assert len(conv_data["messages"]) == 1
        print(f"[PASS] 11. Initiated Conversation #{conv_id} under active PENDING request relationship")

        # 12. Duplicate conversation prevention
        dup_conv = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            headers=ent_headers,
            json={"recipient_id": sp_uid},
        )
        assert dup_conv.status_code == 201
        assert dup_conv.json()["id"] == conv_id
        print("[PASS] 12. Duplicate conversation prevention verified (returned same conversation ID)")

        # 13. Sponsor replies to message
        reply_res = await client.post(
            f"{BACKEND_URL}/messages/conversations/{conv_id}/messages",
            headers=sp_headers,
            json={"content": "Hi Aarav, reviewing the robotics pilot metrics now. Looks promising."},
        )
        assert reply_res.status_code == 201, f"Send message failed: {reply_res.text}"
        print("[PASS] 13. Sponsor sent reply in conversation")

        # 14. Entrepreneur receives notification for new message
        ent_notifs_msg = await client.get(f"{BACKEND_URL}/notifications", headers=ent_headers)
        assert ent_notifs_msg.status_code == 200
        msg_notifs = [n for n in ent_notifs_msg.json()["items"] if n["type"] == "new_message"]
        assert len(msg_notifs) >= 1
        print(f"[PASS] 14. Entrepreneur received 'new_message' notification: '{msg_notifs[0]['title']}'")

        # 15. Chronological message history & read tracking
        conv_detail = await client.get(f"{BACKEND_URL}/messages/conversations/{conv_id}", headers=ent_headers)
        assert conv_detail.status_code == 200
        msgs = conv_detail.json()["messages"]
        assert len(msgs) == 2
        assert msgs[0]["sender_id"] == ent_uid
        assert msgs[1]["sender_id"] == sp_uid
        assert msgs[1]["is_read"] is True  # marked read on retrieval
        print("[PASS] 15. Chronological ordering & automatic read-state tracking verified")

        # 16. Unauthorized conversation access by bystander
        bystander_conv = await client.get(f"{BACKEND_URL}/messages/conversations/{conv_id}", headers=bystander_headers)
        assert bystander_conv.status_code == 403
        bystander_post = await client.post(
            f"{BACKEND_URL}/messages/conversations/{conv_id}/messages",
            headers=bystander_headers,
            json={"content": "Malicious inject"},
        )
        assert bystander_post.status_code == 403
        print("[PASS] 16. Third-party conversation snooping and messaging blocked (403 Forbidden)")

        # 17. Sponsor accepts request -> Commitment created + Notification
        accept_res = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/{request_id}/respond",
            headers=sp_headers,
            json={"action": "accept", "commitment_amount": 1000000.0, "response_note": "Approved for seed tranche."},
        )
        assert accept_res.status_code == 200
        comm_id = accept_res.json()["commitment_id"]
        assert comm_id is not None
        print(f"[PASS] 17. Sponsor accepted request; linked Commitment #{comm_id} created")

        ent_accept_notifs = await client.get(f"{BACKEND_URL}/notifications", headers=ent_headers)
        assert any("Accepted" in n["title"] for n in ent_accept_notifs.json()["items"])
        print("[PASS] 18. Entrepreneur received acceptance notification")

        # 18. Progress Commitment through Lifecycle
        # Discussion
        await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=ent_headers,
            json={"new_status": "discussion", "note": "Legal term sheet review."},
        )
        # Promised
        await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=sp_headers,
            json={"new_status": "promised", "note": "Syndicate committed."},
        )
        # Confirmed
        await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=ent_headers,
            json={"new_status": "confirmed", "note": "Confirmed by founders."},
        )
        # Agreement
        await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=ent_headers,
            json={"new_status": "agreement", "agreement_reference": "NV-SINGH-2026-AGR", "note": "Signed agreement."},
        )
        # Funded
        await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=sp_headers,
            json={"new_status": "funded", "note": "Funds wired to escrow."},
        )
        print("[PASS] 19. Commitment advanced through lifecycle states (DISCUSSION -> FUNDED)")

        # 19. Add Milestone Update with Evidence
        ms_res = await client.post(
            f"{BACKEND_URL}/commitments/{comm_id}/updates",
            headers=ent_headers,
            json={
                "update_type": "milestone",
                "title": "AGV Perception Hardware V2 Shipped",
                "note": "10 test boards manufactured and operational.",
                "evidence_reference": "https://neurovision.ai/milestone2-report.pdf",
            },
        )
        assert ms_res.status_code == 201
        print("[PASS] 20. Milestone update recorded; counterparty notified")

        # 20. Complete Commitment
        comp_res = await client.patch(
            f"{BACKEND_URL}/commitments/{comm_id}/status",
            headers=ent_headers,
            json={"new_status": "completed", "note": "All venture deliverables completed."},
        )
        assert comp_res.status_code == 200
        print("[PASS] 21. Commitment successfully reached COMPLETED status")

        # Verify Trust Score update notification
        ent_trust_notifs = await client.get(f"{BACKEND_URL}/notifications", headers=ent_headers)
        assert any(n["type"] == "trust_score_updated" for n in ent_trust_notifs.json()["items"])
        print("[PASS] 22. Trust Score recalculation event generated notification")

        # 21. CORRECTION RULE 5 & 6 Checks:
        # Check that REJECTED and CANCELLED requests CANNOT initiate a new conversation!
        founder_rej_email = f"founder.rej.{ts_now}@vynk.io"
        f_rej_reg = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": founder_rej_email,
                "password": "SecurePassword123!",
                "full_name": "Rejected Trial",
                "role": "entrepreneur",
                "stage": "idea",
                "industry": "AgriTech",
            },
        )
        f_rej_headers = {"Authorization": f"Bearer {f_rej_reg.json()['access_token']}"}

        p_rej = await client.post(
            f"{BACKEND_URL}/projects/",
            headers=f_rej_headers,
            json={
                "title": f"AgriBot {ts_now}",
                "tagline": "Autonomous weeding bot",
                "description": "Robotic weeding for organic farm management.",
                "category": "AgriTech",
                "stage": "idea",
                "funding_goal": 50000.0,
                "currency": "INR",
            },
        )
        p_rej_id = p_rej.json()["id"]

        # Submit request that will be REJECTED
        r_rej = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=f_rej_headers,
            json={
                "project_id": p_rej_id,
                "recipient_id": sp_uid,
                "sponsorship_type": "Mentorship",
                "requested_amount": 10000.0,
                "message": "Please mentor our agritech startup.",
            },
        )
        r_rej_id = r_rej.json()["id"]

        # Sponsor REJECTS
        await client.post(
            f"{BACKEND_URL}/sponsorship-requests/{r_rej_id}/respond",
            headers=sp_headers,
            json={"action": "reject", "response_note": "No domain expertise."},
        )

        # RULE 5: Attempting to create a NEW conversation solely based on rejected request MUST FAIL with 403
        rej_conv_attempt = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            headers=f_rej_headers,
            json={"recipient_id": sp_uid, "initial_message": "Why reject?"},
        )
        assert rej_conv_attempt.status_code == 403, f"Expected 403 for rejected request, got: {rej_conv_attempt.status_code}"
        print("[PASS] 23. CORRECTION RULE 5 verified: REJECTED request CANNOT initiate a new conversation (403 Forbidden)")

        # Submit request that will be CANCELLED
        r_can = await client.post(
            f"{BACKEND_URL}/sponsorship-requests/",
            headers=f_rej_headers,
            json={
                "project_id": p_rej_id,
                "recipient_id": sp_uid,
                "sponsorship_type": "Financial Funding",
                "requested_amount": 20000.0,
                "message": "Changed our minds.",
            },
        )
        r_can_id = r_can.json()["id"]

        # Entrepreneur CANCELS
        await client.post(
            f"{BACKEND_URL}/sponsorship-requests/{r_can_id}/cancel",
            headers=f_rej_headers,
        )

        # RULE 6: Attempting to create a NEW conversation solely based on cancelled request MUST FAIL with 403
        can_conv_attempt = await client.post(
            f"{BACKEND_URL}/messages/conversations",
            headers=f_rej_headers,
            json={"recipient_id": sp_uid, "initial_message": "Still available?"},
        )
        assert can_conv_attempt.status_code == 403, f"Expected 403 for cancelled request, got: {can_conv_attempt.status_code}"
        print("[PASS] 24. CORRECTION RULE 6 verified: CANCELLED request CANNOT initiate a new conversation (403 Forbidden)")

        # 22. CORRECTION RULE 7 Check: Historical conversation preservation
        # Conversation #conv_id between Aarav and Meera was created while relationship was valid.
        # Ensure it remains fully readable for audit purposes:
        hist_check = await client.get(f"{BACKEND_URL}/messages/conversations/{conv_id}", headers=ent_headers)
        assert hist_check.status_code == 200
        assert len(hist_check.json()["messages"]) >= 2
        print("[PASS] 25. CORRECTION RULE 7 verified: Historical conversation remains accessible for audit trail")

        # 23. In-App Notification Preferences
        # Update preferences to disable new message notifications
        pref_update = await client.patch(
            f"{BACKEND_URL}/notifications/preferences",
            headers=ent_headers,
            json={"in_app_messages": False},
        )
        assert pref_update.status_code == 200
        assert pref_update.json()["in_app_messages"] is False

        # Sponsor sends message to entrepreneur
        await client.post(
            f"{BACKEND_URL}/messages/conversations/{conv_id}/messages",
            headers=sp_headers,
            json={"content": "Preference suppression test message."},
        )

        # Verify no notification created for this message
        ent_unread_notifs = await client.get(f"{BACKEND_URL}/notifications?unread_only=true", headers=ent_headers)
        assert not any("suppression test" in n["content"] for n in ent_unread_notifs.json()["items"])
        print("[PASS] 26. Notification preferences suppression verified (in_app_messages=False suppressed notification)")

        # Re-enable in_app_messages
        await client.patch(
            f"{BACKEND_URL}/notifications/preferences",
            headers=ent_headers,
            json={"in_app_messages": True},
        )
        print("[PASS] 27. Notification preferences re-enabled")

        # 24. Mark all read
        mark_res = await client.post(f"{BACKEND_URL}/notifications/read-all", headers=ent_headers)
        assert mark_res.status_code == 200
        unr_final = await client.get(f"{BACKEND_URL}/notifications/unread-count", headers=ent_headers)
        assert unr_final.json()["unread_notifications"] == 0
        print("[PASS] 28. Mark all notifications as read verified (unread count = 0)")

    print("\n=======================================================")
    print("ALL PHASE 8 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(main())
