# Shopify-ATC

![CI](https://github.com/Technical-1/Shopify-ATC/actions/workflows/ci.yml/badge.svg)

A command-line tool that turns any Shopify storefront into a list of direct **add-to-cart permalinks**.

Point it at a store and it reads the shop's public catalog, then prints a ready-to-click `…/cart/add?id=…` link for every product variant — so you can drop an item straight into your cart instead of clicking through the product page. Output comes in human-readable text, JSON, or CSV.

## How it works

Shopify exposes two public, documented features this tool builds on:

- **`/products.json`** — every Shopify store publishes its catalog (products, variants, prices, stock) as JSON. No API key required.
- **`/cart/add?id=<variant_id>` permalinks** — Shopify's built-in [cart permalink](https://help.shopify.com/en/manual/products/details/checkout-link) format adds a specific variant to the cart in one request.

Shopify-ATC fetches the first, then generates the second for each variant.

## Features

- **Add-to-cart links for every variant** — resolves each product's variants and builds a `/cart/add` permalink with a configurable quantity.
- **In-stock filtering** — `--in-stock-only` drops sold-out variants so you only see what you can actually buy.
- **Three output formats** — `text` for reading, `json` for piping into other tools, `csv` for spreadsheets.
- **Clear failure modes** — a non-Shopify URL, an unreachable host, and an HTTP error each produce a distinct message and a distinct exit code, rather than one catch-all "something went wrong".

## Tech Stack

- **Language**: Python 3.9+
- **HTTP**: `requests`
- **CLI**: `argparse` (standard library)
- **Tests**: `pytest` (HTTP mocked — the suite runs fully offline)
- **CI**: GitHub Actions, matrix across Python 3.9–3.13

## Getting Started

### Prerequisites

- Python 3.9 or newer

### Installation

```bash
# From PyPI (recommended)
pip install shopify-atc

# …or isolated with pipx
pipx install shopify-atc
```

This installs a `shopify-atc` command.

Runnable examples (CLI and library) live in [`examples/`](examples/).

For local development from a clone:

```bash
# Editable install with test deps
pip install -e ".[dev]"
```

### Usage

```bash
shopify-atc <store-url> [--limit N] [--in-stock-only] [--quantity N] [--format text|json|csv]
```

| Flag | Default | Description |
|------|---------|-------------|
| `store_url` | — | Store URL, e.g. `https://www.allbirds.com` (scheme optional) |
| `--limit` | `250` | Max products to fetch (Shopify's page maximum) |
| `--in-stock-only` | off | Only include available variants |
| `--quantity` | `1` | Quantity placed in each cart link |
| `--format` | `text` | `text`, `json`, or `csv` |

#### Examples

```bash
# Human-readable, in-stock only
shopify-atc https://www.allbirds.com --in-stock-only

# JSON for scripting
shopify-atc https://www.allbirds.com --limit 50 --format json > catalog.json

# CSV for a spreadsheet
shopify-atc https://www.allbirds.com --format csv > catalog.csv
```

Text output looks like:

```
Trino® Cozy Crew - Heathered Onyx
https://www.allbirds.com/products/trino-cozy-crew-heathered-onyx
  S (W5-7) — $24.00
  https://www.allbirds.com/cart/add?id=39574630924368&quantity=1
```

Exit codes: `0` success · `2` bad arguments or unreachable host · `3` HTTP error from the store · `4` not a Shopify storefront.

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

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run the test suite
pytest
```

## Project Structure

```
Shopify-ATC/
├── shopify_atc/
│   ├── client.py        # fetch + parse products.json into typed dataclasses; typed errors
│   ├── formatters.py    # pure text / json / csv renderers
│   └── cli.py           # argparse + error→exit-code wiring
├── tests/               # offline tests (HTTP mocked)
├── pyproject.toml       # packaging + `shopify-atc` console entry point
└── .github/workflows/   # CI
```

## Responsible use

Shopify-ATC reads only public endpoints and generates links — it does not log in, store payment details, or complete checkouts. It is not affiliated with Shopify. Respect each store's Terms of Service and avoid hammering a storefront with rapid repeated requests.

## License

MIT

## Author

Jacob Kanfer — [GitHub](https://github.com/Technical-1)
