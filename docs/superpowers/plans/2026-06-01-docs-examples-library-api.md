# Docs, Examples & Library API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `shopify-atc` usable as both a CLI and an importable library, with runnable examples and docs, ahead of the v1.0.0 release.

**Architecture:** Add top-level re-exports in `__init__.py` (the only code change), lock them with tests, fill CLI test gaps, expand the README, and add a runnable `examples/` directory. No changes to `client.py`/`formatters.py`/`cli.py` logic.

**Tech Stack:** Python 3.9+, pytest (HTTP mocked), bash example scripts, argparse CLI.

---

## File Structure

- Modify: `shopify_atc/__init__.py` — re-export public API + `__all__` (Task 1).
- Create: `tests/test_package_exports.py` — lock the public API (Task 1).
- Modify: `tests/test_cli.py` — add `--quantity`, `--format json/csv`, `--version` tests (Task 2).
- Modify: `README.md` — add library section, API table, examples pointer (Task 3).
- Create: `examples/README.md`, `examples/cli_basic.sh`, `examples/cli_export.sh`, `examples/library_usage.py` (Task 4).

**Ordering:** Task 1 (exports) first — Tasks 3 and 4 import the top-level names it defines. Task 2 is independent but small; do it after Task 1. Each task commits independently.

**Test environment note:** Homebrew Python is externally managed (PEP 668). Run the suite in a venv:
```bash
python3 -m venv /tmp/atc-dev && /tmp/atc-dev/bin/pip install -e ".[dev]"
```
Then use `/tmp/atc-dev/bin/pytest` as the `pytest` command throughout. Clean up `/tmp/atc-dev` when done.

---

### Task 1: Top-level package exports

**Files:**
- Modify: `shopify_atc/__init__.py`
- Create: `tests/test_package_exports.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_package_exports.py`:

```python
"""Lock the public API re-exported from the top-level package."""

import shopify_atc


def test_all_names_are_importable():
    for name in shopify_atc.__all__:
        assert hasattr(shopify_atc, name), f"{name} missing from package"


def test_reexports_are_the_same_objects():
    from shopify_atc import client, formatters

    assert shopify_atc.fetch_products is client.fetch_products
    assert shopify_atc.filter_in_stock is client.filter_in_stock
    assert shopify_atc.normalize_url is client.normalize_url
    assert shopify_atc.render is formatters.render
    assert shopify_atc.Product is client.Product
    assert shopify_atc.Variant is client.Variant
    assert shopify_atc.ShopifyError is client.ShopifyError


def test_all_lists_expected_public_api():
    assert set(shopify_atc.__all__) == {
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
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/tmp/atc-dev/bin/pytest tests/test_package_exports.py -v`
Expected: FAIL — `AttributeError: module 'shopify_atc' has no attribute 'fetch_products'` (and `__all__` not defined).

- [ ] **Step 3: Write the implementation**

Replace the entire contents of `shopify_atc/__init__.py` with:

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

- [ ] **Step 4: Run tests to verify they pass**

Run: `/tmp/atc-dev/bin/pytest tests/test_package_exports.py -v`
Expected: PASS (3 tests).

Then run the full suite to confirm no import cycle broke anything:
Run: `/tmp/atc-dev/bin/pytest -q`
Expected: PASS (32 tests — the prior 29 + 3 new).

- [ ] **Step 5: Commit**

```bash
git add shopify_atc/__init__.py tests/test_package_exports.py
git commit -m "feat: re-export public API from top-level package

Generated with [Claude Code](https://claude.ai/code)
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 2: Fill CLI test gaps

**Files:**
- Modify: `tests/test_cli.py`

Context: `tests/test_cli.py` already monkeypatches `fetch_products` and uses `capsys`. Read the top of the file first to reuse its existing imports and any sample-data fixture/helper. The CLI entry point is `shopify_atc.cli.main(argv)`, which returns an int exit code and prints to stdout. `main` calls `fetch_products(base_url, limit=...)` then `render(products, fmt, base_url, quantity)`.

- [ ] **Step 1: Write the failing tests**

Append these to `tests/test_cli.py`. They build a small product list directly (no HTTP) by monkeypatching `fetch_products` in the `cli` module. If the existing file already defines a sample-products helper, reuse it instead of redefining `_sample`.

```python
from shopify_atc.client import Product, Variant


def _sample():
    return [Product(title="Tee", handle="tee", variants=[Variant(id=111, title="S", available=True, price="20.00")])]


def test_main_quantity_flows_into_cart_links(monkeypatch, capsys):
    from shopify_atc import cli

    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--quantity", "3"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "quantity=3" in out


def test_main_format_json_emits_json(monkeypatch, capsys):
    import json
    from shopify_atc import cli

    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--format", "json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(out)
    assert data[0]["handle"] == "tee"
    assert data[0]["variants"][0]["add_url"].endswith("quantity=1")


def test_main_format_csv_emits_header(monkeypatch, capsys):
    from shopify_atc import cli

    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--format", "csv"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.splitlines()[0] == "product_title,variant_title,price,available,add_url"


def test_main_version_exits_zero(capsys):
    from shopify_atc import cli
    import shopify_atc

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert shopify_atc.__version__ in out
```

Note: `--version` uses argparse's `action="version"`, which prints to stdout and raises `SystemExit(0)` — hence `pytest.raises(SystemExit)`. Ensure `import pytest` exists at the top of the file (add it if missing).

- [ ] **Step 2: Run tests to verify they fail or pass correctly**

Run: `/tmp/atc-dev/bin/pytest tests/test_cli.py -v`
Expected: The 4 new tests are collected and PASS (they exercise existing behavior — there is no new implementation code, this task closes coverage gaps). If any fail, the failure reveals a real bug; stop and report it rather than altering the test to pass.

- [ ] **Step 3: Run the full suite**

Run: `/tmp/atc-dev/bin/pytest -q`
Expected: PASS (36 tests — 32 + 4 new).

- [ ] **Step 4: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: cover CLI --quantity, --format json/csv, and --version

Generated with [Claude Code](https://claude.ai/code)
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 3: Expand the README

**Files:**
- Modify: `README.md`

Context: The README has these sections in order: title/badge, intro, How it works, Features, Tech Stack, Getting Started (Prerequisites, Installation, Usage with a flags table and Examples), exit codes line, Development, Project Structure, Responsible use, License, Author. Do NOT alter existing sections except as specified. Read the file first to find exact insertion points.

- [ ] **Step 1: Add a "Use as a Python library" section**

Insert this block immediately AFTER the CLI "Examples" subsection (the block ending with the text-output example and the `Exit codes:` line) and BEFORE the `## Development` heading:

````markdown
## Use as a Python library

Everything the CLI does is available programmatically. The key names are
re-exported from the top-level package:

```python
import shopify_atc

base = shopify_atc.normalize_url("www.allbirds.com")  # -> https://www.allbirds.com

try:
    products = shopify_atc.fetch_products(base, limit=5)
except shopify_atc.ShopifyError as exc:
    raise SystemExit(str(exc))

products = shopify_atc.filter_in_stock(products)  # optional: drop sold-out variants

# Render to any format the CLI supports:
print(shopify_atc.render(products, "json", base, quantity=1))

# …or work with the dataclasses directly:
for product in products:
    for variant in product.variants:
        print(variant.title, variant.price, f"{base}/cart/add?id={variant.id}&quantity=1")
```

### API at a glance

| Name | Description |
|------|-------------|
| `fetch_products(url, limit=250, *, timeout=15)` | Fetch + parse a store's `products.json` into `Product` objects. Raises a `ShopifyError` subclass on failure. |
| `filter_in_stock(products)` | Return products keeping only available variants; drops products left empty. |
| `normalize_url(url)` | Trim whitespace/trailing slash and default to `https://` if no scheme. |
| `render(products, fmt, base_url, quantity)` | Render products as `"text"`, `"json"`, or `"csv"`. |
| `Product`, `Variant` | Dataclasses describing a product and its variants. |
| `ShopifyError` | Base exception; subclasses `NetworkError` (exit 2), `HTTPError` (exit 3), `NotShopifyError` (exit 4). |
````

- [ ] **Step 2: Add an examples pointer**

In the `### Installation` section, immediately after the line `This installs a `shopify-atc` command.`, add this line:

```markdown

Runnable examples (CLI and library) live in [`examples/`](examples/).
```

- [ ] **Step 3: Verify the edits**

Run: `grep -n "Use as a Python library" README.md` → expect one match.
Run: `grep -n "examples/" README.md` → expect at least one match (the pointer).
Run: `grep -c "## Development" README.md` → expect `1` (unchanged, not duplicated).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add library usage section, API table, and examples pointer

Generated with [Claude Code](https://claude.ai/code)
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 4: Add the examples/ directory

**Files:**
- Create: `examples/README.md`
- Create: `examples/cli_basic.sh`
- Create: `examples/cli_export.sh`
- Create: `examples/library_usage.py`

- [ ] **Step 1: Create `examples/cli_basic.sh`**

```bash
#!/usr/bin/env bash
# Basic CLI usage: list add-to-cart links as human-readable text.
# Usage: ./cli_basic.sh [store-url]   (defaults to a public demo store)
set -euo pipefail

STORE="${1:-https://www.allbirds.com}"

echo "# All variants (text), capped at 5 products:"
shopify-atc "$STORE" --limit 5

echo
echo "# In-stock variants only:"
shopify-atc "$STORE" --limit 5 --in-stock-only
```

- [ ] **Step 2: Create `examples/cli_export.sh`**

```bash
#!/usr/bin/env bash
# Export a store's catalog to JSON and CSV files.
# Usage: ./cli_export.sh [store-url]   (defaults to a public demo store)
set -euo pipefail

STORE="${1:-https://www.allbirds.com}"

shopify-atc "$STORE" --limit 5 --format json > catalog.json
shopify-atc "$STORE" --limit 5 --format csv  > catalog.csv

echo "Wrote catalog.json ($(wc -l < catalog.json) lines) and catalog.csv ($(wc -l < catalog.csv) lines)."
```

- [ ] **Step 3: Create `examples/library_usage.py`**

```python
#!/usr/bin/env python3
"""Use shopify-atc as a library: fetch, filter, render, and build cart links.

Run:  python library_usage.py [store-url]
"""

from __future__ import annotations

import sys

import shopify_atc


def main(argv: list[str]) -> int:
    store = argv[1] if len(argv) > 1 else "https://www.allbirds.com"
    base = shopify_atc.normalize_url(store)

    try:
        products = shopify_atc.fetch_products(base, limit=5)
    except shopify_atc.ShopifyError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code

    products = shopify_atc.filter_in_stock(products)
    print(f"{len(products)} product(s) with in-stock variants from {base}\n")

    # Work with the dataclasses directly:
    for product in products:
        print(product.title)
        for variant in product.variants:
            price = f"${variant.price}" if variant.price is not None else "n/a"
            cart = f"{base}/cart/add?id={variant.id}&quantity=1"
            print(f"  {variant.title} — {price} — {cart}")
        print()

    # Or render to JSON exactly like the CLI's --format json:
    print("--- JSON render ---")
    print(shopify_atc.render(products, "json", base, quantity=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Create `examples/README.md`**

````markdown
# Examples

Runnable examples for the `shopify-atc` CLI and Python library.

## Prerequisites

```bash
pip install shopify-atc
```

Each script accepts a store URL as its first argument and defaults to a public
store. Keep `--limit` small and avoid rapid repeated runs — these hit a live
storefront's public `products.json`. This tool reads only public endpoints and
is not affiliated with Shopify.

## CLI examples

```bash
./cli_basic.sh                       # text output, default store
./cli_basic.sh https://example.com   # against your own store
./cli_export.sh                      # writes catalog.json and catalog.csv
```

If a script's `shopify-atc` call fails (e.g. the URL isn't a Shopify store),
the script aborts with the CLI's exit code: `2` bad args/unreachable host,
`3` HTTP error, `4` not a Shopify storefront.

## Library example

```bash
python library_usage.py                       # default store
python library_usage.py https://example.com   # your own store
```

Shows `fetch_products` → `filter_in_stock` → iterating `Product`/`Variant`
objects and `render(..., "json", ...)`.
````

- [ ] **Step 5: Make the shell scripts executable**

Run: `chmod +x examples/cli_basic.sh examples/cli_export.sh`

- [ ] **Step 6: Verify the scripts are well-formed**

Run shellcheck if available:
`shellcheck examples/cli_basic.sh examples/cli_export.sh`
Expected: no warnings. (If `shellcheck` is not installed, skip — note it was skipped.)

Verify the Python example imports and compiles (does not hit the network):
Run: `/tmp/atc-dev/bin/python -c "import py_compile; py_compile.compile('examples/library_usage.py', doraise=True); print('ok')"`
Expected: `ok`

Confirm executable bits:
Run: `test -x examples/cli_basic.sh && test -x examples/cli_export.sh && echo "executable ok"`
Expected: `executable ok`

- [ ] **Step 7: Commit**

```bash
git add examples/
git commit -m "docs: add runnable CLI and library examples

Generated with [Claude Code](https://claude.ai/code)
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 5: Final verification (build + full suite)

**Files:** none (verification only)

- [ ] **Step 1: Run the full test suite**

Run: `/tmp/atc-dev/bin/pytest -q`
Expected: PASS (36 tests).

- [ ] **Step 2: Build and validate the distribution**

```bash
rm -rf dist build shopify_atc.egg-info
/tmp/atc-dev/bin/python -m build
/tmp/atc-dev/bin/twine check dist/*
```
Expected: build succeeds; `twine check` PASSED for wheel + sdist.

- [ ] **Step 3: Confirm top-level imports in a clean venv**

```bash
rm -rf /tmp/atc-verify
python3 -m venv /tmp/atc-verify
/tmp/atc-verify/bin/pip install --quiet dist/*.whl
/tmp/atc-verify/bin/python -c "from shopify_atc import fetch_products, filter_in_stock, render, Product, Variant, ShopifyError; print('imports ok')"
/tmp/atc-verify/bin/shopify-atc --version
```
Expected: `imports ok` then `shopify-atc 1.0.0`.

- [ ] **Step 4: Clean up**

Run: `rm -rf /tmp/atc-dev /tmp/atc-verify dist build shopify_atc.egg-info`
Expected: clean exit. (Artifacts are git-ignored; nothing to commit.)

---

## Self-Review (completed by plan author)

**Spec coverage:**
- Unit 1 (top-level exports) → Task 1. ✅
- Unit 2 (README library section + API table + examples pointer) → Task 3. ✅
- Unit 3 (examples/ dir: README, cli_basic.sh, cli_export.sh, library_usage.py) → Task 4. ✅
- Unit 4 (CLI tests + test_package_exports) → Task 1 (exports test) + Task 2 (CLI tests). ✅
- Verification (build, twine, clean install) → Task 5. ✅

**Type/name consistency:** Export names in Task 1's `__init__.py`, Task 1's test `__all__` set, Task 3's API table, and Task 4's `library_usage.py` all use the same names (`fetch_products`, `filter_in_stock`, `normalize_url`, `render`, `Product`, `Variant`, `ShopifyError`, `NetworkError`, `HTTPError`, `NotShopifyError`). Test counts are cumulative and consistent (29 → 32 → 36).

## Acceptance Criteria (from spec)

1. ✅ Top-level imports work; `__all__` defined (Task 1).
2. ✅ README has library section, API table, examples pointer; existing sections intact (Task 3).
3. ✅ examples/ has all four files; shell scripts executable and shellcheck-clean (Task 4).
4. ✅ New tests pass; full suite green; build + twine check pass (Tasks 1, 2, 5).
5. ✅ No core-logic changes, no new runtime deps, version stays 1.0.0.
