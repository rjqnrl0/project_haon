import io
import uuid

import pytest
from PIL import Image


def make_test_jpeg(width=800, height=600) -> bytes:
    img = Image.new("RGB", (width, height), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_weather_codi_success(client, auth_headers):
    resp = await client.post(
        "/recommend/weather",
        json={"city": "Tokyo"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "Tokyo"
    assert "codi_advice" in data
    assert "essential_items" in data
    assert isinstance(data["essential_items"], list)


@pytest.mark.asyncio
async def test_weather_codi_empty_city(client, auth_headers):
    resp = await client.post(
        "/recommend/weather",
        json={"city": "  "},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_size_recommendation_task_not_found(client, auth_headers):
    resp = await client.get(
        f"/recommend/size/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_size_recommendation_success(client, auth_headers):
    # First create a fitting task by uploading body
    body_bytes = make_test_jpeg(800, 600)
    files = {"file": ("body.jpg", body_bytes, "image/jpeg")}
    resp = await client.post("/fitting/body/upload", files=files, headers=auth_headers)
    task_id = resp.json()["task_id"]

    # Get size recommendation
    resp = await client.get(f"/recommend/size/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "top" in data["recommendations"]
