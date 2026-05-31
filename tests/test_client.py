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
