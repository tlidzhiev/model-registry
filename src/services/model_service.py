import logging

from src.models.models import MLModel
from src.repositories.model_repository import ModelRepository
from src.schemas.models import ModelCreate, ModelUpdate

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self, repo: ModelRepository):
        self.repo = repo

    def create(self, data: ModelCreate) -> MLModel:
        if self.repo.get_by_name(data.name):
            raise ValueError(f"Model '{data.name}' already exists")
        model = MLModel(name=data.name, description=data.description, created_by=data.created_by)
        model = self.repo.create(model)
        logger.info(f"Created model '{data.name}' by {data.created_by}")
        return model

    def get(self, name: str) -> MLModel:
        model = self.repo.get_by_name(name)
        if not model:
            raise KeyError(f"Model '{name}' not found")
        return model

    def list(self, search: str | None = None, limit: int = 20, offset: int = 0) -> list[MLModel]:
        return self.repo.list(search=search, limit=limit, offset=offset)

    def update(self, name: str, data: ModelUpdate) -> MLModel:
        model = self.get(name)
        if data.description is not None:
            model.description = data.description
        return self.repo.save(model)

    async def delete(self, name: str, storage) -> None:
        model = self.get(name)
        await storage.delete_model(name)
        self.repo.delete(model)
        logger.info(f"Deleted model '{name}'")

    def count_versions(self, model_id: int) -> int:
        return self.repo.count_versions(model_id)
