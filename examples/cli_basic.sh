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
