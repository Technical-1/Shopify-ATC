"""Lock the public API re-exported from the top-level package."""

import shopify_atc


def test_all_names_are_importable():
    for name in shopify_atc.__all__:
        assert hasattr(shopify_atc, name), f"{name} missing from package"


def test_reexports_are_the_same_objects():
    from shopify_atc import client, formatters

    assert shopify_atc.fetch_products is client.fetch_products
    assert shopify_atc.filter_in_stock is client.filter_in_stock
    assert shopify_atc.normalize_url is client.normalize_url
    assert shopify_atc.render is formatters.render
    assert shopify_atc.Product is client.Product
    assert shopify_atc.Variant is client.Variant
    assert shopify_atc.ShopifyError is client.ShopifyError


def test_all_lists_expected_public_api():
    assert set(shopify_atc.__all__) == {
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
    }
