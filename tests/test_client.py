from shopify_atc.client import normalize_url, Product, Variant


def test_normalize_url_adds_https_scheme():
    assert normalize_url("shop.example") == "https://shop.example"


def test_normalize_url_strips_trailing_slash():
    assert normalize_url("https://shop.example/") == "https://shop.example"


def test_normalize_url_preserves_existing_scheme():
    assert normalize_url("http://shop.example") == "http://shop.example"


def test_dataclasses_support_equality():
    a = Product(title="P", handle="p", variants=[Variant(id=1, title="S", available=True, price="9.99")])
    b = Product(title="P", handle="p", variants=[Variant(id=1, title="S", available=True, price="9.99")])
    assert a == b


import pytest
import requests
from shopify_atc.client import (
    fetch_products,
    NetworkError,
    HTTPError,
    NotShopifyError,
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


from shopify_atc.client import filter_in_stock


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
