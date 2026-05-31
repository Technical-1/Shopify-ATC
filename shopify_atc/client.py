"""Fetch and parse a Shopify store's public products.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


def normalize_url(url: str) -> str:
    """Trim whitespace/trailing slash and default to https:// if no scheme."""
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
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
