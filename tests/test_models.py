from tests.conftest import PREFIX


def test_create_model(client) -> None:
    resp = client.post(f"{PREFIX}/models", json={
        "name": "test_model",
        "description": "A test model",
        "created_by": "tester",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test_model"
    assert data["created_by"] == "tester"
    assert data["versions_count"] == 0


def test_create_duplicate_model(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "dup", "created_by": "a"})
    resp = client.post(f"{PREFIX}/models", json={"name": "dup", "created_by": "b"})
    assert resp.status_code == 409


def test_list_models(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "model_a", "created_by": "a"})
    client.post(f"{PREFIX}/models", json={"name": "model_b", "created_by": "b"})
    resp = client.get(f"{PREFIX}/models")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_search_models(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "sft_model", "created_by": "a"})
    client.post(f"{PREFIX}/models", json={"name": "rl_model", "created_by": "b"})
    resp = client.get(f"{PREFIX}/models", params={"search": "sft"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "sft_model"


def test_get_model(client, created_model) -> None:
    resp = client.get(f"{PREFIX}/models/test_model")
    assert resp.status_code == 200
    assert resp.json()["name"] == "test_model"


def test_get_model_not_found(client) -> None:
    resp = client.get(f"{PREFIX}/models/nonexistent")
    assert resp.status_code == 404


def test_update_model(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "upd", "created_by": "a"})
    resp = client.patch(f"{PREFIX}/models/upd", json={"description": "updated"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated"


def test_delete_model(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "del_me", "created_by": "a"})
    resp = client.delete(f"{PREFIX}/models/del_me")
    assert resp.status_code == 204
    assert client.get(f"{PREFIX}/models/del_me").status_code == 404


def test_invalid_model_name(client) -> None:
    resp = client.post(f"{PREFIX}/models", json={"name": "bad name!", "created_by": "a"})
    assert resp.status_code == 422
