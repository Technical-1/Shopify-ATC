import pytest
import requests

from shopify_atc.client import (
    HTTPError,
    NetworkError,
    NotShopifyError,
    Product,
    Variant,
    _parse_product,
    fetch_products,
    filter_in_stock,
    normalize_url,
)


def test_normalize_url_adds_https_scheme():
    assert normalize_url("shop.example") == "https://shop.example"


def test_normalize_url_strips_trailing_slash():
    assert normalize_url("https://shop.example/") == "https://shop.example"


def test_normalize_url_preserves_existing_scheme():
    assert normalize_url("http://shop.example") == "http://shop.example"


def test_normalize_url_treats_scheme_case_insensitively():
    assert normalize_url("HTTP://shop.example") == "HTTP://shop.example"


def test_parse_product_maps_fields():
    raw = {
        "title": "Cool Shirt",
        "handle": "cool-shirt",
        "variants": [
            {"id": 111, "title": "Small", "available": True, "price": "20.00"},
        ],
    }
    assert _parse_product(raw) == Product(
        title="Cool Shirt",
        handle="cool-shirt",
        variants=[Variant(id=111, title="Small", available=True, price="20.00")],
    )


def test_parse_product_uses_defaults_for_missing_optional_fields():
    raw = {"variants": [{"id": 5}]}
    assert _parse_product(raw) == Product(
        title="",
        handle="",
        variants=[Variant(id=5, title="", available=False, price=None)],
    )


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("no json body")
        return self._payload


SAMPLE = {
    "products": [
        {
            "title": "Cool Shirt",
            "handle": "cool-shirt",
            "variants": [
                {"id": 111, "title": "Small", "available": True, "price": "20.00"},
                {"id": 222, "title": "Large", "available": False, "price": "20.00"},
            ],
        }
    ]
}


def test_fetch_products_parses_sample(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(payload=SAMPLE))
    products = fetch_products("https://shop.example")
    assert products == [
        Product(
            title="Cool Shirt",
            handle="cool-shirt",
            variants=[
                Variant(id=111, title="Small", available=True, price="20.00"),
                Variant(id=222, title="Large", available=False, price="20.00"),
            ],
        )
    ]


def test_fetch_products_network_error(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("dns fail")

    monkeypatch.setattr(requests, "get", boom)
    with pytest.raises(NetworkError) as exc:
        fetch_products("https://shop.example")
    assert exc.value.exit_code == 2


def test_fetch_products_http_error(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(status_code=404))
    with pytest.raises(HTTPError) as exc:
        fetch_products("https://shop.example")
    assert exc.value.exit_code == 3


def test_fetch_products_not_shopify(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(payload={"foo": "bar"}))
    with pytest.raises(NotShopifyError) as exc:
        fetch_products("https://shop.example")
    assert exc.value.exit_code == 4


def test_fetch_products_null_products_is_not_shopify(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(payload={"products": None}))
    with pytest.raises(NotShopifyError) as exc:
        fetch_products("https://shop.example")
    assert exc.value.exit_code == 4


def test_fetch_products_variant_missing_id_is_not_shopify(monkeypatch):
    payload = {"products": [{"title": "X", "handle": "x", "variants": [{"title": "no id"}]}]}
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(payload=payload))
    with pytest.raises(NotShopifyError) as exc:
        fetch_products("https://shop.example")
    assert exc.value.exit_code == 4


def test_filter_in_stock_keeps_only_available_variants():
    products = [
        Product(
            title="P",
            handle="p",
            variants=[
                Variant(id=1, title="A", available=True, price="1.00"),
                Variant(id=2, title="B", available=False, price="1.00"),
            ],
        )
    ]
    assert filter_in_stock(products) == [
        Product(title="P", handle="p", variants=[Variant(id=1, title="A", available=True, price="1.00")])
    ]


def test_filter_in_stock_drops_products_with_no_available_variants():
    products = [
        Product(title="P", handle="p", variants=[Variant(id=2, title="B", available=False)])
    ]
    assert filter_in_stock(products) == []
