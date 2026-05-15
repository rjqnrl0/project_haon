import io
import uuid

import pytest
from PIL import Image


def make_test_jpeg(width=800, height=600) -> bytes:
    img = Image.new("RGB", (width, height), color="purple")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


async def create_completed_fitting(client, auth_headers) -> str:
    body_bytes = make_test_jpeg(800, 600)
    files = {"file": ("body.jpg", body_bytes, "image/jpeg")}
    resp = await client.post("/fitting/body/upload", files=files, headers=auth_headers)
    task_id = resp.json()["task_id"]

    resp = await client.post(
        "/fitting/execute",
        json={"body_image_id": task_id, "clothing_ids": []},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    return task_id


@pytest.mark.asyncio
async def test_download_creates_watermarked_image(client, auth_headers):
    task_id = await create_completed_fitting(client, auth_headers)
    resp = await client.post(
        "/share/download",
        json={"source_task_id": task_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "download_url" in data
    assert data["filename"].endswith(".jpg")


@pytest.mark.asyncio
async def test_create_share_link(client, auth_headers):
    task_id = await create_completed_fitting(client, auth_headers)
    resp = await client.post(
        "/share/create",
        json={"source_task_id": task_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "share_token" in data
    assert "share_url" in data
    assert "/share/" in data["share_url"]
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_get_shared_image(client, auth_headers):
    task_id = await create_completed_fitting(client, auth_headers)
    resp = await client.post(
        "/share/create",
        json={"source_task_id": task_id},
        headers=auth_headers,
    )
    share_token = resp.json()["share_token"]

    # Access shared image (public, no auth)
    resp = await client.get(f"/share/{share_token}")
    assert resp.status_code == 200
    data = resp.json()
    assert "image_url" in data
    assert "title" in data


@pytest.mark.asyncio
async def test_get_shared_image_not_found(client):
    resp = await client.get(f"/share/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_task_not_found(client, auth_headers):
    resp = await client.post(
        "/share/download",
        json={"source_task_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 404
