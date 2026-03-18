from tests.conftest import PREFIX, upload_version


def test_create_version(client, created_model) -> None:
    resp = upload_version(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["version"] == 1
    assert data["stage"] == "development"
    assert data["file_size"] == len(b"model data")
    assert len(data["checksum"]) == 64


def test_auto_increment_version(client, created_model) -> None:
    upload_version(client)
    resp = upload_version(client, content=b"v2")
    assert resp.json()["version"] == 2


def test_version_with_metrics(client, created_model) -> None:
    resp = upload_version(
        client,
        metrics='{"accuracy": 0.95, "f1": 0.92}',
        parameters='{"lr": 0.001}',
        tags='{"framework": "pytorch"}',
    )
    data = resp.json()
    assert data["metrics"]["accuracy"] == 0.95
    assert data["parameters"]["lr"] == 0.001
    assert data["tags"]["framework"] == "pytorch"


def test_list_versions(client, created_model) -> None:
    upload_version(client)
    upload_version(client, content=b"v2")
    resp = client.get(f"{PREFIX}/models/test_model/versions")
    assert len(resp.json()) == 2


def test_filter_versions_by_stage(client, created_model) -> None:
    upload_version(client)
    resp = client.get(f"{PREFIX}/models/test_model/versions", params={"stage": "production"})
    assert len(resp.json()) == 0


def test_download_version(client, created_model) -> None:
    content = b"model binary data"
    upload_version(client, content=content)
    resp = client.get(f"{PREFIX}/models/test_model/versions/1/download")
    assert resp.status_code == 200
    assert resp.content == content


def test_update_stage(client, created_model) -> None:
    upload_version(client)
    resp = client.patch(
        f"{PREFIX}/models/test_model/versions/1/stage",
        json={"stage": "production"},
    )
    assert resp.status_code == 200
    assert resp.json()["stage"] == "production"


def test_production_exclusivity(client, created_model) -> None:
    upload_version(client)
    upload_version(client, content=b"v2")

    client.patch(f"{PREFIX}/models/test_model/versions/1/stage", json={"stage": "production"})
    client.patch(f"{PREFIX}/models/test_model/versions/2/stage", json={"stage": "production"})

    v1 = client.get(f"{PREFIX}/models/test_model/versions/1").json()
    v2 = client.get(f"{PREFIX}/models/test_model/versions/2").json()
    assert v1["stage"] == "archived"
    assert v2["stage"] == "production"


def test_version_not_found(client, created_model) -> None:
    resp = client.get(f"{PREFIX}/models/test_model/versions/999")
    assert resp.status_code == 404
