# Tech Stack

## Core Technologies

| Category | Technology | Version | Why this choice |
|----------|------------|---------|-----------------|
| Language | Python | 3.9+ | Ubiquitous for small CLIs; dataclasses and f-strings keep the code compact |
| HTTP client | `requests` | ≥2.25 | Single, well-understood dependency for one GET request |
| CLI parsing | `argparse` | stdlib | No third-party dependency needed for flags, choices, and `--help` |

## Backend

- **Runtime**: Python 3.9+
- **API Style**: Consumes Shopify's public `/products.json` REST endpoint (read-only, no auth)

## Infrastructure

- **Hosting**: N/A — distributed as an installable CLI
- **CI/CD**: GitHub Actions, test matrix across Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Monitoring**: none (local tool)

## Development Tools

- **Package Manager**: pip / pipx
- **Packaging**: setuptools via `pyproject.toml` (dynamic version, console entry point)
- **Testing**: `pytest`, with `requests.get` mocked so the suite runs offline

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | Fetch the store's `products.json` |
| `pytest` | Test runner (dev extra only) |
