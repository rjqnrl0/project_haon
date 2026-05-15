import pytest


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_invalid_token(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client, auth_headers, test_user):
    resp = await client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)
    assert data["face_registered"] is False


@pytest.mark.asyncio
async def test_logout_endpoint(client, auth_headers):
    resp = await client.post("/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
