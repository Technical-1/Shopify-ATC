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
