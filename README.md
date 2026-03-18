# Model Registry

## Overview
ML Model Registry for managing models, versions, and artifacts.

Homework assignment for the MLOps course in the Master's program [Machine Learning in a Digital Product](https://www.hse.ru/en/ma/mldp/) (HSE University, Faculty of Computer Science & Avito)

## 🛠️ Installation

### Prerequisites
- Python 3.12.11

### Setup

```bash
# Clone the repository
git clone https://github.com/tlidzhiev/model_registry.git
cd model_registry

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv --python 3.12.11
source .venv/bin/activate

# Install dependencies via uv
uv sync --all-groups

# Install pre-commit
pre-commit install
```

## Running

```bash
# Start the server (default http://localhost:8000)
uv run fastapi dev src/main.py
```

API documentation is available after startup:
- Swagger UI: http://localhost:8000/docs

### Configuration

Environment variables (prefix `REGISTRY_`):

| Variable | Default | Description |
|--------------------------|--------------------------------|-------------------------|
| `REGISTRY_DATABASE_URL`  | `sqlite:///./model_registry.db`| Database connection URL |
| `REGISTRY_STORAGE_PATH`  | `./artifact_storage`           | Artifact storage path   |
| `REGISTRY_API_PREFIX`    | `/api/v1`                       | API prefix             |

Can also be set via `.env` file in the project root.

## Tests

```bash
pytest tests
```

## Project Structure

```
src/
├── main.py                  # FastAPI entrypoint
├── core/
│   ├── config.py            # Configuration (pydantic-settings)
│   └── database.py          # SQLAlchemy engine and sessions
├── api/
│   ├── routes.py            # Router setup
│   ├── models.py            # Model endpoints
│   ├── versions.py          # Version and comparison endpoints
│   └── deps.py              # Dependency injection
├── models/
│   └── models.py            # SQLAlchemy models (MLModel, ModelVersion)
├── schemas/
│   ├── models.py            # Pydantic schemas for models
│   └── versions.py          # Pydantic schemas for versions
├── repositories/
│   ├── model_repository.py  # Model repository
│   └── version_repository.py # Version repository
├── services/
│   ├── model_service.py     # Model business logic
│   └── version_service.py   # Version business logic
└── storage/
    └── backend.py           # Artifact storage abstraction
```

## API

### Models

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/models` | Create a model |
| `GET` | `/api/v1/models` | List models (search, pagination) |
| `GET` | `/api/v1/models/{name}` | Get a model |
| `PATCH` | `/api/v1/models/{name}` | Update description |
| `DELETE` | `/api/v1/models/{name}` | Delete model and all versions |

### Versions

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/models/{name}/versions` | Upload a version (multipart) |
| `GET` | `/api/v1/models/{name}/versions` | List versions (filter by stage) |
| `GET` | `/api/v1/models/{name}/versions/{v}` | Get a version |
| `GET` | `/api/v1/models/{name}/versions/{v}/download` | Download artifact |
| `PATCH` | `/api/v1/models/{name}/versions/{v}/stage` | Update stage |

### Comparison

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/models/{name}/compare?v1=X&v2=Y` | Compare metrics of two versions |

### Lifecycle Stages

`development` → `staging` → `production` → `archived`

Only one version of a model can be in `production` stage — when promoting a new version to production, the previous one is automatically moved to `archived`.
