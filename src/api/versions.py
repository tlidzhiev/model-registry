from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from src.models.models import Stage
from src.schemas.versions import CompareResponse, StageUpdate, VersionResponse
from src.services.version_service import VersionService
from src.storage.backend import StorageBackend, get_storage

from .deps import get_version_service

router = APIRouter(tags=["versions"])


@router.post("/{name}/versions", response_model=VersionResponse, status_code=201)
async def create_version(
    name: str,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    metrics: str | None = Form(None),
    parameters: str | None = Form(None),
    tags: str | None = Form(None),
    created_by: str = Form(...),
    service: VersionService = Depends(get_version_service),
) -> VersionResponse:
    try:
        version = await service.create(
            model_name=name,
            file=file,
            created_by=created_by,
            description=description,
            metrics=metrics,
            parameters=parameters,
            tags=tags,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return VersionResponse.model_validate(version)


@router.get("/{name}/versions", response_model=list[VersionResponse])
def list_versions(
    name: str,
    stage: Stage | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: VersionService = Depends(get_version_service),
) -> list[VersionResponse]:
    try:
        versions = service.list(name, stage=stage, limit=limit, offset=offset)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [VersionResponse.model_validate(v) for v in versions]


@router.get("/{name}/versions/{version}", response_model=VersionResponse)
def get_version(name: str, version: int, service: VersionService = Depends(get_version_service)) -> VersionResponse:
    try:
        v = service.get(name, version)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return VersionResponse.model_validate(v)


@router.get("/{name}/versions/{version}/download")
async def download_version(
    name: str,
    version: int,
    service: VersionService = Depends(get_version_service),
    storage: StorageBackend = Depends(get_storage),
) -> FileResponse:
    try:
        v = service.get(name, version)
        path = await storage.load(v.artifact_path)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return FileResponse(path, filename=path.name)


@router.patch("/{name}/versions/{version}/stage", response_model=VersionResponse)
def update_stage(
    name: str,
    version: int,
    data: StageUpdate,
    service: VersionService = Depends(get_version_service),
) -> VersionResponse:
    try:
        v = service.update_stage(name, version, data.stage)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return VersionResponse.model_validate(v)


@router.get("/{name}/compare", response_model=CompareResponse)
def compare_versions(
    name: str,
    v1: int = Query(...),
    v2: int = Query(...),
    service: VersionService = Depends(get_version_service),
) -> CompareResponse:
    try:
        ver1, ver2, metrics_diff = service.compare(name, v1, v2)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return CompareResponse(
        version_1=VersionResponse.model_validate(ver1),
        version_2=VersionResponse.model_validate(ver2),
        metrics_diff=metrics_diff,
    )
