from datetime import datetime

from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str | None = None
    created_by: str = Field(..., min_length=1, max_length=255)


class ModelUpdate(BaseModel):
    description: str | None = None


class ModelResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    versions_count: int = 0

    model_config = {"from_attributes": True}
