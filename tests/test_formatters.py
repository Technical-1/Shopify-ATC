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


def test_render_text_full_block():
    out = render(PRODUCTS, "text", BASE, 1)
    assert out == (
        "Cool Shirt\n"
        "https://shop.example/products/cool-shirt\n"
        "  Small — $20.00\n"
        "  https://shop.example/cart/add?id=111&quantity=1"
    )


def test_render_text_omits_price_suffix_when_none():
    products = [Product(title="P", handle="p", variants=[Variant(id=9, title="S", available=True, price=None)])]
    out = render(products, "text", BASE, 1)
    assert "  S\n" in out
    assert "—" not in out


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


def test_render_csv_blank_price_when_none():
    products = [Product(title="P", handle="p", variants=[Variant(id=9, title="S", available=False, price=None)])]
    out = render(products, "csv", BASE, 1)
    row = out.strip().splitlines()[1]
    assert row == "P,S,,False,https://shop.example/cart/add?id=9&quantity=1"


def test_render_csv_neutralizes_formula_injection():
    products = [
        Product(title="=HYPERLINK(1)", handle="h", variants=[Variant(id=9, title="@SUM(A1)", available=True, price="1")])
    ]
    out = render(products, "csv", BASE, 1)
    row = out.strip().splitlines()[1]
    # Dangerous leading chars (=, @) are prefixed with a quote so spreadsheets treat them as text.
    assert row.startswith("'=HYPERLINK(1),'@SUM(A1),")


def test_render_csv_tolerates_non_string_price():
    # A store may return a numeric JSON price; the CSV path must not crash on it.
    products = [Product(title="P", handle="p", variants=[Variant(id=9, title="S", available=True, price=20.0)])]
    out = render(products, "csv", BASE, 1)
    row = out.strip().splitlines()[1]
    assert row == "P,S,20.0,True,https://shop.example/cart/add?id=9&quantity=1"


def test_render_empty_product_list():
    assert render([], "text", BASE, 1) == ""
    assert render([], "json", BASE, 1) == "[]"
    assert render([], "csv", BASE, 1).strip() == "product_title,variant_title,price,available,add_url"


def test_render_rejects_unknown_format():
    import pytest

    with pytest.raises(ValueError):
        render(PRODUCTS, "xml", BASE, 1)
