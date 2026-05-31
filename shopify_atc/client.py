"""Fetch and parse a Shopify store's public products.json."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

import requests

DEFAULT_TIMEOUT: int = 15


class ShopifyError(Exception):
    """Base error; carries the process exit code to use."""

    exit_code = 1


class NetworkError(ShopifyError):
    exit_code = 2


class HTTPError(ShopifyError):
    exit_code = 3


class NotShopifyError(ShopifyError):
    exit_code = 4


def normalize_url(url: str) -> str:
    """Trim whitespace/trailing slash and default to https:// if no scheme."""
    url = url.strip().rstrip("/")
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


@dataclass
class Variant:
    id: int
    title: str
    available: bool
    price: Optional[str] = None


@dataclass
class Product:
    title: str
    handle: str
    variants: List[Variant] = field(default_factory=list)


def _parse_product(raw: dict) -> Product:
    variants = [
        Variant(
            id=v["id"],
            title=v.get("title", ""),
            available=bool(v.get("available", False)),
            price=v.get("price"),
        )
        for v in raw.get("variants", [])
    ]
    return Product(
        title=raw.get("title", ""),
        handle=raw.get("handle", ""),
        variants=variants,
    )


def fetch_products(url: str, limit: int = 250, *, timeout: int = DEFAULT_TIMEOUT) -> List[Product]:
    base = normalize_url(url)
    endpoint = f"{base}/products.json?limit={limit}"
    try:
        resp = requests.get(endpoint, headers={"cache-control": "no-store"}, timeout=timeout)
    except requests.RequestException as exc:
        raise NetworkError(f"Could not reach {base}: {exc}") from exc
    if resp.status_code != 200:
        raise HTTPError(f"Store returned HTTP {resp.status_code}")
    try:
        raw_products = resp.json()["products"]
        return [_parse_product(p) for p in raw_products]
    except (ValueError, KeyError, TypeError) as exc:
        raise NotShopifyError("Not a Shopify storefront (no products.json)") from exc


def filter_in_stock(products: List[Product]) -> List[Product]:
    """Return products keeping only available variants; drop products left empty."""
    result: List[Product] = []
    for p in products:
        available = [v for v in p.variants if v.available]
        if available:
            result.append(replace(p, variants=available))
    return result
