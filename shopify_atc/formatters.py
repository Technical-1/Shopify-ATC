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


def render_text(products: List[Product], base_url: str, quantity: int) -> str:
    blocks = []
    for p in products:
        lines = [p.title, _product_url(base_url, p.handle)]
        for v in p.variants:
            price = f" — ${v.price}" if v.price else ""
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
            writer.writerow([p.title, v.title, v.price or "", v.available, _add_url(base_url, v.id, quantity)])
    return buf.getvalue()


_RENDERERS = {"text": render_text, "json": render_json, "csv": render_csv}


def render(products: List[Product], fmt: str, base_url: str, quantity: int) -> str:
    try:
        renderer = _RENDERERS[fmt]
    except KeyError:
        raise ValueError(f"unknown format: {fmt}")
    return renderer(products, base_url, quantity)
