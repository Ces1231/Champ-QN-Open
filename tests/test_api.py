import io
import json

import yaml


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_status(client):
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["persist_uploads"] is False


def test_index_page_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "CHAMP-QN" in resp.text


def test_assess_json_body(client):
    inventory = {
        "inventory_name": "API Test",
        "assets": [{"id": "host-a", "algorithms": ["RSA-2048", "AES-256-GCM"]}],
    }
    resp = client.post("/api/v1/assess", json=inventory)
    assert resp.status_code == 200
    body = resp.json()
    assert body["asset_count"] == 1
    assert body["finding_count"] == 2


def test_assess_missing_required_field_returns_422(client):
    # Asset objects require an 'id' field.
    inventory = {"assets": [{"algorithms": ["RSA-2048"]}]}
    resp = client.post("/api/v1/assess", json=inventory)
    assert resp.status_code == 422


def test_assess_upload_valid_json(client):
    payload = {"inventory_name": "Upload Test", "assets": [{"id": "a", "algorithms": ["SHA-1"]}]}
    file_bytes = json.dumps(payload).encode()
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.json", io.BytesIO(file_bytes), "application/json")},
    )
    assert resp.status_code == 200
    assert resp.json()["finding_count"] == 1


def test_assess_upload_valid_yaml(client):
    payload = {"inventory_name": "YAML Test", "assets": [{"id": "a", "algorithms": ["AES-256"]}]}
    file_bytes = yaml.safe_dump(payload).encode()
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.yaml", io.BytesIO(file_bytes), "application/x-yaml")},
    )
    assert resp.status_code == 200
    assert resp.json()["finding_count"] == 1


def test_assess_upload_malformed_json_returns_400(client):
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.json", io.BytesIO(b"{not valid json"), "application/json")},
    )
    assert resp.status_code == 400


def test_assess_upload_unsafe_yaml_is_rejected(client):
    # A YAML document using a Python-object constructor tag must be rejected
    # by the safe loader rather than executed or silently accepted.
    unsafe_yaml = b"!!python/object/apply:os.system ['echo pwned']"
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.yaml", io.BytesIO(unsafe_yaml), "application/x-yaml")},
    )
    assert resp.status_code == 400


def test_assess_upload_invalid_file_type_content_is_handled(client):
    # A .txt file with binary garbage is neither valid JSON nor valid YAML.
    resp = client.post(
        "/api/v1/assess/upload",
        files={
            "file": ("notes.txt", io.BytesIO(b"\x00\x01\x02 not structured data"), "text/plain")
        },
    )
    assert resp.status_code in (400, 422)


def test_assess_upload_oversized_input_returns_413(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "max_upload_bytes", 10)
    payload = json.dumps({"assets": [{"id": "a", "algorithms": ["RSA"]}]}).encode()
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.json", io.BytesIO(payload), "application/json")},
    )
    assert resp.status_code == 413


def test_assess_sample(client):
    resp = client.post("/api/v1/assess/sample")
    assert resp.status_code == 200
    body = resp.json()
    assert body["asset_count"] > 0
    assert body["finding_count"] > 0


def test_assess_sample_markdown_format(client):
    resp = client.post("/api/v1/assess/sample?format=markdown")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    assert "CHAMP-QN Crypto Readiness Report" in resp.text


def test_get_sample_returns_raw_inventory(client):
    resp = client.get("/api/v1/sample")
    assert resp.status_code == 200
    body = resp.json()
    assert "assets" in body


def test_no_persistence_of_uploaded_data(client, tmp_path, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "persist_dir", str(tmp_path))
    payload = json.dumps({"assets": [{"id": "a", "algorithms": ["RSA-2048"]}]}).encode()
    resp = client.post(
        "/api/v1/assess/upload",
        files={"file": ("inventory.json", io.BytesIO(payload), "application/json")},
    )
    assert resp.status_code == 200
    # The reference implementation has no write path for uploaded content at
    # all; the configured persistence directory must remain untouched.
    assert list(tmp_path.iterdir()) == []


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
