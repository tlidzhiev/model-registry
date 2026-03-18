from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.models import ModelVersion, Stage


class VersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_max_version(self, model_id: int) -> int:
        return (
            self.db.query(func.max(ModelVersion.version))
            .filter(ModelVersion.model_id == model_id)
            .scalar()
        ) or 0

    def create(self, version: ModelVersion) -> ModelVersion:
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list(
        self,
        model_id: int,
        stage: Stage | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ModelVersion]:
        query = self.db.query(ModelVersion).filter(ModelVersion.model_id == model_id)
        if stage:
            query = query.filter(ModelVersion.stage == stage)
        return query.order_by(ModelVersion.version.desc()).offset(offset).limit(limit).all()

    def get(self, model_id: int, version: int) -> ModelVersion | None:
        return (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_id == model_id, ModelVersion.version == version)
            .first()
        )

    def get_production(self, model_id: int) -> ModelVersion | None:
        return (
            self.db.query(ModelVersion)
            .filter(ModelVersion.model_id == model_id, ModelVersion.stage == Stage.production)
            .first()
        )

    def save(self, version: ModelVersion) -> ModelVersion:
        self.db.commit()
        self.db.refresh(version)
        return version
