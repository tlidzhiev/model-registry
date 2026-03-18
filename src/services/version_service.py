import json
import logging

from fastapi import UploadFile

from src.models.models import MLModel, ModelVersion, Stage
from src.repositories.model_repository import ModelRepository
from src.repositories.version_repository import VersionRepository
from src.storage.backend import StorageBackend

logger = logging.getLogger(__name__)


class VersionService:
    def __init__(
        self,
        model_repo: ModelRepository,
        version_repo: VersionRepository,
        storage: StorageBackend,
    ):
        self.model_repo = model_repo
        self.version_repo = version_repo
        self.storage = storage

    def _get_model_or_raise(self, model_name: str) -> MLModel:
        model = self.model_repo.get_by_name(model_name)
        if not model:
            raise KeyError(f"Model '{model_name}' not found")
        return model

    async def create(
        self,
        model_name: str,
        file: UploadFile,
        created_by: str,
        description: str | None = None,
        metrics: str | None = None,
        parameters: str | None = None,
        tags: str | None = None,
    ) -> ModelVersion:
        model = self._get_model_or_raise(model_name)
        new_version = self.version_repo.get_max_version(model.id) + 1

        artifact_path, file_size, checksum = await self.storage.save(model_name, new_version, file)

        version = ModelVersion(
            model_id=model.id,
            version=new_version,
            description=description,
            artifact_path=artifact_path,
            file_size=file_size,
            checksum=checksum,
            metrics=json.loads(metrics) if metrics else None,
            parameters=json.loads(parameters) if parameters else None,
            tags=json.loads(tags) if tags else None,
            created_by=created_by,
        )
        version = self.version_repo.create(version)
        logger.info(f"Created version {new_version} for model '{model_name}'")
        return version

    def list(
        self,
        model_name: str,
        stage: Stage | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ModelVersion]:
        model = self._get_model_or_raise(model_name)
        return self.version_repo.list(model.id, stage=stage, limit=limit, offset=offset)

    def get(self, model_name: str, version: int) -> ModelVersion:
        model = self._get_model_or_raise(model_name)
        v = self.version_repo.get(model.id, version)
        if not v:
            raise KeyError(f"Version {version} of model '{model_name}' not found")
        return v

    def update_stage(self, model_name: str, version: int, stage: Stage) -> ModelVersion:
        model = self._get_model_or_raise(model_name)
        v = self.version_repo.get(model.id, version)
        if not v:
            raise KeyError(f"Version {version} of model '{model_name}' not found")

        if stage == Stage.production:
            current_prod = self.version_repo.get_production(model.id)
            if current_prod and current_prod.id != v.id:
                current_prod.stage = Stage.archived
                self.version_repo.save(current_prod)
                logger.info(
                    f"Demoted version {current_prod.version} of '{model_name}' from production to archived"
                )

        v.stage = stage
        v = self.version_repo.save(v)
        logger.info(f"Updated version {version} of '{model_name}' to stage '{stage.value}'")
        return v

    def compare(
        self, model_name: str, v1: int, v2: int
    ) -> tuple[ModelVersion, ModelVersion, dict | None]:
        ver1 = self.get(model_name, v1)
        ver2 = self.get(model_name, v2)

        metrics_diff = None
        if ver1.metrics and ver2.metrics:
            all_keys = set(ver1.metrics.keys()) | set(ver2.metrics.keys())
            metrics_diff = {
                key: {
                    'version_1': ver1.metrics.get(key),
                    'version_2': ver2.metrics.get(key),
                    'diff': (
                        round(ver2.metrics[key] - ver1.metrics[key], 6)
                        if isinstance(ver1.metrics.get(key), (int, float))
                        and isinstance(ver2.metrics.get(key), (int, float))
                        else None
                    ),
                }
                for key in all_keys
            }

        return ver1, ver2, metrics_diff
