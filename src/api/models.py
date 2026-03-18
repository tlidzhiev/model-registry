from fastapi import APIRouter, Depends, HTTPException, Query

from src.schemas.models import ModelCreate, ModelResponse, ModelUpdate
from src.services.model_service import ModelService
from src.storage.backend import StorageBackend, get_storage

from .deps import get_model_service

router = APIRouter(tags=["models"])


@router.post("", response_model=ModelResponse, status_code=201)
def create_model(data: ModelCreate, service: ModelService = Depends(get_model_service)) -> ModelResponse:
    try:
        model = service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
        versions_count=0,
    )


@router.get("", response_model=list[ModelResponse])
def list_models(
    search: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ModelService = Depends(get_model_service),
) -> list[ModelResponse]:
    models = service.list(search=search, limit=limit, offset=offset)
    return [
        ModelResponse(
            id=m.id,
            name=m.name,
            description=m.description,
            created_by=m.created_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
            versions_count=service.count_versions(m.id),
        )
        for m in models
    ]


@router.get("/{name}", response_model=ModelResponse)
def get_model(name: str, service: ModelService = Depends(get_model_service)) -> ModelResponse:
    try:
        model = service.get(name)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
        versions_count=service.count_versions(model.id),
    )


@router.patch("/{name}", response_model=ModelResponse)
def update_model(
    name: str, data: ModelUpdate, service: ModelService = Depends(get_model_service)
) -> ModelResponse:
    try:
        model = service.update(name, data)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
        versions_count=service.count_versions(model.id),
    )


@router.delete("/{name}", status_code=204)
async def delete_model(
    name: str,
    service: ModelService = Depends(get_model_service),
    storage: StorageBackend = Depends(get_storage),
) -> None:
    try:
        await service.delete(name, storage)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
