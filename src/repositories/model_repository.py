from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.models import MLModel, ModelVersion


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> MLModel | None:
        return self.db.query(MLModel).filter(MLModel.name == name).first()

    def create(self, model: MLModel) -> MLModel:
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list(
        self,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MLModel]:
        query = self.db.query(MLModel)
        if search:
            query = query.filter(MLModel.name.ilike(f"%{search}%"))
        return query.order_by(MLModel.created_at.desc()).offset(offset).limit(limit).all()

    def save(self, model: MLModel) -> MLModel:
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model: MLModel) -> None:
        self.db.delete(model)
        self.db.commit()

    def count_versions(self, model_id: int) -> int:
        return (
            self.db.query(func.count(ModelVersion.id))
            .filter(ModelVersion.model_id == model_id)
            .scalar()
        ) or 0
