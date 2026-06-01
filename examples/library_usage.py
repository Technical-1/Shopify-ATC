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
