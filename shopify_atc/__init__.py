"""Generate Shopify add-to-cart permalinks from a store's public products.json."""

from .client import (
    fetch_products,
    filter_in_stock,
    normalize_url,
    Product,
    Variant,
    ShopifyError,
    NetworkError,
    HTTPError,
    NotShopifyError,
)
from .formatters import render

__version__ = "1.0.0"

__all__ = [
    "fetch_products",
    "filter_in_stock",
    "normalize_url",
    "render",
    "Product",
    "Variant",
    "ShopifyError",
    "NetworkError",
    "HTTPError",
    "NotShopifyError",
    "__version__",
]
