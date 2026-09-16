import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_entrepreneur(client: AsyncClient):
    # 1. Register Entrepreneur
    payload = {
        "email": "sarah.founder@vynk.io",
        "password": "SecurePassword123!",
        "full_name": "Sarah Connor",
        "role": "entrepreneur",
        "stage": "prototype",
        "industry": "CleanTech",
    }
    reg_res = await client.post("/api/v1/auth/register", json=payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["role"] == "entrepreneur"
    token = reg_data["access_token"]

    # 2. Query /auth/me with Bearer token
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "sarah.founder@vynk.io"
    assert me_data["role"] == "entrepreneur"
    assert me_data["entrepreneur_profile"] is not None
    assert me_data["trust_score"]["score"] == 50

    # 3. Login with correct credentials
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "sarah.founder@vynk.io",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 4. Login with wrong password
    bad_login_res = await client.post("/api/v1/auth/login", json={
        "email": "sarah.founder@vynk.io",
        "password": "WrongPassword!"
    })
    assert bad_login_res.status_code == 401


@pytest.mark.asyncio
async def test_register_sponsor_role(client: AsyncClient):
    payload = {
        "email": "david.investor@vynk.io",
        "password": "VentureCapital2026!",
        "full_name": "David Miller",
        "role": "sponsor",
        "organization_name": "Apex Frontier Ventures",
        "sponsor_type": "venture_fund",
        "min_budget": 5000,
        "max_budget": 100000,
    }
    reg_res = await client.post("/api/v1/auth/register", json=payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["role"] == "sponsor"
    token = reg_data["access_token"]

    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["role"] == "sponsor"
    assert me_data["sponsor_profile"]["organization_name"] == "Apex Frontier Ventures"


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401
