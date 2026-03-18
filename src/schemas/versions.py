from datetime import datetime

from pydantic import BaseModel

from src.models.models import Stage


class VersionResponse(BaseModel):
    id: int
    model_id: int
    version: int
    description: str | None
    stage: Stage
    file_size: int
    checksum: str
    metrics: dict | None
    parameters: dict | None
    tags: dict | None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StageUpdate(BaseModel):
    stage: Stage


class CompareResponse(BaseModel):
    version_1: VersionResponse
    version_2: VersionResponse
    metrics_diff: dict | None = None
