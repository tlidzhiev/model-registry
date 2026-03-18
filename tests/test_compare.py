import pytest

from tests.conftest import PREFIX, upload_version


def test_compare_versions(client) -> None:
    client.post(f"{PREFIX}/models", json={"name": "cmp", "created_by": "a"})
    upload_version(client, model="cmp", content=b"v1", metrics='{"accuracy": 0.90, "loss": 0.5}')
    upload_version(client, model="cmp", content=b"v2", metrics='{"accuracy": 0.95, "loss": 0.3}')

    resp = client.get(f"{PREFIX}/models/cmp/compare", params={"v1": 1, "v2": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["metrics_diff"]["accuracy"]["diff"] == pytest.approx(0.05)
    assert data["metrics_diff"]["loss"]["diff"] == pytest.approx(-0.2)
