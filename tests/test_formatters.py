import json

from shopify_atc.client import Product, Variant
from shopify_atc.formatters import render

PRODUCTS = [
    Product(
        title="Cool Shirt",
        handle="cool-shirt",
        variants=[Variant(id=111, title="Small", available=True, price="20.00")],
    )
]
BASE = "https://shop.example"


def test_render_text_includes_titles_and_links():
    out = render(PRODUCTS, "text", BASE, 1)
    assert "Cool Shirt" in out
    assert "https://shop.example/collections/frontpage/products/cool-shirt" in out
    assert "https://shop.example/cart/add?id=111&quantity=1" in out


def test_render_json_emits_add_url_with_quantity():
    out = render(PRODUCTS, "json", BASE, 2)
    data = json.loads(out)
    assert data[0]["title"] == "Cool Shirt"
    assert data[0]["variants"][0]["add_url"] == "https://shop.example/cart/add?id=111&quantity=2"


def test_render_csv_has_header_and_row():
    out = render(PRODUCTS, "csv", BASE, 1)
    lines = out.strip().splitlines()
    assert lines[0] == "product_title,variant_title,price,available,add_url"
    assert lines[1] == "Cool Shirt,Small,20.00,True,https://shop.example/cart/add?id=111&quantity=1"


def test_render_rejects_unknown_format():
    import pytest

    with pytest.raises(ValueError):
        render(PRODUCTS, "xml", BASE, 1)
