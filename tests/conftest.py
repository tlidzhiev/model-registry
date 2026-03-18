import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.storage.backend import LocalStorageBackend, get_storage

engine = create_engine(
    'sqlite:///:memory:',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)

PREFIX = '/api/v1'


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def tmp_storage(tmp_path) -> LocalStorageBackend:
    return LocalStorageBackend(str(tmp_path / 'artifacts'))


@pytest.fixture()
def client(tmp_storage):
    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    def override_storage():
        return tmp_storage

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_storage] = override_storage
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def created_model(client) -> dict:
    resp = client.post(f'{PREFIX}/models', json={'name': 'test_model', 'created_by': 'tester'})
    return resp.json()


def upload_version(
    client, model: str = 'test_model', content: bytes = b'model data', **kwargs
) -> dict:
    files = {'file': ('model.pt', io.BytesIO(content), 'application/octet-stream')}
    data = {'created_by': 'tester', **kwargs}
    return client.post(f'{PREFIX}/models/{model}/versions', files=files, data=data)
