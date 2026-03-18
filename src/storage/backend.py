import hashlib
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile

from src.core.config import settings


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, model_name: str, version: int, file: UploadFile) -> tuple[str, int, str]:
        """Save artifact. Returns (path, file_size, checksum)."""
        ...

    @abstractmethod
    async def load(self, artifact_path: str) -> Path:
        """Return path to artifact file."""
        ...

    @abstractmethod
    async def delete(self, artifact_path: str) -> None:
        """Delete artifact."""
        ...

    @abstractmethod
    async def delete_model(self, model_name: str) -> None:
        """Delete all artifacts for a model."""
        ...


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str = settings.storage_path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, model_name: str, version: int, file: UploadFile) -> tuple[str, int, str]:
        dir_path = self.base_path / model_name / str(version)
        dir_path.mkdir(parents=True, exist_ok=True)

        filename = file.filename or "artifact"
        file_path = dir_path / filename

        sha256 = hashlib.sha256()
        file_size = 0

        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):
                f.write(chunk)
                sha256.update(chunk)
                file_size += len(chunk)

        relative_path = str(file_path.relative_to(self.base_path))
        return relative_path, file_size, sha256.hexdigest()

    async def load(self, artifact_path: str) -> Path:
        full_path = self.base_path / artifact_path
        if not full_path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")
        return full_path

    async def delete(self, artifact_path: str) -> None:
        full_path = self.base_path / artifact_path
        if full_path.exists():
            os.remove(full_path)
            # Clean up empty parent dirs
            parent = full_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()

    async def delete_model(self, model_name: str) -> None:
        model_dir = self.base_path / model_name
        if model_dir.exists():
            shutil.rmtree(model_dir)


def get_storage() -> StorageBackend:
    return LocalStorageBackend()
