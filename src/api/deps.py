from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.model_repository import ModelRepository
from src.repositories.version_repository import VersionRepository
from src.services.model_service import ModelService
from src.services.version_service import VersionService
from src.storage.backend import StorageBackend, get_storage


def get_model_service(db: Session = Depends(get_db)) -> ModelService:
    return ModelService(ModelRepository(db))


def get_version_service(
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
) -> VersionService:
    return VersionService(ModelRepository(db), VersionRepository(db), storage)
