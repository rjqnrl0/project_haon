import io
import pytest
from PIL import Image


def make_test_jpeg(width=800, height=600) -> bytes:
    img = Image.new("RGB", (width, height), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_upload_body_success(client, auth_headers):
    image_bytes = make_test_jpeg(800, 600)
    files = {"file": ("body.jpg", image_bytes, "image/jpeg")}
    resp = await client.post("/fitting/body/upload", files=files, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    assert data["width"] == 800
    assert data["height"] == 600


@pytest.mark.asyncio
async def test_upload_body_too_small(client, auth_headers):
    image_bytes = make_test_jpeg(320, 240)
    files = {"file": ("body.jpg", image_bytes, "image/jpeg")}
    resp = await client.post("/fitting/body/upload", files=files, headers=auth_headers)
    assert resp.status_code == 422
    assert "640x480" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_clothing_success(client, auth_headers):
    image_bytes = make_test_jpeg(400, 400)
    files = {"file": ("top.jpg", image_bytes, "image/jpeg")}
    data = {"category": "top"}
    resp = await client.post("/fitting/clothing/upload", files=files, data=data, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["category"] == "top"


@pytest.mark.asyncio
async def test_upload_clothing_invalid_category(client, auth_headers):
    image_bytes = make_test_jpeg(400, 400)
    files = {"file": ("shoes.jpg", image_bytes, "image/jpeg")}
    data = {"category": "shoes"}
    resp = await client.post("/fitting/clothing/upload", files=files, data=data, headers=auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_execute_fitting_task_not_found(client, auth_headers):
    import uuid
    resp = await client.post(
        "/fitting/execute",
        json={"body_image_id": str(uuid.uuid4()), "clothing_ids": []},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_full_fitting_flow(client, auth_headers):
    # 1. Upload body
    body_bytes = make_test_jpeg(800, 600)
    files = {"file": ("body.jpg", body_bytes, "image/jpeg")}
    resp = await client.post("/fitting/body/upload", files=files, headers=auth_headers)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    # 2. Execute fitting
    resp = await client.post(
        "/fitting/execute",
        json={"body_image_id": task_id, "clothing_ids": []},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert "result_url" in resp.json()

    # 3. Get result
    resp = await client.get(f"/fitting/result/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_get_result_not_found(client, auth_headers):
    import uuid
    resp = await client.get(f"/fitting/result/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404
