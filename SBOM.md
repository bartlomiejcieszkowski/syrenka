# Generating SBOM

For SBOM generation we are using CycloneDX:
https://github.com/CycloneDX/cyclonedx-python

Since there is no dedicated support for uv, we are:
1. Exporting uv.lock to requirements.txt
2. Generating sbom from requirements.txt

## Exporting uv to requirements.txt

Commands used are:
```bash
uv export --frozen --format requirements.txt --no-dev -o requirements.txt
uv export --frozen --format requirements.txt --only-dev -o requirements-dev.txt
```

## Generating SBOM from requirements.txt

```bash
uv run --only-dev python -m cyclonedx_py requirements --output-reproducible requirements.txt --output-file syrenka-sbom.json
uv run --only-dev python -m cyclonedx_py requirements --output-reproducible requirements-dev.txt --output-file syrenka-dev-sbom.json
```
