# Avito Backend Course

## Overview

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
