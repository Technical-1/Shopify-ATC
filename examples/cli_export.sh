#!/usr/bin/env bash
# Export a store's catalog to JSON and CSV files.
# Usage: ./cli_export.sh [store-url]   (defaults to a public demo store)
set -euo pipefail

STORE="${1:-https://www.allbirds.com}"

shopify-atc "$STORE" --limit 5 --format json > catalog.json
shopify-atc "$STORE" --limit 5 --format csv  > catalog.csv

echo "Wrote catalog.json ($(wc -l < catalog.json) lines) and catalog.csv ($(wc -l < catalog.csv) lines)."
