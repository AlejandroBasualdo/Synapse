"""
Exporta el spec OpenAPI que genera FastAPI a docs/api/employee-service.yaml,
en la raiz del repo. Se corre a mano cada vez que cambian los endpoints.

Uso:
    python -m scripts.export_openapi
"""
from pathlib import Path

import yaml

from app.main import app

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = ROOT / "docs" / "api" / "employee-service.yaml"


def main():
    schema = app.openapi()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        yaml.dump(schema, f, sort_keys=False, allow_unicode=True)
    print(f"OpenAPI spec exportado a {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
