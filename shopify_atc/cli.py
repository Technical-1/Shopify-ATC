"""Command-line interface for shopify-atc."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .client import fetch_products, normalize_url, filter_in_stock, ShopifyError
from .formatters import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shopify-atc",
        description="Generate Shopify add-to-cart permalinks from a store's public products.json.",
    )
    parser.add_argument("store_url", help="Shopify store URL, e.g. https://example.com")
    parser.add_argument("--limit", type=int, default=250, help="Max products to fetch (default: 250)")
    parser.add_argument("--in-stock-only", action="store_true", help="Only include available variants")
    parser.add_argument("--quantity", type=int, default=1, help="Quantity placed in cart links (default: 1)")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="Output format")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    base_url = normalize_url(args.store_url)
    try:
        products = fetch_products(base_url, limit=args.limit)
    except ShopifyError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    if args.in_stock_only:
        products = filter_in_stock(products)
    print(render(products, args.format, base_url, args.quantity))
    return 0


if __name__ == "__main__":
    sys.exit(main())
