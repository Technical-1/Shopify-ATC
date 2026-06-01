# Design: Docs, Examples & Library API for `shopify-atc`

**Date:** 2026-06-01
**Author:** Jacob Kanfer
**Status:** Approved — ready for implementation plan

## Goal

Make `shopify-atc` approachable for two audiences — CLI users and developers
embedding it as a library — with runnable example files. These ship alongside
the first `v1.0.0` PyPI release. No changes to core fetching/parsing/rendering
logic.

## Background / Current State

- The package (`shopify_atc/`) has three modules: `client.py` (fetch + parse +
  typed errors), `formatters.py` (text/json/csv renderers), `cli.py` (argparse).
- `shopify_atc/__init__.py` currently exports only `__version__`; consumers must
  import from submodules (`shopify_atc.client`, `shopify_atc.formatters`).
- Test coverage is already strong: 29 tests (client 15, formatters 9, cli 5),
  HTTP fully mocked, suite runs offline.
- The README is solid but documents only CLI use, not library use, and has no
  separate runnable examples.

## Non-Goals (YAGNI)

- No changes to `client.py` / `formatters.py` / `cli.py` logic.
- No new runtime dependencies.
- No CONTRIBUTING file, docs site, or generated API reference.
- No version bump — the package is still the unreleased `1.0.0`.

## Design

### Unit 1 — Top-level package exports (`shopify_atc/__init__.py`)

Re-export the public API and declare it explicitly. This is the only behavior
change; it defines the package's supported surface so docs and examples use
clean imports.

```python
"""Generate Shopify add-to-cart permalinks from a store's public products.json."""

from .client import (
    fetch_products,
    filter_in_stock,
    normalize_url,
    Product,
    Variant,
    ShopifyError,
    NetworkError,
    HTTPError,
    NotShopifyError,
)
from .formatters import render

__version__ = "1.0.0"

__all__ = [
    "fetch_products",
    "filter_in_stock",
    "normalize_url",
    "render",
    "Product",
    "Variant",
    "ShopifyError",
    "NetworkError",
    "HTTPError",
    "NotShopifyError",
    "__version__",
]
```

**Depends on:** nothing. **Consumed by:** Units 2, 3, 4.

### Unit 2 — Expand `README.md`

Add the following without disturbing existing sections (How it works,
Features, Tech Stack, Getting Started, Usage, exit codes, Responsible use,
License, Author):

- A **"Use as a Python library"** section after the CLI Usage section, with a
  short annotated snippet: `fetch_products` → `filter_in_stock` → `render`,
  plus iterating `Product`/`Variant` and reading `variant.id`.
- An **"API at a glance"** table listing the exported names (from Unit 1) and a
  one-line description of each.
- A pointer line under Getting Started linking to `examples/`.

### Unit 3 — `examples/` directory (runnable)

Files:

- `examples/README.md` — prerequisites (`pip install shopify-atc`), how to run
  each example, and a responsible-use reminder (use a small `--limit`, public
  data only, not affiliated with Shopify).
- `examples/cli_basic.sh` — text output and `--in-stock-only`. Accepts a store
  URL as `$1` (default `https://www.allbirds.com`) and uses `--limit 5`.
- `examples/cli_export.sh` — writes JSON and CSV to files (`catalog.json`,
  `catalog.csv`); same store-arg/default/limit convention.
- `examples/library_usage.py` — annotated programmatic walkthrough using the
  Unit 1 top-level exports: fetch, filter, render to JSON, and a manual loop
  printing each variant's cart permalink. Accepts an optional store URL argv.

Conventions: shell scripts start with `#!/usr/bin/env bash` and `set -euo
pipefail`, carry the executable bit, and pass `shellcheck`. The Python example
runs under Python 3.9+ and has a `if __name__ == "__main__":` guard.

### Unit 4 — Targeted tests

Follow existing patterns (mock `requests` / monkeypatch `fetch_products`,
`capsys` for output). Fill the genuine CLI gaps and lock the new public API:

- `tests/test_cli.py`:
  - `--quantity N` flows into generated cart links (output contains
    `quantity=N`).
  - `--format json` produces JSON output via `main()`.
  - `--format csv` produces CSV output via `main()`.
  - `--version` prints the version and exits with code 0.
- `tests/test_package_exports.py` (new): asserts each name in
  `shopify_atc.__all__` is importable from the top-level package and that
  `shopify_atc.fetch_products is shopify_atc.client.fetch_products` (guards
  against the re-export silently breaking).

## Data Flow (library usage)

```
caller
  └─ shopify_atc.fetch_products(url, limit) ──▶ List[Product]
       └─ shopify_atc.filter_in_stock(products) ──▶ List[Product]  (optional)
            └─ shopify_atc.render(products, "json"|"csv"|"text", base_url, qty) ──▶ str
       └─ or iterate: for p in products: for v in p.variants: v.id, v.price ...
```

## Error Handling

- Library examples wrap `fetch_products` in `try/except ShopifyError` and print
  the message, mirroring the CLI's behavior, so copy-paste users see the right
  pattern.
- Shell examples rely on `set -euo pipefail`; a failing `shopify-atc` exit code
  aborts the script (documented in `examples/README.md` alongside the exit-code
  meanings).

## Testing / Verification

- `pytest` green: existing 29 + new CLI tests + `test_package_exports`.
- `examples/*.sh` pass `shellcheck` and execute against a real store (manual
  smoke during implementation; not part of the offline unit suite).
- `python -m build` + `twine check dist/*` still PASS (the new `__init__.py`
  exports build cleanly; `examples/` lives in the repo and is not packaged into
  the installed wheel — that is intentional, examples are for the repo).
- Clean-venv install still exposes a working `shopify-atc` CLI and the new
  top-level imports.

## Acceptance Criteria

1. `from shopify_atc import fetch_products, filter_in_stock, render, normalize_url, Product, Variant, ShopifyError` succeeds; `__all__` is defined.
2. README has a "Use as a Python library" section, an API table, and an
   examples pointer; existing sections intact.
3. `examples/` contains `README.md`, `cli_basic.sh`, `cli_export.sh`, and
   `library_usage.py`; shell scripts are executable and shellcheck-clean.
4. New tests pass; full suite green; build + twine check still pass.
5. No core-logic changes, no new runtime deps, version stays `1.0.0`.
```
