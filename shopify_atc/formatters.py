"""Render parsed products as text, JSON, or CSV."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from .client import Product


def _add_url(base_url: str, variant_id: int, quantity: int) -> str:
    return f"{base_url}/cart/add?id={variant_id}&quantity={quantity}"


def _product_url(base_url: str, handle: str) -> str:
    return f"{base_url}/collections/frontpage/products/{handle}"


# Leading characters a spreadsheet may interpret as a formula. Product/variant
# titles come from arbitrary external stores, so untrusted text cells are
# prefixed with a quote to neutralize CSV (formula) injection. See OWASP.
_FORMULA_LEADERS = ("=", "+", "-", "@", "\t", "\r")


def _safe_cell(value: str) -> str:
    return "'" + value if value.startswith(_FORMULA_LEADERS) else value


def render_text(products: List[Product], base_url: str, quantity: int) -> str:
    blocks = []
    for p in products:
        lines = [p.title, _product_url(base_url, p.handle)]
        for v in p.variants:
            price = f" — ${v.price}" if v.price is not None else ""
            lines.append(f"  {v.title}{price}")
            lines.append(f"  {_add_url(base_url, v.id, quantity)}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def render_json(products: List[Product], base_url: str, quantity: int) -> str:
    data = [
        {
            "title": p.title,
            "handle": p.handle,
            "product_url": _product_url(base_url, p.handle),
            "variants": [
                {
                    "id": v.id,
                    "title": v.title,
                    "available": v.available,
                    "price": v.price,
                    "add_url": _add_url(base_url, v.id, quantity),
                }
                for v in p.variants
            ],
        }
        for p in products
    ]
    return json.dumps(data, indent=2)


def render_csv(products: List[Product], base_url: str, quantity: int) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["product_title", "variant_title", "price", "available", "add_url"])
    for p in products:
        for v in p.variants:
            price = v.price if v.price is not None else ""
            writer.writerow(
                [
                    _safe_cell(p.title),
                    _safe_cell(v.title),
                    _safe_cell(price),
                    v.available,
                    _add_url(base_url, v.id, quantity),
                ]
            )
    # Drop csv.writer's trailing line terminator so every renderer returns a
    # string with no trailing newline (the CLI's print() adds exactly one).
    return buf.getvalue().rstrip("\r\n")


_RENDERERS = {"text": render_text, "json": render_json, "csv": render_csv}


def render(products: List[Product], fmt: str, base_url: str, quantity: int) -> str:
    try:
        renderer = _RENDERERS[fmt]
    except KeyError:
        raise ValueError(f"unknown format: {fmt}")
    return renderer(products, base_url, quantity)
